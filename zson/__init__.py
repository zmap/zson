import datetime
from anyjson import loads, dumps

def __zson_encode(obj):
    if isinstance(obj, (str, int, float, bool, None.__class__)):
        return dumps(obj)
    elif isinstance(obj, (list, tuple, set)):
        return dumps(list(map(lambda x: __zson_encode(x), obj)))
    elif isinstance(obj, dict):
        return dumps(dict([(__zson_encode(k), __zson_encode(v)) for k,v in obj.items()]))
    elif isinstance(obj, datetime.datetime):
        return dumps({
            "__zson_class_name":"datetime",
            "year":obj.year,
            "month":obj.month,
            "day":obj.day,
            "hour":obj.hour,
            "minute":obj.minute,
            "second":obj.second,
            "microsecond":obj.microsecond
        })
    elif hasattr(obj, "to_json"):
        d = obj.to_json()
        if "__zson_class_name" in d:
             raise Exception("Object is not allowed to define __zson_class_name in to_json")
        d["__zson_class_name"] = obj.__class__.__name__
        return dumps(self, d)
    else:
        raise Exception("unable to encode object %s to json" % repr(obj))

def __zson_decode(str_):
    #if isinstance(str_, bytes_t):
    #    str_ = str_.decode()
    temp = loads(str_)
    if isinstance(temp, dict) and "__zson_class_name" in temp:
        if temp["__zson_class_name"] == "datetime":
            return datetime.datetime(
                    temp["year"],
                    temp["month"],
                    temp["day"],
                    temp["hour"],
                    temp["minute"],
                    temp["second"],
                    temp["microsecond"]
            )
        else:
            for klass in object.__subclasses__:
                 if klass.__name__ == temp["__zson_class_name"]:
                     candidate = klass
                     break
            else:
                raise Exception("Unknown class <%s> defined in zson object" % temp["__zson_class_name"])
            if not hasattr(candidate, "from_json"):
                raise Exception("%s does not implement from_json" % candidates[0].__name__)
            else:
                del temp["__zson_class_name"]
                return candidate.from_json(temp)
    else:
        return temp


zson_registration_args = (__zson_encode, __zson_decode, 'application/json', 'utf-8')
