# Pull in Earnings  Dashboard.

# Provide the date and year.

# Use historical earnings, to show geowth with time.

# Based on Earnings Make a call to the DB to fetch records of similar standing.


# Check through investments calling Platforms or investment dashboard.
# with this show a comparision with time with earnings and how much may and may not have been set aside.


# Fetch the highest set asiders and suggest the platform they use.

# Infer not financial advise.


# Talk about other Index funds, Crypto, Foreign realestate if in Africa. Hedging aganist the dollar.

# Setting up a will and if a top earner and investor setting a LLC Trust


# Compare with Country of Orgin Stat.


from uuid import UUID

import accountant.services.earning_service as earning_service
import accountant.services.investment_service as investment_service


async def proto_func(user_uid: UUID, user_group_uid: UUID):

    # investment_dashboard =
    await investment_service.investment_dashboard(user_group_uid=user_group_uid)

    # earning_dashboard =
    await earning_service.earning_dashboard(user_uid=user_uid)
