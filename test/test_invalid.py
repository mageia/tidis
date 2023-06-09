import random
import unittest

from rediswrap import RedisWrapper
from test_util import NaN, random_string


class InvalidTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = RedisWrapper.get_instance()

        cls.k1 = '__invalid1__'

        cls.f1 = 'f1'
        cls.f2 = 'f2'

        cls.v1 = 'value1'
        cls.v2 = 'value2'

    def setUp(self):
        self.r.execute_command('del', self.k1)
        pass

    def assertError(self, err_str, cmd, *args):
        with self.assertRaises(Exception) as cm:
            self.r.execute_command(cmd, *args)
        err = cm.exception
        self.assertEqual(str(err), err_str)

    def assertInvalid(self, cmd, *args):
        self.assertError('Invalid arguments', cmd, *args)

    # # ================ string ================
    def test_set_get(self):
        self.assertInvalid('set', self.k1, self.v1, self.v2)
        self.assertInvalid('get', self.k1, self.v1, self.v2)

    def test_setex(self):
        self.assertInvalid('setex', self.k1, self.v1, self.v2)

    def test_setnx(self):
        self.assertInvalid('setnx', self.k1, self.v1, self.v2)

    def test_mset(self):
        self.assertInvalid('mset', self.k1)

    def test_incr(self):
        self.assertInvalid('incr')

    def test_incrby(self):
        self.assertInvalid('incrby', self.k1, self.v1, self.v2)
        self.assertInvalid('incrby', self.k1, self.v1, NaN)

    def test_decr(self):
        self.assertInvalid('decr')

    def test_decrby(self):
        self.assertInvalid('decrby', self.k1, self.v1, self.v2)
        self.assertInvalid('decrby', self.k1, self.v1, NaN)

    def test_strlen(self):
        self.assertInvalid('strlen', self.k1, self.v1)

    # ================ hash ================
    def test_hget_hset(self):
        self.assertInvalid('hget', self.k1, self.f1, self.v1)
        self.assertInvalid('hset', self.k1, self.f1)

    def test_hmget_hmset(self):
        self.assertInvalid('hmget')
        self.assertInvalid('hmset', self.k1, self.f1)

    def test_hsetnx(self):
        self.assertInvalid('hsetnx')
        self.assertInvalid('hsetnx', self.k1, self.f1)
        self.assertInvalid('hsetnx', self.k1, self.f1, self.v1, self.f2, self.v2)

    def test_hexists(self):
        self.assertInvalid('hexists', self.k1)

    def test_hstrlen(self):
        self.assertInvalid('hstrlen', self.k1)

    def test_hlen(self):
        self.assertInvalid('hlen', self.k1, self.f1)

    def test_hkeys(self):
        self.assertInvalid('hkeys', self.k1, self.f1)

    def test_hvals(self):
        self.assertInvalid('hvals', self.k1, self.f1)

    def test_hgetall(self):
        self.assertInvalid('hgetall', self.k1, self.f1)

    def test_hincrby(self):
        self.assertInvalid('hincrby', self.k1, self.v1, self.v2)
        self.assertInvalid('hincrby', self.k1, self.f1, NaN)

    def test_hdel(self):
        self.assertInvalid('hdel')

    # ================ list ================
    def test_lpop(self):
        self.assertInvalid('lpop', self.k1, self.v1, self.v2)

    def test_lpush(self):
        self.assertInvalid('lpush')

    def test_rpop(self):
        self.assertInvalid('rpop', self.k1, self.v1, self.v2)

    def test_rpush(self):
        self.assertInvalid('rpush')

    def test_llen(self):
        self.assertInvalid('llen', self.k1, self.v1, self.v2)

    def test_lindex(self):
        self.assertInvalid('lindex', self.k1)
        self.assertInvalid('lindex', self.k1, NaN)

    def test_lrange(self):
        self.assertInvalid('lrange', self.k1)
        self.assertInvalid('lrange', self.k1, NaN, NaN)

    def test_lset(self):
        self.assertInvalid('lset', self.k1)
        self.assertInvalid('lset', self.k1, NaN, self.v1)

    def test_ltrim(self):
        self.assertInvalid('ltrim', self.k1)
        self.assertInvalid('ltrim', self.k1, NaN, NaN)

    def test_lrem(self):
        self.assertInvalid('lrem', self.k1, NaN, 'x')
        self.assertInvalid('lrem', self.k1, 0, 'x', 'x')

    def test_linsert(self):
        self.assertInvalid('linsert', self.k1, 'invalid_op', 'x', 'x')
        self.assertInvalid('linsert', self.k1, 'before', 'x')
        self.assertInvalid('linsert', self.k1, 'before', 'x', 'x', 'x')

    # ================ set ================
    def test_sadd(self):
        self.assertInvalid('sadd')

    def test_scard(self):
        self.assertInvalid('scard', self.k1, self.v1, self.v2)

    def test_sismember(self):
        self.assertInvalid('sismember', self.k1, self.v1, self.v2)

    def test_smismember(self):
        self.assertInvalid('smismember')

    def test_smembers(self):
        self.assertInvalid('smembers', self.k1, self.v1, self.v2)

    def test_srandmember(self):
        self.assertInvalid('srandmember', self.k1, self.v1, self.v2)

    def test_srem(self):
        self.assertInvalid('srem')

    def test_spop(self):
        self.assertInvalid('spop', self.k1, self.v1, self.v2)

    # ================ sorted set ================
    def test_zadd(self):
        self.assertInvalid('zadd', self.k1)

    def test_zcard(self):
        self.assertInvalid('zcard', self.k1, self.v1, self.v2)

    def test_zrange(self):
        self.assertInvalid('zrange', self.k1)

    def test_zrevrange(self):
        self.assertInvalid('zrevrange', self.k1)

    def test_zrangebyscore(self):
        self.assertInvalid('zrangebyscore', self.k1)

    def test_zrevrangebyscore(self):
        self.assertInvalid('zrevrangebyscore', self.k1)

    def test_zremrangebyscore(self):
        self.assertInvalid('zremrangebyscore', self.k1)

    def test_zcount(self):
        self.assertInvalid('zcount', self.k1)

    def test_zscore(self):
        self.assertInvalid('zscore', self.k1)

    def test_zrem(self):
        self.assertInvalid('zrem')

    def test_zrank(self):
        self.assertInvalid('zrank', self.k1, self.v1, self.v2)

    def test_zpopmin(self):
        self.assertInvalid('zpopmin', self.k1, self.v1, self.v2)

    def test_zincrby(self):
        self.assertInvalid('zincrby', self.k1, self.v1)
        self.assertInvalid('zincrby', self.k1, self.v1, self.f1)
        self.assertError('value is not a valid float', 'zincrby', self.k1, NaN, self.f1)

    # ================ generic ================
    def test_type(self):
        self.assertInvalid('type', self.k1, self.v1)

    def test_persist(self):
        self.assertInvalid('persist', self.k1, self.v1, self.v2)

    def test_pexpire(self):
        self.assertInvalid('pexpire', self.k1, self.v1, self.v2)
        self.assertInvalid('pexpire', self.k1, NaN)

    def test_pexpireat(self):
        self.assertInvalid('pexpireat', self.k1, self.v1, self.v2)
        self.assertInvalid('pexpireat', self.k1, NaN)

    def test_expire(self):
        self.assertInvalid('expire', self.k1, self.v1, self.v2)
        self.assertInvalid('expire', self.k1, NaN)

    def test_expireat(self):
        self.assertInvalid('expireat', self.k1, self.v1, self.v2)
        self.assertInvalid('expireat', self.k1, NaN)

    def test_unknown(self):
        arbitrary_unknown = "unknown_" + random_string(random.randint(3, 6)).lower()
        self.assertError("unknown command '{}'".format(arbitrary_unknown), arbitrary_unknown)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.r.execute_command('del', cls.k1)
        print('test data cleaned up')
