from accountant.root.database import async_session
from accountant.database.orms.user_orm import User as UserDB
from accountant.database.orms.user_orm import UserGroup as UserGroupDB
from accountant.database.orms.user_orm import UserGroupInvitation as UserGroupIVDB
import logging
from sqlalchemy import select, insert, update, delete
import accountant.schemas.user_schemas as schemas
from accountant.services.service_utils.accountant_exceptions import CreateError

LOGGER = logging.getLogger(__name__)


async def create_user(user: schemas.User):
    async with async_session() as session:

        stmt = insert(UserDB).values(**user.model_dump()).returning(UserDB)


        result = (await session.execute(statement=stmt)).scalar_one_or_none()



        if result is None:
            await session.rollback()
            raise CreateError
            
    
    return schemas.UserExtendedProfile(**result.as_dict())
    
    
    ...

async def check_user():
    ...


async def get_user():
    ...



async def update_user():



    ...


async def delete_user():

    ...



# UserGroup

async def create_user_group():
    ...


async def get_user_group():
    ...


async def add_user_to_group():
    ...

async def delete_from_user_group():

    ...


async def get_users_in_user_group():
    ...


#User Invitation

async def create_dependent():
    ...


async def get_all_dependents():
    ...




async def get_dependent():
    ...



async def delete_dependent():

    ...
