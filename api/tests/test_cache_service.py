import pytest

from conftest import redis_cache_service


@pytest.mark.django_db
class TestRedisCache:

    def test_check_health(self, redis_cache_service):
        redis_cache_service._connection.ping.return_value = True
        assert redis_cache_service._check_health() is True
        redis_cache_service._connection.ping.assert_called()

    def test_get(self, redis_cache_service):
        redis_cache_service._connection.get.return_value = "value"
        result = redis_cache_service.get("key")
        assert result == "value"
        redis_cache_service._connection.get.assert_called_once_with("key")

    def test_set(self, redis_cache_service):
        redis_cache_service.set("key", "value")
        redis_cache_service._connection.set.assert_called_once_with("key", "value")
