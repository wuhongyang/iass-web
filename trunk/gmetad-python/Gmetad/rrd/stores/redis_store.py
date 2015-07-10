from Gmetad.rrd.rrd_store import RRDStore
import redis
import logging

def get_rrd_store(impid="redis", cfgid="rrd-store"):
    ''' Get the specified RRD store from the factory via cfgid '''
    return RedisStore(impid, cfgid)

class RedisStore(RRDStore):
    ''' The RRD store class implemented via redis '''

    REDIS_HOST = 'host'                 # The host of redis-server
    REDIS_PORT = 'port'                 # The port of redis-server
    REDIS_DB = 'db'                     # The database in redis-server

    _cfgDefaults = {
        REDIS_HOST: '127.0.0.1',
        REDIS_PORT: 6379,
        REDIS_DB: 0,
    }

    def initConfDefaults(self):
        self.cfg = RedisStore._cfgDefaults

    def initConfHandlers(self):
        '''Init the handler array of configs'''
        self.cfgHandlers = {
            RedisStore.REDIS_HOST: self._parseRedisHost,
            RedisStore.REDIS_PORT: self._parseRedisPort,
            RedisStore.REDIS_DB: self._parseRedisDB,
        }

    def _parseRedisHost(self, arg):
        ''' Parse the Redis host. '''
        self.cfg[RedisStore.REDIS_HOST] = arg.strip().strip('"')

    def _parseRedisPort(self, arg):
        ''' Parse the Redis port. '''
        self.cfg[RedisStore.REDIS_PORT] = arg.strip().strip('"')

    def _parseRedisDB(self, arg):
        ''' Parse the Redis port. '''
        self.cfg[RedisStore.REDIS_DB] = arg.strip().strip('"')

    def _connect(self):
        try:
            _redis = redis.StrictRedis(
                host=self.cfg[RedisStore.REDIS_HOST],
                port=self.cfg[RedisStore.REDIS_PORT],
                db=self.cfg[RedisStore.REDIS_DB]
            )
            _redis.ping()
            return _redis
        except redis.ConnectionError:
            logging.error('Redis server [%s:%d/%s] not ready' % (
            self.cfg[RedisStore.REDIS_HOST], self.cfg[RedisStore.REDIS_PORT],
            self.cfg[RedisStore.REDIS_DB]))
            raise

    def getHostInfo(self, hostKey):
        ''' Get the host information from redis-server '''
        _redis = self._connect()
        hostinfo = None
        if _redis.exists(hostKey):
            hostinfo = _redis.hgetall(hostKey)
        return hostinfo


