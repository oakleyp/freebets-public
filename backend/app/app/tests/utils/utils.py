import random
import string
from datetime import datetime, timedelta
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings


def random_lower_string(length: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def random_datetime_in_range(
    start: datetime, end: datetime, precision_modifier: str = "hours"
) -> datetime:
    delta = end - start

    if precision_modifier == "days":
        int_delta = delta.days
    elif precision_modifier == "hours":
        int_delta = delta.seconds / 60 / 60
    elif precision_modifier == "minutes":
        int_delta = delta.seconds / 60
    elif precision_modifier == "seconds":
        int_delta = delta.total_seconds()
    else:
        raise ValueError(
            "Invalid precision_modifier provided (%s)." % precision_modifier
        )

    if int_delta < 1:
        return start

    random_val = random.randrange(int(int_delta))
    return start + timedelta(**{precision_modifier: random_val})
