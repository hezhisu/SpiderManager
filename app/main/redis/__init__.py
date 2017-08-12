import redis
my_redis = redis.StrictRedis(host='localhost',port=6379,db=0,decode_responses=True)