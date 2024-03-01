import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import redis


class CacheBaseCli(ABC):
    def __init__(self, obj, conn_data, *args, **kwargs):
        self._connection = self._get_connection(obj, conn_data)
        self._connection_error = "[ERROR] Lost connection to cache"
        self.health_status = False
        self.health_status_time = None
        self.check_timeout_min = 5
        self._check_health()

    @abstractmethod
    def get(self, value):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    def _get_connection(self, obj, conn_data):
        try:
            conn = obj(**conn_data)
            return conn
        except Exception:
            return None

    @abstractmethod
    def _check_health(self):
        pass

    def check_health(self):
        if (
            not self.health_status
            and self.health_status_time
            and (datetime.now() - self.health_status_time)
            >= timedelta(minutes=self.check_timeout_min)
        ):
            self._check_health()

        return self.health_status


class CacheRedisCli(CacheBaseCli):
    def get(self, value):
        try:
            res = self._connection.get(value)
            self.health_status = True
            return res
        except Exception:
            self.health_status = False
            sys.stdout.write(
                f"\n[{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] {self._connection_error}\n"
            )
            return None
        finally:
            self.health_status_time = datetime.now()

    def set(self, key, value):
        try:
            self._connection.set(key, value)
            self.health_status = True
        except Exception:
            self.health_status = False
            sys.stdout.write(
                f"\n[{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] {self._connection_error}\n"
            )
        finally:
            self.health_status_time = datetime.now()

    def _check_health(self):
        try:
            self._connection.ping()
            self.health_status = True
        except Exception:
            self.health_status = False
            sys.stdout.write(
                f"\n[{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] {self._connection_error}\n"
            )
        finally:
            return self.health_status


cache_connection = CacheRedisCli(
    obj=redis.Redis, conn_data={"host": os.environ.get("REDIS_CLIENT"), "port": 6379}
)
