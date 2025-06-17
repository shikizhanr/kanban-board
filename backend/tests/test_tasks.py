import pytest
from httpx import AsyncClient
from fastapi import status

pytestmark = pytest.mark.asyncio

async def get_auth_token(async_client: AsyncClient, email: str, password: str) -> str:
    response = await async_client.post(
        "/api/auth/token",
        data={"username": email, "password": password}
    )
    assert response.status_code == status.HTTP_200_OK, "Failed to get auth token"
    return response.json()["access_token"]

class TestTaskRoutesWithAuth:
    @pytest.fixture(scope="function", autouse=True)
    async def setup_users_and_token(self, async_client: AsyncClient):
        creator_email = "task_creator@example.com"
        creator_password = "password123"

        user_response = await async_client.post(
            "/api/users/",
            json={"email": creator_email, "first_name": "Создатель", "last_name": "Задач", "password": creator_password}
        )
        assert user_response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

        self.token = await get_auth_token(async_client, creator_email, creator_password)
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    async def test_create_task_unauthenticated(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/tasks/",
            json={"title": "Попытка без токена", "type": "testing"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_task_success(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/tasks/",
            headers=self.auth_headers,
            json={
                "title": "Очень важная задача",
                "description": "Сделать что-то очень важное",
                "type": "development",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Очень важная задача"
        assert data["creator"]["email"] == "task_creator@example.com"

    async def test_get_tasks_authenticated(self, async_client: AsyncClient):
        response = await async_client.get("/api/tasks/", headers=self.auth_headers)
        assert response.status_code == status.HTTP_200_OK

    async def test_get_and_delete_task(self, async_client: AsyncClient):
        create_response = await async_client.post(
            "/api/tasks/",
            headers=self.auth_headers,
            json={"title": "Задача на удаление", "type": "documentation"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        task_id = create_response.json()["id"]

        get_response = await async_client.get(f"/api/tasks/{task_id}", headers=self.auth_headers)
        assert get_response.status_code == status.HTTP_200_OK

        # ИСПРАВЛЕНО: Проверяем, что эндпоинт возвращает 204 No Content
        delete_response = await async_client.delete(f"/api/tasks/{task_id}", headers=self.auth_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_after_delete_response = await async_client.get(f"/api/tasks/{task_id}", headers=self.auth_headers)
        assert get_after_delete_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_assigned_user_can_change_status(self, async_client: AsyncClient):
        # Create user1 (creator - already created in setup_users_and_token)
        creator_email = "task_creator@example.com"
        creator_token = self.token
        creator_headers = self.auth_headers

        # Create user2 (assignee)
        assignee_email = "assignee@example.com"
        assignee_password = "password123"
        user_response = await async_client.post(
            "/api/users/",
            json={"email": assignee_email, "first_name": "Assignee", "last_name": "User", "password": assignee_password}
        )
        # Allow for user already existing if tests are run multiple times
        assert user_response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        assignee_id = user_response.json()["id"] if user_response.status_code == status.HTTP_201_CREATED else \
                      (await async_client.get("/api/users/", headers=creator_headers)).json()[1]["id"] # hacky way to get id if user exists

        assignee_token = await get_auth_token(async_client, assignee_email, assignee_password)
        assignee_headers = {"Authorization": f"Bearer {assignee_token}"}

        # User1 creates a task and assigns it to User2
        task_creation_response = await async_client.post(
            "/api/tasks/",
            headers=creator_headers,
            json={
                "title": "Task to be status-updated by assignee",
                "description": "Description",
                "type": "testing",
                "status": "pending",
                "priority": "medium",
                "assignee_ids": [assignee_id]
            }
        )
        assert task_creation_response.status_code == status.HTTP_201_CREATED
        task_id = task_creation_response.json()["id"]

        # User2 (assignee) changes the task status
        new_status = "in_progress"
        update_response = await async_client.put(
            f"/api/tasks/{task_id}",
            headers=assignee_headers,
            json={"status": new_status}
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_task_data = update_response.json()
        assert updated_task_data["status"] == new_status

    async def test_non_assigned_user_cannot_change_status(self, async_client: AsyncClient):
        # User1 (creator - from setup)
        creator_headers = self.auth_headers

        # Create User2 (non-assignee)
        non_assignee_email = "nonassignee@example.com"
        non_assignee_password = "password123"
        user_response = await async_client.post(
            "/api/users/",
            json={"email": non_assignee_email, "first_name": "NonAssignee", "last_name": "User", "password": non_assignee_password}
        )
        assert user_response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        
        non_assignee_token = await get_auth_token(async_client, non_assignee_email, non_assignee_password)
        non_assignee_headers = {"Authorization": f"Bearer {non_assignee_token}"}

        # User1 creates a task (not assigned to User2)
        task_creation_response = await async_client.post(
            "/api/tasks/",
            headers=creator_headers,
            json={
                "title": "Task for non-assignee status change attempt",
                "description": "Description",
                "type": "testing", # type is required by TaskBase
                # "status": "pending", <--- Removed, status is not in TaskCreate, defaults to "todo"
                "priority": "low"
                # No assignee_ids or assign to someone else if needed
            }
        )
        assert task_creation_response.status_code == status.HTTP_201_CREATED
        task_id = task_creation_response.json()["id"]

        # User2 (non-assignee) tries to change the task status
        update_response = await async_client.put(
            f"/api/tasks/{task_id}",
            headers=non_assignee_headers,
            json={"status": "in_progress"} # Changed to a valid TaskStatus enum value
        )
        assert update_response.status_code == status.HTTP_403_FORBIDDEN
        assert update_response.json()["detail"] == "Вы не назначены на выполнение этой задачи"

    async def test_non_assigned_user_can_change_other_fields(self, async_client: AsyncClient):
        # User1 (creator - from setup)
        creator_headers = self.auth_headers

        # Create User2 (non-assignee)
        other_user_email = "otheruser@example.com"
        other_user_password = "password123"
        user_response = await async_client.post(
            "/api/users/",
            json={"email": other_user_email, "first_name": "Other", "last_name": "User", "password": other_user_password}
        )
        assert user_response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

        other_user_token = await get_auth_token(async_client, other_user_email, other_user_password)
        other_user_headers = {"Authorization": f"Bearer {other_user_token}"}

        # User1 creates a task
        task_creation_response = await async_client.post(
            "/api/tasks/",
            headers=creator_headers,
            json={
                "title": "Original Title",
                "description": "Original Description",
                "type": "testing", # Changed to a valid TaskType, "general" is not in enum
                # "status": "pending", <--- Removed, status is not in TaskCreate, defaults to "todo"
                "priority": "high"
            }
        )
        assert task_creation_response.status_code == status.HTTP_201_CREATED
        task_id = task_creation_response.json()["id"]
        original_status = task_creation_response.json()["status"]

        # User2 (non-assignee) changes the task's title (NOT status)
        new_title = "Updated Title by Non-Assignee"
        update_response = await async_client.put(
            f"/api/tasks/{task_id}",
            headers=other_user_headers,
            json={"title": new_title}
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_task_data = update_response.json()
        assert updated_task_data["title"] == new_title
        assert updated_task_data["status"] == original_status # Status should remain unchanged