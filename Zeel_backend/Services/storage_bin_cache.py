import json
from fastapi.encoders import jsonable_encoder
from core.cache import redis_client  # adjust import

CACHE_TTL = 300  # 5 minutes


def get_storage_bin_cache(key: str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def set_storage_bin_cache(key: str, data):
    serialized_data = json.dumps(jsonable_encoder(data))
    redis_client.setex(key, CACHE_TTL, serialized_data)


def delete_storage_bin_cache(key: str):
    redis_client.delete(key)


def delete_storage_bin_list_cache():
    for key in redis_client.scan_iter("storage_bins:*"):
        redis_client.delete(key)
