import redis
from accountant.root.settings import Settings


settings = Settings()


redis_url = str(settings.redis_url)
acc_redis = redis.Redis(decode_responses=True)
acc_redis.from_url(url=redis_url, decode_responses=True)
