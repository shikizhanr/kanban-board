from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str):
    """Получает пользователя по его email."""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate):
    """Создает нового пользователя."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, user_id: int):
    """Получает пользователя по его ID."""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def get_users(db: AsyncSession):
    """Получает список всех пользователей."""
    result = await db.execute(select(User))
    return result.scalars().all()

async def update_avatar(db: AsyncSession, user: User, avatar_path: str) -> User:
    """Обновляет путь к аватару для пользователя."""
    user.avatar_url = avatar_path
    await db.commit()
    await db.refresh(user)
    return user
