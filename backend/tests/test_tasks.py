# backend/tests/test_tasks.py
import pytest
from fastapi import status
from app.schemas.task import TaskStatus, TaskProfile # For expected enum values
from app.models.user import User # To get user ID for assertions
from app.models.task import Task # To verify DB state directly if needed

# Test creating a task with all fields provided
def test_create_task_all_fields(auth_client, db_session, test_user_data):
    task_data = {
        "title": "Detailed Test Task",
        "description": "This is a task with all fields specified.",
        "task_profile": TaskProfile.DEVELOPMENT.value, # Use enum value
        "status": TaskStatus.IN_PROGRESS.value,     # Use enum value
        "assigned_user_ids": [] # Example: assign no one initially
    }
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_task = response.json()
    assert created_task["title"] == task_data["title"]
    assert created_task["description"] == task_data["description"]
    assert created_task["task_profile"] == task_data["task_profile"]
    assert created_task["status"] == task_data["status"]
    assert "id" in created_task
    assert "created_at" in created_task
    assert "updated_at" in created_task
    assert created_task["time_spent"] == 0 # Default value

    # Verify author_id (need to get current_user's ID)
    user = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    assert user is not None
    assert created_task["author_id"] == user.id

# Test creating a task with minimal fields (relying on defaults)
def test_create_task_minimal_fields(auth_client, db_session, test_user_data):
    task_data = {
        "title": "Minimal Test Task"
    }
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_task = response.json()
    assert created_task["title"] == task_data["title"]
    assert created_task["description"] is None # Default
    assert created_task["task_profile"] == TaskProfile.GENERAL.value # Default from model/schema
    assert created_task["status"] == TaskStatus.PLANNED.value       # Default from model/schema
    assert created_task["time_spent"] == 0
    assert created_task["assigned_users"] == [] # Default

    user = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    assert user is not None
    assert created_task["author_id"] == user.id

# Test creating a task with assigned users
def test_create_task_with_assigned_users(auth_client, db_session, test_user_data, test_user2_data, test_user2): # Ensure test_user2 fixture runs
    # Get IDs of test_user and test_user2
    user1 = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    # user2 fixture ensures testuser2 is created, we can fetch them by username from test_user2_data
    user2_model = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
    assert user1 is not None
    assert user2_model is not None, f"Test user 2 with username '{test_user2_data['username']}' not found in DB."


    task_data = {
        "title": "Task Assigned to Users",
        "assigned_user_ids": [user1.id, user2_model.id]
    }
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_201_CREATED
    created_task = response.json()
    assert created_task["title"] == task_data["title"]
    assigned_user_ids_in_response = sorted([user["id"] for user in created_task["assigned_users"]])
    assert assigned_user_ids_in_response == sorted([user1.id, user2_model.id])

