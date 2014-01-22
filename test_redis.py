# coding: utf-8
import redis
import storable
from struct import unpack


class RedisSession(object):

    def __init__(self, *args, **kwargs):
        # defaults
        self.host = 'localhost'
        self.port = 6379
        self.db = 0

        if kwargs.get('host', None):
            self.host = kwargs['host']
        if kwargs.get('port', None):
            self.port = kwargs['port']
        if kwargs.get('db', None):
            self.db = kwargs['db']

        self.connection = redis.StrictRedis(host=self.host, port=self.port, db=self.db)

    def process_cookies(self, cookies):
        self.session_key = cookies.get('dancer.session', None)

    def read(self, key):
        raw_data = self.connection.get(key)

        print(type(raw_data))

        return storable.thaw(raw_data)


redisCon = RedisSession()
result = redisCon.read("449701409573983014964654998572780158") #Взял свою активную сессию
print(type(result))