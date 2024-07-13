from uuid import UUID

from fastapi import HTTPException, status

import accountant.database.handlers.investment_handler as investment_handler
import accountant.schemas.investment_schemas as schemas
import accountant.services.auth_service as user_service
import accountant.services.service_utils.auth_utils as auth_utils
import accountant.services.service_utils.investment_utils as investment_utils
from accountant.services.service_utils.accountant_exceptions import NotFoundError


async def check_platform(platform_name: str, user_group_uid: UUID):

    try:
        return await investment_handler.check_platform(
            name=platform_name, user_group_uid=user_group_uid
        )

    except NotFoundError as e:
        raise e


async def create_platform(user_group_uid: UUID, platform: schemas.Platform):

    platform.name = platform.name.lower()

    try:
        await check_platform(platform_name=platform.name, user_group_uid=user_group_uid)
        raise HTTPException(
            detail="user has added this platform",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except NotFoundError:

        # Encoding the platform access credentials.

        platform = investment_utils.platform_encoder(
            platform=platform, user_group_uid=user_group_uid
        )

        return await investment_handler.create_platform_record(
            user_group_uid=user_group_uid, platform=platform
        )


async def get_platforms(user_group_uid: UUID):

    return await investment_handler.get_platforms(user_group_uid=user_group_uid)


async def get_platform(user_group_uid: UUID, platform_uid: UUID):

    try:
        return await investment_handler.get_platform(
            user_group_uid=user_group_uid, platform_uid=platform_uid
        )

    except NotFoundError:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="platform is not found"
        )


async def decode_platform(
    user_group_uid: UUID, platform_uid: UUID, user_password: str, user_uid: UUID
):

    platform = await get_platform(
        user_group_uid=user_group_uid, platform_uid=platform_uid
    )

    user_profile = await user_service.check_user(user_uid=user_uid)

    if (
        auth_utils.verify_password(
            plain_password=user_password, hashed_password=user_profile.password
        )
        is False
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="access credential is invalid"
        )

    return investment_utils.platform_decoder(platform=platform)


async def update_platform(
    user_group_uid: UUID, platform_uid: UUID, platform_update: schemas.PlatformUpdate
):

    await get_platform(user_group_uid=user_group_uid, platform_uid=platform_uid)

    return await investment_handler.update_platform(
        platform_uid=platform_uid, platform_update=platform_update
    )


async def delete_platform(user_group_uid: UUID, platform_uid: UUID):

    await get_platform(user_group_uid=user_group_uid, platform_uid=platform_uid)

    await investment_handler.delete_platform(platform_uid=platform_uid)

    return {}


# ######################################### Investment ##################################################


async def check_investment(plan_name: str, platform_uid: UUID, user_group_uid: UUID):

    return await investment_handler.check_investment(
        plan_name=plan_name, platform_uid=platform_uid, user_group_uid=user_group_uid
    )


async def create_investment(
    platform_uid: UUID, user_group_uid: UUID, investment: schemas.Investment
):

    investment.plan_name = investment.plan_name.capitalize().strip()

    try:
        await check_investment(
            plan_name=investment.plan_name,
            platform_uid=platform_uid,
            user_group_uid=user_group_uid,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="plan already exists"
        )
    except NotFoundError:

        return await investment_handler.create_investment(
            investment=investment,
            platform_uid=platform_uid,
            user_group_uid=user_group_uid,
        )


async def get_investments(platform_uid: UUID, user_group_uid: UUID):
    await get_platform(user_group_uid=user_group_uid, platform_uid=platform_uid)

    return await investment_handler.get_investments(platform_uid=platform_uid)


async def get_investment(
    platform_uid: UUID, user_group_uid: UUID, investment_uid: UUID
):

    await get_platform(user_group_uid=user_group_uid, platform_uid=platform_uid)

    try:
        return await investment_handler.get_investment(
            platform_uid=platform_uid,
            investment_uid=investment_uid,
        )

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="investment plan not found"
        )