# Test creating a task with invalid title (too short)
def test_create_task_invalid_title_short(auth_client):
    task_data = {"title": "T"} # min_length is 3
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Test creating a task with invalid enum value for status
def test_create_task_invalid_status_enum(auth_client):
    task_data = {
        "title": "Invalid Status Task",
        "status": "NON_EXISTENT_STATUS"
    }
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Test creating a task with invalid enum value for task_profile
def test_create_task_invalid_profile_enum(auth_client):
    task_data = {
        "title": "Invalid Profile Task",
        "task_profile": "NON_EXISTENT_PROFILE"
    }
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Test creating a task without authentication
def test_create_task_unauthenticated(client): # Using non-authed client
    task_data = {"title": "Unauthenticated Task"}
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize(
    "title, description, task_profile, task_status, expected_status_code",
    [
        ("Valid Task Full", "Desc", "DEVELOPMENT", "IN_PROGRESS", status.HTTP_201_CREATED),
        ("Valid Task Min", None, "GENERAL", "PLANNED", status.HTTP_201_CREATED),
        # Pydantic by default considers "" as a valid string if min_length=0 or not set.
        # Our title has min_length=3, so "" is invalid.
        ("", "Desc", "ANALYTICS", "COMPLETED", status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("OK", "Desc", "ANALYTICS", "COMPLETED", status.HTTP_422_UNPROCESSABLE_ENTITY),  # Title too short (min_length=3)
        ("Valid Title Param", "Desc", "INVALID_PROFILE_PARAM", "PLANNED", status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("Valid Title Param", "Desc", "DOCUMENTATION", "INVALID_STATUS_PARAM", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ]
)
def test_create_task_parametrized(auth_client, title, description, task_profile, task_status, expected_status_code):
    task_data = {"title": title}
    if description is not None: # Only add if not None, as Pydantic treats None as "field not provided" for optional fields
        task_data["description"] = description

    # For task_profile and status, we pass the string directly.
    # If it's a valid enum string (e.g., "DEVELOPMENT"), Pydantic will convert it.
    # If it's an invalid string (e.g., "INVALID_PROFILE_PARAM"), Pydantic will raise a validation error.
    task_data["task_profile"] = task_profile
    task_data["status"] = task_status

    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_201_CREATED:
        created_task = response.json()
        assert created_task["title"] == title
        if description is not None: # Check only if description was intended to be set
            assert created_task["description"] == description
        else: # If description was None in params, it should be None in response (default)
            assert created_task["description"] is None

        # Check task_profile and status against the input if they were valid enum strings
        # Pydantic converts valid strings to enum values, which are then serialized back to strings for JSON.
        if task_profile in [p.value for p in TaskProfile]:
             assert created_task["task_profile"] == task_profile
        else: # If input was default (None) or invalid, check against expected default or error
            if task_profile is None : # Assuming None means use default
                 assert created_task["task_profile"] == TaskProfile.GENERAL.value
            # If it was an invalid string, the status code check handles it.

        if task_status in [s.value for s in TaskStatus]:
            assert created_task["status"] == task_status
        else: # If input was default (None) or invalid
            if task_status is None : # Assuming None means use default
                assert created_task["status"] == TaskStatus.PLANNED.value
            # If it was an invalid string, the status code check handles it.
    elif expected_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        # Optionally, inspect the error details further if needed
        error_details = response.json().get("detail")
        assert error_details is not None
        # Example: if title was "OK", check that error message mentions title
        # if title == "OK":
        #     assert any("title" in e.get("loc", []) for e in error_details)
        # This level of detail might be too much for every parametrized case.
        pass

# --- Tests for GET /tasks/{task_id} ---

@pytest.mark.parametrize(
    "user_client_fixture_name, setup_assignee, expected_status_code",
    [
        ("auth_client", False, status.HTTP_200_OK), # Author
        ("auth_client_user2", True, status.HTTP_200_OK), # Assigned user
        ("auth_client_user2", False, status.HTTP_403_FORBIDDEN), # Other authenticated user (not assigned)
        ("client", False, status.HTTP_401_UNAUTHORIZED) # Unauthenticated
    ]
)
def test_get_task_permissions(
    request, user_client_fixture_name, setup_assignee, expected_status_code,
    test_task, auth_client, db_session, test_user2_data, test_user2 # Include test_user2 to ensure user2 exists
):
    task_id = test_task["id"] # test_task created by auth_client (test_user)

    # Dynamically get the client fixture based on the name passed by parametrize
    current_client = request.getfixturevalue(user_client_fixture_name)

    if setup_assignee:
        # This case is for "auth_client_user2" who needs to be assigned to the task for the test.
        # The task is created by "auth_client" (test_user).
        # We use "auth_client" (the author) to assign "test_user2" to the task.
        user2_for_assignment = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
        assert user2_for_assignment is not None, f"User {test_user2_data['username']} for assignment not found."

        assign_response = auth_client.post(f"/tasks/{task_id}/assign/{user2_for_assignment.id}")
        assert assign_response.status_code == status.HTTP_200_OK, \
            f"Failed to assign user {user2_for_assignment.id} to task {task_id}: {assign_response.text}"

    response = current_client.get(f"/tasks/{task_id}")
    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        retrieved_task = response.json()
        assert retrieved_task["id"] == task_id
        # For the author case, we can also check the title if test_task is directly available
        if user_client_fixture_name == "auth_client":
             assert retrieved_task["title"] == test_task["title"]


def test_get_non_existent_task(auth_client):
    response = auth_client.get("/tasks/99999") # Assuming 99999 does not exist
    assert response.status_code == status.HTTP_404_NOT_FOUND

# --- Tests for GET /tasks/ (List Tasks) ---

def test_list_tasks_unauthenticated(client):
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_list_tasks_no_filters(auth_client, test_task): # test_task ensures at least one task exists
    response = auth_client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert isinstance(tasks, list)
    # This user might have other tasks from previous failed/uncleaned tests if db is not fully reset.
    # The test_task fixture (function scope) cleans tasks for "testuser" before creating one.
    # So, for "testuser", there should be at least this one.
    assert len(tasks) >= 1
    assert any(t["id"] == test_task["id"] for t in tasks)


def test_list_tasks_filter_by_status(auth_client, db_session, test_user_data):
    user = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    assert user is not None
    # Clean up tasks for this user before creating new ones for this specific test
    db_session.query(Task).filter(Task.author_id == user.id).delete()
    db_session.commit()

    task1_data = {"title": "Status Planned Task", "status": TaskStatus.PLANNED.value}
    task2_data = {"title": "Status In Progress Task", "status": TaskStatus.IN_PROGRESS.value}
    auth_client.post("/tasks/", json=task1_data)
    auth_client.post("/tasks/", json=task2_data)

    response = auth_client.get(f"/tasks/?status={TaskStatus.PLANNED.value}")
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert len(tasks) == 1 # Should be exactly one after cleanup
    assert tasks[0]["status"] == TaskStatus.PLANNED.value
    assert tasks[0]["title"] == task1_data["title"]

    response_inprogress = auth_client.get(f"/tasks/?status={TaskStatus.IN_PROGRESS.value}")
    assert response_inprogress.status_code == status.HTTP_200_OK
    tasks_inprogress = response_inprogress.json()
    assert len(tasks_inprogress) == 1 # Should be exactly one
    assert tasks_inprogress[0]["status"] == TaskStatus.IN_PROGRESS.value
    assert tasks_inprogress[0]["title"] == task2_data["title"]


def test_list_tasks_filter_by_task_profile(auth_client, db_session, test_user_data):
    user = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    assert user is not None
    db_session.query(Task).filter(Task.author_id == user.id).delete()
    db_session.commit()

    task1_data = {"title": "Profile Dev Task", "task_profile": TaskProfile.DEVELOPMENT.value}
    task2_data = {"title": "Profile Docs Task", "task_profile": TaskProfile.DOCUMENTATION.value}
    auth_client.post("/tasks/", json=task1_data)
    auth_client.post("/tasks/", json=task2_data)

    response = auth_client.get(f"/tasks/?task_profile={TaskProfile.DEVELOPMENT.value}")
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["task_profile"] == TaskProfile.DEVELOPMENT.value
    assert tasks[0]["title"] == task1_data["title"]

def test_list_tasks_filter_by_author_id(auth_client, auth_client_user2, test_task, db_session, test_user_data, test_user2_data, test_user2):
    # test_task is created by test_user (auth_client)
    user1 = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    assert user1 is not None

    # Create a task for test_user2. test_user2 fixture ensures the user exists.
    task_user2_data = {"title": "User2 Task for Author Filter"}
    response_user2_task = auth_client_user2.post("/tasks/", json=task_user2_data)
    assert response_user2_task.status_code == status.HTTP_201_CREATED

    # List tasks by author_id of test_user (user1)
    # Note: test_task fixture already cleans user1's tasks and creates one.
    # So, we expect at least that one.
    response = auth_client.get(f"/tasks/?author_id={user1.id}")
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert len(tasks) >= 1
    for task in tasks:
        assert task["author_id"] == user1.id
    assert any(t["id"] == test_task["id"] for t in tasks)

def test_list_tasks_filter_by_assigned_user_id(auth_client, auth_client_user2, db_session, test_user_data, test_user2_data, test_user, test_user2):
    user1 = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    user2 = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
    assert user1 is not None
    assert user2 is not None

    # Clean up tasks by user1 to ensure a predictable state for this test
    db_session.query(Task).filter(Task.author_id == user1.id).delete()
    db_session.commit()

    # Task 1 created by user1, assigned to user2
    task1_data = {"title": "Task for User2 Assignment", "assigned_user_ids": [user2.id]}
    task1_resp = auth_client.post("/tasks/", json=task1_data)
    assert task1_resp.status_code == status.HTTP_201_CREATED
    task1_id = task1_resp.json()["id"]

    # Task 2 created by user1, assigned to user1
    task2_data = {"title": "Task for User1 Assignment", "assigned_user_ids": [user1.id]}
    task2_resp = auth_client.post("/tasks/", json=task2_data)
    assert task2_resp.status_code == status.HTTP_201_CREATED
    # task2_id = task2_resp.json()["id"] # Not used in assertions below for user2

    # List tasks assigned to user2
    response = auth_client.get(f"/tasks/?assigned_user_id={user2.id}")
    assert response.status_code == status.HTTP_200_OK
    tasks_for_user2 = response.json()
    assert len(tasks_for_user2) == 1 # Expecting only task1
    assert tasks_for_user2[0]["id"] == task1_id
    # assert any(t["id"] == task1_id for t in tasks_for_user2)
    for task_item in tasks_for_user2: # Renamed task to task_item to avoid conflict with Task model
        assert any(assigned_user["id"] == user2.id for assigned_user in task_item["assigned_users"])

# Test pagination: skip and limit
def test_list_tasks_pagination(auth_client, db_session, test_user_data):
    user = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    assert user is not None
    # Clean up tasks for this user to ensure a predictable state
    db_session.query(Task).filter(Task.author_id == user.id).delete()
    db_session.commit()

    # Create a few tasks to test pagination
    task_ids = []
    for i in range(5):
        resp = auth_client.post("/tasks/", json={"title": f"Pagination Task {i+1}"})
        assert resp.status_code == status.HTTP_201_CREATED
        task_ids.append(resp.json()["id"])

    # Test limit
    response_limit = auth_client.get("/tasks/?limit=2")
    assert response_limit.status_code == status.HTTP_200_OK
    assert len(response_limit.json()) == 2

    # Test skip
    response_skip = auth_client.get("/tasks/?skip=1&limit=2")
    assert response_skip.status_code == status.HTTP_200_OK
    skipped_tasks = response_skip.json()
    assert len(skipped_tasks) == 2

    # Ensure skipped tasks are different from the first tasks without skip
    assert response_limit.json()[0]["id"] == task_ids[0]
    assert response_limit.json()[1]["id"] == task_ids[1]
    assert skipped_tasks[0]["id"] == task_ids[1] # Task at index 1 (second task)
    assert skipped_tasks[1]["id"] == task_ids[2] # Task at index 2 (third task)

    # Test skip that results in fewer tasks than limit
    response_skip_more = auth_client.get("/tasks/?skip=4&limit=2")
    assert response_skip_more.status_code == status.HTTP_200_OK
    assert len(response_skip_more.json()) == 1 # Only one task left (task_ids[4])
    assert response_skip_more.json()[0]["id"] == task_ids[4]

    # Test skip that results in zero tasks
    response_skip_all = auth_client.get("/tasks/?skip=5&limit=2")
    assert response_skip_all.status_code == status.HTTP_200_OK
    assert len(response_skip_all.json()) == 0

# --- Tests for PUT /tasks/{task_id} (Update Task) ---

def test_update_task_by_author(auth_client, test_task):
    task_id = test_task["id"]
    update_data = {
        "title": "Updated Title by Author",
        "description": "Updated description.",
        "task_profile": TaskProfile.ANALYTICS.value,
        "status": TaskStatus.IN_PROGRESS.value
    }
    response = auth_client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    updated_task = response.json()
    assert updated_task["title"] == update_data["title"]
    assert updated_task["description"] == update_data["description"]
    assert updated_task["task_profile"] == update_data["task_profile"]
    assert updated_task["status"] == update_data["status"]
    assert updated_task["id"] == task_id

def test_update_task_partial(auth_client, test_task):
    task_id = test_task["id"]
    update_data = {"title": "Partially Updated Title"}
    response = auth_client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    updated_task = response.json()
    assert updated_task["title"] == update_data["title"]
    assert updated_task["description"] == test_task["description"] # Should remain unchanged

def test_update_task_by_non_author(auth_client_user2, test_task):
    task_id = test_task["id"] # test_task created by test_user (auth_client)
    update_data = {"title": "Attempted Update by Non-Author"}
    response = auth_client_user2.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_task_assign_users(auth_client, test_task, test_user2_data, db_session, test_user2): # Ensure test_user2 created
    task_id = test_task["id"]
    user2 = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
    assert user2 is not None

    update_data = {
        "title": "Update with Assignment", # Title must be present due to schema validation (min_length=3)
                                        # even if only changing assignments.
                                        # Or use a more specific schema for this if allowed by PUT.
                                        # For now, assume full update schema is used.
        "assigned_user_ids": [user2.id]
    }
    # If title is not part of the TaskUpdate schema as required field, this needs adjustment.
    # Current TaskUpdate makes title Optional[str] = Field(None, min_length=3, max_length=100)
    # So we don't strictly need to send title if we only want to update assigned_user_ids
    # Let's test that specific case:
    update_assignment_only = { "assigned_user_ids": [user2.id] }

    response = auth_client.put(f"/tasks/{task_id}", json=update_assignment_only)
    assert response.status_code == status.HTTP_200_OK
    updated_task = response.json()
    assert len(updated_task["assigned_users"]) == 1
    assert updated_task["assigned_users"][0]["id"] == user2.id
    assert updated_task["title"] == test_task["title"] # Title should remain unchanged

def test_update_task_clear_assignments(auth_client, test_task, test_user2_data, db_session, test_user2): # Ensure test_user2 created
    task_id = test_task["id"]
    user2 = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
    assert user2 is not None
    # First assign a user
    auth_client.put(f"/tasks/{task_id}", json={"assigned_user_ids": [user2.id]})

    update_data = {"assigned_user_ids": []} # Clear assignments
    response = auth_client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    updated_task = response.json()
    assert len(updated_task["assigned_users"]) == 0


# --- Tests for DELETE /tasks/{task_id} ---

def test_delete_task_by_author(auth_client, test_task):
    task_id = test_task["id"]
    response = auth_client.delete(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify task is deleted
    get_response = auth_client.get(f"/tasks/{task_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_task_by_non_author(auth_client_user2, test_task):
    task_id = test_task["id"]
    response = auth_client_user2.delete(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_non_existent_task(auth_client):
    response = auth_client.delete("/tasks/99999") # Assuming 99999 does not exist
    assert response.status_code == status.HTTP_404_NOT_FOUND # API returns 404, not 400


# --- Tests for Assign/Unassign Endpoints ---

@pytest.mark.parametrize(
    "actor_client_fixture_name, target_user_fixture_name, action, expected_status_code",
    [
        # Assign action
        ("auth_client", "test_user2", "assign", status.HTTP_200_OK), # Author assigns user2
        ("auth_client_user2", "test_user", "assign", status.HTTP_403_FORBIDDEN), # User2 (non-author) tries to assign user1
        ("client", "test_user2", "assign", status.HTTP_401_UNAUTHORIZED), # Unauthenticated tries to assign
        # Unassign action (after assignment)
        ("auth_client", "test_user2", "unassign", status.HTTP_200_OK), # Author unassigns user2
        ("auth_client_user2", "test_user", "unassign", status.HTTP_403_FORBIDDEN), # User2 (non-author) tries to unassign user1
    ]
)
def test_assign_unassign_permissions(
    request, actor_client_fixture_name, target_user_fixture_name, action, expected_status_code,
    test_task, db_session, test_user_data, test_user2_data, test_user, test_user2 # Ensure all users exist
):
    task_id = test_task["id"] # Task created by test_user (auth_client)

    actor_client = request.getfixturevalue(actor_client_fixture_name)

    # Determine the ID of the user to be (un)assigned
    target_user_model = None
    if target_user_fixture_name == "test_user":
        target_user_model = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    elif target_user_fixture_name == "test_user2":
        target_user_model = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
    assert target_user_model is not None, f"Target user for (un)assignment ('{target_user_fixture_name}') not found."
    target_user_id = target_user_model.id

    url = f"/tasks/{task_id}/{action}/{target_user_id}"

    # If testing "unassign", we need to ensure the user is assigned first.
    # This setup should be done by the author of the task (auth_client).
    if action == "unassign":
        # Only attempt pre-assignment if the actor is also the author, to avoid 403 here.
        # Or, more simply, ensure the pre-assignment is always done by auth_client (author).
        author_client = request.getfixturevalue("auth_client") # Get author client specifically for setup
        assign_response = author_client.post(f"/tasks/{task_id}/assign/{target_user_id}")
        # If target user is already assigned by test_task or another test, this might return the task as is.
        # We only care that it's 200 OK or that the user is assigned.
        if assign_response.status_code != status.HTTP_200_OK:
             # Check if already assigned, e.g. if target_user_id is author_id who is implicitly assigned sometimes or if test_task assigned them
            current_task_state = author_client.get(f"/tasks/{task_id}").json()
            if not any(u["id"] == target_user_id for u in current_task_state["assigned_users"]):
                 pytest.fail(f"Pre-assignment for unassign test failed: {assign_response.text}")


    if action == "assign":
        response = actor_client.post(url)
    elif action == "unassign":
        response = actor_client.delete(url)
    else:
        pytest.fail(f"Invalid action '{action}' for assign/unassign test.")

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        task_after_action = response.json()
        is_assigned = any(u["id"] == target_user_id for u in task_after_action["assigned_users"])
        if action == "assign":
            assert is_assigned is True, f"User {target_user_id} was not found in assigned_users after assign."
        elif action == "unassign":
            assert is_assigned is False, f"User {target_user_id} was still found in assigned_users after unassign."

# --- Tests for Log Time Endpoint ---

@pytest.mark.parametrize(
    "user_client_fixture_name, setup_assignee, time_to_add, expected_status_code",
    [
        ("auth_client", False, 60, status.HTTP_200_OK),  # Author
        ("auth_client_user2", True, 30, status.HTTP_200_OK),  # Assigned user
        ("auth_client_user2", False, 10, status.HTTP_403_FORBIDDEN), # Other authenticated user
        ("client", False, 10, status.HTTP_401_UNAUTHORIZED), # Unauthenticated
    ]
)
def test_log_time_permissions(
    request, user_client_fixture_name, setup_assignee, time_to_add, expected_status_code,
    test_task, auth_client, db_session, test_user2_data, test_user2 # Ensure test_user2 for assignment
):
    task_id = test_task["id"]
    current_client = request.getfixturevalue(user_client_fixture_name)

    # Fetch initial time_spent using auth_client (author) to ensure read access
    # and to get a consistent value before any modifications in this test run.
    # The test_task fixture provides the initial state of the task.
    initial_time_spent = test_task["time_spent"]

    if setup_assignee: # This means current_client is auth_client_user2 and needs to be assigned
        user2_for_assignment = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
        assert user2_for_assignment is not None
        assign_response = auth_client.post(f"/tasks/{task_id}/assign/{user2_for_assignment.id}")
        assert assign_response.status_code == status.HTTP_200_OK
        # Re-fetch task state after assignment if time_spent could change, though assign doesn't change time_spent
        # For this specific test, initial_time_spent from test_task is fine.

    response = current_client.post(f"/tasks/{task_id}/log_time", json={"time_added": time_to_add})
    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        updated_task = response.json()
        assert updated_task["time_spent"] == initial_time_spent + time_to_add

def test_log_time_invalid_input(auth_client, test_task):
    task_id = test_task["id"]

    invalid_payloads = [
        {"time_added": -10}, # negative time
        {"time_added": 0},   # zero time (gt=0 in schema)
        {"time_added": "abc"} # wrong type
    ]
    for payload in invalid_payloads:
        response = auth_client.post(f"/tasks/{task_id}/log_time", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# --- Tests for Update Status Endpoint ---

@pytest.mark.parametrize(
    "user_client_fixture_name, setup_assignee, new_status, expected_status_code",
    [
        ("auth_client", False, TaskStatus.COMPLETED.value, status.HTTP_200_OK), # Author
        ("auth_client_user2", True, TaskStatus.IN_PROGRESS.value, status.HTTP_200_OK), # Assigned user
        ("auth_client_user2", False, TaskStatus.PLANNED.value, status.HTTP_403_FORBIDDEN), # Other authenticated user
        ("client", False, TaskStatus.PLANNED.value, status.HTTP_401_UNAUTHORIZED) # Unauthenticated
    ]
)
def test_update_status_permissions(
    request, user_client_fixture_name, setup_assignee, new_status, expected_status_code,
    test_task, auth_client, db_session, test_user2_data, test_user2
):
    task_id = test_task["id"]
    current_client = request.getfixturevalue(user_client_fixture_name)

    if setup_assignee: # current_client is auth_client_user2, assign them
        user2_for_assignment = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
        assert user2_for_assignment is not None
        assign_response = auth_client.post(f"/tasks/{task_id}/assign/{user2_for_assignment.id}")
        assert assign_response.status_code == status.HTTP_200_OK

    response = current_client.put(f"/tasks/{task_id}/status", json={"status": new_status})
    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        updated_task = response.json()
        assert updated_task["status"] == new_status

def test_update_status_invalid_enum(auth_client, test_task):
    task_id = test_task["id"]
    response = auth_client.put(f"/tasks/{task_id}/status", json={"status": "INVALID_STATUS_VALUE"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
