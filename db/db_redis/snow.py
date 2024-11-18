from db.db_redis.connection import r


r.set("foo1", "bar1")
print(r.get("foo"))
