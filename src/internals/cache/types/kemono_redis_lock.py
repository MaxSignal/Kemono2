import redis_lock


class KemonoRedisLock(redis_lock.Lock):
    def release(self):
        if self._lock_renewal_thread is not None:
            self._stop_lock_renewer()
        # soft reimplementation of UNLOCK_SCRIPT in Python
        self._client.delete(self._signal)
        self._client.lpush(self._signal, 1)
        self._client.pexpire(self._signal, self._signal_expire)
        self._client.delete(self._name)

    def extend(self, expire=None):
        if expire:
            expire = int(expire)
            if expire < 0:
                raise ValueError("A negative expire is not acceptable.")
        elif self._expire is not None:
            expire = self._expire
        else:
            raise TypeError(
                "To extend a lock 'expire' must be provided as an "
                "argument to `extend()` method or at initialization time."
            )
        # soft reimplementation of EXTEND_SCRIPT in Python
        self._client.expire(self._name, expire)
