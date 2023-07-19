from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.user import User


class UserRepositoryPort(ABC):
    @abstractmethod
    # TODO: add input parameters, annotation
    async def create_user(self, new_user_data: User) -> User:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> User:
        pass

    @abstractmethod
    async def get_user_by_login(self, username, email=None, phone_number=None):
        pass

    @abstractmethod
    def update_user_by_id(self, new_user_data: User, user_id: UUID):
        pass

    @abstractmethod
    def delete_user(self, user_id: UUID):
        pass