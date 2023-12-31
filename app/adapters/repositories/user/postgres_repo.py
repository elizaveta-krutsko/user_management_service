import uuid
from typing import Union

from fastapi_pagination import paginate
from sqlalchemy import delete, exc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm_engines.models import UserORM
from app.common import utils
from app.common.config import logger
from app.common.exceptions.fast_api_sql_alchemy_exceptions import ORMError
from app.domain.user import User
from app.ports.user_port import UserRepositoryPort
from app.rest.routes.filters import UsersFilter


class SQLAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def __convert_to_domain(self, user_from_db) -> User:
        user_as_domain = User(
            role=user_from_db.role,
            name=user_from_db.name,
            surname=user_from_db.surname,
            username=user_from_db.username,
            phone_number=user_from_db.phone_number,
            email=user_from_db.email,
            image_path=user_from_db.image_path,
            group_id=user_from_db.group_id,
            is_blocked=user_from_db.is_blocked,
            id=user_from_db.id,
            password=user_from_db.hashed_password,
            created_at=user_from_db.created_at,
            modified_at=user_from_db.modified_at,
        )
        return user_as_domain

    async def create_user(self, new_user_data: User):
        try:
            hashed_password = utils.get_hashed_password(new_user_data.password)
            del new_user_data.password
            new_user_data.hashed_password = hashed_password

            db_new_user = await self.__create_orm_user(new_user_data)

            logger.info(f"Created new entity: {db_new_user}.")

            return db_new_user

        except exc.IntegrityError as e:
            await self.db.rollback()
            raise ORMError(e).bad_request_error()

    async def __create_orm_user(self, new_user_data):
        db_new_user = UserORM()

        self.db.add(db_new_user)

        db_new_user.name = new_user_data.name
        db_new_user.surname = new_user_data.surname
        db_new_user.username = new_user_data.username
        db_new_user.hashed_password = new_user_data.hashed_password
        db_new_user.phone_number = new_user_data.phone_number
        db_new_user.email = new_user_data.email
        db_new_user.role = new_user_data.role
        db_new_user.image_path = new_user_data.image_path
        db_new_user.is_blocked = new_user_data.is_blocked
        db_new_user.group_id = new_user_data.group_id

        await self.db.commit()
        await self.db.refresh(db_new_user)

        return db_new_user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Union[User | None]:
        db_user = select(UserORM).where(UserORM.id == user_id)
        res = await self.db.execute(db_user)
        res_db = res.scalars().first()
        if res_db is not None:
            return self.__convert_to_domain(res_db)
        else:
            return None

    async def get_user_by_login(self, username, email=None, phone_number=None):
        if email is None:
            email = username
        if phone_number is None:
            phone_number = username
        stmt = select(UserORM).where(
            or_(
                UserORM.username == username,
                UserORM.email == email,
                UserORM.phone_number == phone_number,
            )
        )
        res = await self.db.execute(stmt)

        return res.scalars().first()

    async def update_user_by_id(self, new_user_data: User, user_id: uuid.UUID) -> User:
        logger.debug(new_user_data)
        logger.debug(user_id)
        try:
            updated_user_data = (
                update(UserORM)
                .where(UserORM.id == user_id)
                .values(new_user_data.dict())
                .returning(UserORM)
            )
            result = await self.db.execute(updated_user_data)
            await self.db.commit()
            return self.__convert_to_domain(result.scalars().first())

        except exc.IntegrityError as e:
            await self.db.rollback()
            raise ORMError(e).bad_request_error()

    async def delete_user(self, user_id: uuid.UUID):
        try:
            user_request = delete(UserORM).where(UserORM.id == user_id)
            await self.db.execute(user_request)
            await self.db.commit()
            return user_id

        except exc.IntegrityError as e:
            await self.db.rollback()
            raise ORMError(e).bad_request_error()

    async def get_users_by_filters(self, users_filter: UsersFilter, group_id=None):
        try:
            query = users_filter.filter(select(UserORM))
            query = users_filter.sort(query)
            if group_id is None:
                result = await self.db.execute(query)
            else:
                new_query = query.filter(UserORM.group_id == group_id)
                result = await self.db.execute(new_query)
            return paginate(result.scalars().all())
        except exc.IntegrityError as e:
            raise ORMError(e).bad_request_error()