async def update_investment(
    platform_uid: UUID,
    investment_uid: UUID,
    investment_update: schemas.InvestmentUpdate,
):

    await get_investment(platform_uid=platform_uid, investment_uid=investment_uid)

    return await investment_handler.update_investment(
        investment_uid=investment_uid, investment_update=investment_update
    )


async def delete_investment(
    platform_uid: UUID, investment_uid: UUID, user_group_uid: UUID
):

    await get_investment(
        platform_uid=platform_uid,
        user_group_uid=user_group_uid,
        investment_uid=investment_uid,
    )

    await investment_handler.delete_investment(
        investment_uid=investment_uid, user_group_uid=user_group_uid
    )

    return {}


###############################     Investment Tracker     ####################################################


async def create_investment_tracker(
    platform_uid: UUID,
    user_group_uid: UUID,
    investment_uid: UUID,
    investment_tracker: schemas.InvestmentTracker,
):

    await get_investment(
        investment_uid=investment_uid,
        user_group_uid=user_group_uid,
        platform_uid=platform_uid,
    )

    return await investment_handler.create_investment_tracker(
        investment_uid=investment_uid, investment_tracker=investment_tracker
    )


async def get_investment_trackers(
    investment_uid: UUID,
    user_group_uid: UUID,
    platform_uid: UUID,
):

    await get_investment(
        investment_uid=investment_uid,
        user_group_uid=user_group_uid,
        platform_uid=platform_uid,
    )

    return await investment_handler.get_investment_trackers(
        investment_uid=investment_uid
    )


async def get_investment_tracker(investment_uid: UUID, tracker_uid: UUID):
    try:
        return await investment_handler.get_investment_tracker(
            investment_uid=investment_uid, uid=tracker_uid
        )

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="investment tracker record not found",
        )


async def update_investment_tracker(
    investment_uid: UUID,
    tracker_uid: UUID,
    investment_tracker_update: schemas.InvestmentTracker,
):

    await get_investment_tracker(
        investment_uid=investment_uid,
        tracker_uid=tracker_uid,
    )

    return await investment_handler.update_investment_tracker(
        uid=tracker_uid, investment_tracker_update=investment_tracker_update
    )


async def delete_invest_tracker(investment_uid: UUID, tracker_uid: UUID):
    await get_investment_tracker(investment_uid=investment_uid, tracker_uid=tracker_uid)

    await investment_handler.delete_investment_tracker(uid=tracker_uid)

    return {}


async def investment_dashboard(user_group_uid: UUID):

    investment_dashboard_profile = {}

    platform_profiles = await get_platforms(user_group_uid=user_group_uid)

    for platform in platform_profiles.result_set:

        if investment_dashboard_profile.get(platform.name) is None:
            investment_dashboard_profile[platform.name] = {
                "cash_in": {},
                "cash_out": {},
            }

        for plans in platform.investment_plans:
            for tracker in plans.activities:

                if tracker.transaction_type == schemas.TransactionType.credit.value:

                    if (
                        investment_dashboard_profile[platform.name]["cash_in"].get(
                            tracker.currency
                        )
                        is None
                    ):

                        investment_dashboard_profile[platform.name]["cash_in"][
                            tracker.currency
                        ] = tracker.amount

                    else:
                        investment_dashboard_profile[platform.name]["cash_in"][
                            tracker.currency
                        ] += tracker.amount

                else:

                    if (
                        investment_dashboard_profile[platform.name]["cash_in"].get(
                            tracker.currency
                        )
                        is None
                    ):

                        investment_dashboard_profile[platform.name]["cash_in"][
                            tracker.currency
                        ] = tracker.amount

                    else:
                        investment_dashboard_profile[platform.name]["cash_in"][
                            tracker.currency
                        ] += tracker.amount

    return schemas.InvestmentDashboard(result=investment_dashboard_profile)
