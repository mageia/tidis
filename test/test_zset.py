import time
import unittest

from rediswrap import RedisWrapper
from test_util import sec_ts_after_five_secs, msec_ts_after_five_secs, NOT_EXISTS_LITERAL, CmdType, \
    trigger_async_del_size


class ZsetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = RedisWrapper.get_instance()

        cls.k1 = '__zset1__'
        cls.k2 = '__zset2__'

        cls.v1 = 'value1'
        cls.v2 = 'value2'

    def setUp(self):
        self.r.execute_command('del', self.k1)
        self.r.execute_command('del', self.k2)
        pass

    def test_zadd(self):
        for i in range(200):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        self.assertEqual(self.r.zcard(self.k1), 200)
        for i in range(200):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 0)
        self.assertEqual(self.r.zcard(self.k1), 200)

        # test for add multiple member score
        self.assertEqual(self.r.zadd(self.k1, {str(200): 200, str(201): 201}), 2)
        self.assertEqual(self.r.zcard(self.k1), 202)

        # zadd xx
        self.assertEqual(self.r.zcard(self.k2), 0)
        self.assertEqual(self.r.zadd(self.k2, {self.v1: 1}, xx=True), 0)
        self.assertEqual(self.r.zcard(self.k2), 0)
        self.assertEqual(self.r.zadd(self.k2, {self.v1: 1}), 1)
        self.assertListEqual(self.r.zrange(self.k2, 0, -1, False, True), [(self.v1, 1)])
        self.assertEqual(self.r.zadd(self.k2, {self.v1: 2}, xx=True), 0)
        self.assertEqual(self.r.zadd(self.k2, {self.v1: 3}, xx=True, ch=True), 1)
        self.assertListEqual(self.r.zrange(self.k2, 0, -1, False, True), [(self.v1, 3)])

        # zadd nx
        self.assertEqual(self.r.zadd(self.k2, {self.v1: 4}, nx=True), 0)
        self.assertListEqual(self.r.zrange(self.k2, 0, -1, False, True), [(self.v1, 3)])
        self.assertEqual(self.r.zadd(self.k2, {self.v2: 1}, nx=True), 1)
        self.assertListEqual(self.r.zrange(self.k2, 0, -1, False, True), [(self.v2, 1), (self.v1, 3)])

        # zadd ch
        self.assertEqual(self.r.zadd(self.k2, {self.v1: 1, self.v2: 1, 'new_ele': 2}), 1)
        self.assertEqual(self.r.zadd(self.k2, {self.v1: 2, self.v2: 2, 'new_ele': 2}, ch=True), 2)

        # zadd lt, gt, incr are pending

    def test_type(self):
        self.assertEqual(self.r.type(self.k1), CmdType.NULL.value)
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 1}), 1)
        self.assertEqual(self.r.type(self.k1), CmdType.ZSET.value)

    def test_zcard(self):
        self.assertEqual(self.r.zcard(self.k1), 0)
        for i in range(200):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        self.assertEqual(self.r.zcard(self.k1), 200)
        for i in range(200):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 0)
        self.assertEqual(self.r.zcard(self.k1), 200)

    def test_zrange(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        self.assertListEqual(self.r.zrange(self.k1, 0, -1, False, False), [str(i) for i in range(100)])
        self.assertListEqual(self.r.zrange(self.k1, 10, 20, False, False), [str(i) for i in range(10, 21)])
        self.assertListEqual(self.r.zrange(self.k1, 20, 10, False, False), [])
        # range with scores
        self.assertListEqual(self.r.zrange(self.k1, 10, 20, False, True), [(str(i), i) for i in range(10, 21)])

    def test_zrevrange(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): 100 - i}), 1)
        self.assertListEqual(self.r.zrevrange(self.k1, 0, -1, False), [str(i) for i in range(100)])
        self.assertListEqual(self.r.zrevrange(self.k1, 10, 20, False), [str(i) for i in range(10, 21)])
        self.assertListEqual(self.r.zrevrange(self.k1, 20, 10, False), [])
        #  range with scores
        self.assertListEqual(self.r.zrevrange(self.k1, 10, 20, True), [(str(i), 100 - i) for i in range(10, 21)])

    def test_zrangebyscore(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): 100 - i}), 1)
        self.assertListEqual(self.r.zrangebyscore(self.k1, '-inf', '+inf'),
                             list(reversed([str(i) for i in range(100)])))
        self.assertListEqual(self.r.zrangebyscore(self.k1, '0', '-1'), [])

    def test_zrevrangebyscore(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): 100 - i}), 1)
        self.assertListEqual(self.r.zrevrangebyscore(self.k1, '+inf', '-inf'), [str(i) for i in range(100)])
        self.assertListEqual(self.r.zrevrangebyscore(self.k1, '-1', '0'), [])

    def test_zremrangebyscore(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        self.assertEqual(self.r.zremrangebyscore(self.k1, 21, 30), 10)
        self.assertEqual(self.r.zremrangebyscore(self.k1, 30, 21), 0)

    def test_zremrangebyrank(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        self.assertEqual(self.r.zremrangebyrank(self.k1, 21, 30), 10)
        self.assertEqual(self.r.zremrangebyrank(self.k1, 30, 21), 0)
        self.assertEqual(self.r.zremrangebyrank(self.k1, 0, -1), 90)
        self.assertEqual(self.r.zcard(self.k1), 0)

    def test_zcount(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        self.assertEqual(self.r.zcount(self.k1, 50, 100), 50)

    def test_zscore(self):
        self.assertIsNone(self.r.zscore(self.k1, self.v1))
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        for i in range(100):
            self.assertEqual(self.r.zscore(self.k1, str(i)), i)

    def test_zrem(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        for i in range(10, 100):
            self.assertEqual(self.r.zrem(self.k1, str(i)), 1)
        self.assertEqual(self.r.zcard(self.k1), 10)

        # multi values
        self.assertEqual(self.r.zcard(self.k1), 10)
        self.assertEqual(self.r.zrem(self.k1, "1", "2", "3"), 3)
        self.assertEqual(self.r.zcard(self.k1), 7)

    def test_zrank(self):
        for i in range(100):
            self.assertEqual(self.r.zadd(self.k1, {str(i): i}), 1)
        for i in range(100):
            self.assertEqual(self.r.zrank(self.k1, str(i)), i)

    def test_zpopmin(self):
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 1, self.v2: 2}), 2)
        self.assertListEqual(self.r.zpopmin(self.k1), [(self.v1, 1)])

    def test_zpopmax(self):
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 1, self.v2: 2}), 2)
        self.assertListEqual(self.r.zpopmax(self.k1), [(self.v2, 2)])

    def test_zincrby(self):
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 1, self.v2: 2}), 2)
        self.assertListEqual(self.r.zrange(self.k1, 0, -1, False, True), [(self.v1, 1), (self.v2, 2)])
        self.assertEqual(self.r.zincrby(self.k1, 2, self.v1), 3)
        self.assertListEqual(self.r.zrange(self.k1, 0, -1, False, True), [(self.v2, 2), (self.v1, 3)])
        self.assertEqual(self.r.zscore(self.k1, self.v1), 3)

        self.assertEqual(self.r.zincrby(self.k1, -1.2, self.v1), 1.8)
        self.assertListEqual(self.r.zrange(self.k1, 0, -1, False, True), [(self.v1, 1.8), (self.v2, 2)])
        self.assertEqual(self.r.zscore(self.k1, self.v1), 1.8)

        self.assertEqual(self.r.zincrby(self.k1, 1.5, NOT_EXISTS_LITERAL), 1.5)
        self.assertListEqual(self.r.zrange(self.k1, 0, -1, False, True),
                             [(NOT_EXISTS_LITERAL, 1.5), (self.v1, 1.8), (self.v2, 2)])
        self.assertEqual(self.r.zscore(self.k1, NOT_EXISTS_LITERAL), 1.5)

    def test_del(self):
        self.assertTrue(self.r.zadd(self.k1, {self.v1: 1}), 1)
        self.assertEqual(self.r.zcard(self.k1), 1)
        self.assertEqual(self.r.execute_command('del', self.k1), 1)
        self.assertEqual(self.r.zcard(self.k1), 0)

        # multi keys
        self.assertTrue(self.r.zadd(self.k2, {self.v2: 1}), 1)
        self.assertEqual(self.r.zcard(self.k2), 1)
        self.assertEqual(self.r.execute_command("del", self.k1, self.k2), 1)
        self.assertEqual(self.r.zcard(self.k2), 0)

    def test_async_del(self):
        size = trigger_async_del_size()
        for i in range(size):
            self.assertTrue(self.r.zadd(self.k1, {str(i): i}))
        for i in range(size):
            self.assertEqual(int(self.r.zscore(self.k1, str(i))), i)
        self.assertTrue(self.r.delete(self.k1))
        self.assertEqual(self.r.zcard(self.k1), 0)
        self.assertTrue(self.r.zadd(self.k1, {self.v1: 1}))

    def test_async_expire(self):
        size = trigger_async_del_size()
        for i in range(size):
            self.assertTrue(self.r.zadd(self.k1, {str(i): i}))
        for i in range(size):
            self.assertEqual(int(self.r.zscore(self.k1, str(i))), i)
        self.assertTrue(self.r.expire(self.k1, 1))
        time.sleep(1)
        self.assertEqual(self.r.zcard(self.k1), 0)
        self.assertTrue(self.r.zadd(self.k1, {self.v1: 1}))

    def test_persist(self):
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 10}), 1)
        # expire in 5s
        self.assertTrue(self.r.execute_command('pexpire', self.k1, 5000))
        pttl = self.r.execute_command('pttl', self.k1)
        self.assertLessEqual(pttl, 5000)
        self.assertGreater(pttl, 0)
        self.assertEqual(self.r.zcard(self.k1), 1)
        # persis the key
        self.assertEqual(self.r.persist(self.k1), 1)
        self.assertEqual(self.r.execute_command('pttl', self.k1), -1)

    def test_pexpire(self):
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 10}), 1)
        # expire in 5s
        self.assertTrue(self.r.execute_command('pexpire', self.k1, 5000))
        pttl = self.r.execute_command('pttl', self.k1)
        self.assertLessEqual(pttl, 5000)
        self.assertGreater(pttl, 0)
        self.assertEqual(self.r.zcard(self.k1), 1)
        time.sleep(6)
        self.assertEqual(self.r.zcard(self.k1), 0)

    def test_pexpireat(self):
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 10}), 1)
        # expire in 5s
        self.assertTrue(self.r.execute_command('pexpireat', self.k1, msec_ts_after_five_secs()))
        time.sleep(1)
        pttl = self.r.execute_command('pttl', self.k1)
        self.assertLess(pttl, 5000)
        self.assertGreater(pttl, 0)
        self.assertEqual(self.r.zcard(self.k1), 1)
        time.sleep(6)
        self.assertEqual(self.r.zcard(self.k1), 0)

    def test_expire(self):
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 10}), 1)
        # expire in 5s
        self.assertTrue(self.r.execute_command('expire', self.k1, 5))
        ttl = self.r.execute_command('ttl', self.k1)
        self.assertLessEqual(ttl, 5)
        self.assertGreater(ttl, 0)
        self.assertEqual(self.r.zcard(self.k1), 1)
        time.sleep(6)
        self.assertEqual(self.r.zcard(self.k1), 0)

    def test_expireat(self):
        self.assertEqual(self.r.zadd(self.k1, {self.v1: 10}), 1)
        # expire in 5s
        self.assertTrue(self.r.execute_command('expireat', self.k1, sec_ts_after_five_secs()))
        ttl = self.r.execute_command('ttl', self.k1)
        self.assertLessEqual(ttl, 5)
        self.assertGreater(ttl, 0)
        self.assertEqual(self.r.zcard(self.k1), 1)
        time.sleep(6)
        self.assertEqual(self.r.zcard(self.k1), 0)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.r.execute_command('del', cls.k1)
        cls.r.execute_command('del', cls.k2)
        print('test data cleaned up')
