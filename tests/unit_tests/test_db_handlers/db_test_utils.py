import tests.utils as general_utils
from accountant.database.handlers import user_handler


async def create_user():

    user = general_utils.get_user()

    return await user_handler.create_user(user=user)
