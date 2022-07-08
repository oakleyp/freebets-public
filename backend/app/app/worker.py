from raven import Client

from app.core.celery_app import celery_app
from app.core.config import settings
from app.lib.crawlers.live_racing import LiveRacingCrawler
from app.lib_private.clients.live_racing import LiveRacingClient

client_sentry = Client(settings.SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task()
def pull_races():
    client = LiveRacingClient()
    crawler = LiveRacingCrawler(client)

    print(crawler.get_all_track_races())
