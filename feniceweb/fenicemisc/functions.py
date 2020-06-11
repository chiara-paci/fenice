import pytz
import datetime
import os.path

def date_serialize(dt):
    if dt.tzinfo is None:
        dt=pytz.utc.localize(dt)
        dt_utc=dt
    else:
        dt_utc=dt.astimezone(pytz.utc)
    return {
        "timestamp": dt_utc.timestamp(),
        "timezone": {
            "name":"UTC",
            "utcoffset": 0,
            "dst": False
        },
        "year": dt_utc.year,
        "month": dt_utc.month,
        "day": dt_utc.day,
        "hour": dt_utc.hour,
        "minute": dt_utc.minute,
        "second": dt_utc.second,
        "microsecond": dt_utc.microsecond,
        "weekday": dt_utc.weekday(),
    }

def date_deserialize(ser):
    args=[         
        ser["year"],
        ser["month"],
        ser["day"],
        ser["hour"],
        ser["minute"],
        ser["second"],
        ser["microsecond"],
    ]

    return pytz.timezone(ser["timezone"]["name"]).localize(datetime.datetime(*args),is_dst=ser["timezone"]["dst"])

def relative_path(path,prefix):
    if not path.startswith(prefix): return path
    return os.path.relpath(path,prefix)

