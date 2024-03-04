import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import redis


class Cachable(ABC):
    @abstractmethod
    def get(self, value):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def _check_health(self):
        pass


class CacheBaseService(Cachable):
    def __init__(self, obj, conn_data, *args, **kwargs):
        self._connection = self._get_connection(obj, conn_data)
        self._connection_error = "[ERROR] Lost connection to cache"
        self.health_status = False
        self.health_status_time = None
        self.check_timeout_min = 5
        self._check_health()

    def _get_connection(self, obj, conn_data):
        try:
            conn = obj(**conn_data)
            return conn
        except Exception:
            return None

    def check_health(self):
        if (
            not self.health_status
            and self.health_status_time
            and (datetime.now() - self.health_status_time)
            >= timedelta(minutes=self.check_timeout_min)
        ):
            self._check_health()

        return self.health_status


class RedisCacheService(CacheBaseService):
    def _update_health_status(func):
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                self.health_status = True
                return result
            except Exception as e:
                self.health_status = False
                sys.stdout.write(
                    f"\n[{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] {self._connection_error}\n"
                )
                return None
            finally:
                if func.__name__ != "_check_health":
                    self.health_status_time = datetime.now()

        return wrapper

    @_update_health_status
    def get(self, value):
        return self._connection.get(value)

    @_update_health_status
    def set(self, key, value):
        return self._connection.set(key, value)

    @_update_health_status
    def _check_health(self):
        return self._connection.ping()


cache_service = RedisCacheService(
    obj=redis.Redis, conn_data={"host": os.environ.get("REDIS_CLIENT"), "port": 6379}
)
