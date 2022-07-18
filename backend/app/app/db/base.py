# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.bet import Bet  # noqa
from app.models.bet_tag import BetTag  # noqa
from app.models.item import Item  # noqa
from app.models.raceday_refresh_log import RaceDayRefreshLog  # noqa
from app.models.user import User  # noqa
