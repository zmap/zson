import unittest
import datetime
from anyjson import loads, dumps

def zson_encode(obj):
    def __inner_encode(obj):
        if isinstance(obj, (str, int, float, bool, dict, None.__class__)):
            return obj
        elif isinstance(obj, datetime.datetime):
            return {
                "__zson_class_name":"datetime",
                "year":obj.year,
                "month":obj.month,
                "day":obj.day,
                "hour":obj.hour,
                "minute":obj.minute,
                "second":obj.second,
                "microsecond":obj.microsecond
            }
        elif isinstance(obj, (list, tuple, set)):
            return list(map(lambda x: __inner_encode(x), obj))
        elif isinstance(obj, dict):
            return dict([(__inner_encode(k), __inner_encode(v)) for k,v in obj.items()])
        elif hasattr(obj, "to_json"):
            d = obj.to_json()
            if "__zson_class_name" in d:
                 raise Exception("Object is not allowed to define __zson_class_name in to_json")
            d["__zson_class_name"] = obj.__class__.__name__
            return d
        else:
            raise Exception("unable to encode object %s to json" % repr(obj))

    return dumps(__inner_encode(obj))
   
def zson_decode(str_):
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
            for klass in object.__subclasses__():
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


zson_registration_args = (zson_encode, zson_decode, 'application/zson', 'utf-8')

class ZsonTestCase(unittest.TestCase):
    def testString(self):
        v = "string"
        self.assertEqual(zson_encode(v), dumps(v))
        self.assertEqual(v, loads(dumps(v)))
        self.assertEqual(v, zson_decode(zson_encode(v)))

    def testList(self):
        v = [1, 1.0, "test", False, None]
        self.assertEqual(zson_encode(v), dumps(v))
        self.assertEqual(v, loads(dumps(v)))
        self.assertEqual(v, zson_decode(zson_encode(v)))

    def testDict(self):
        v = {"key1": "value", "key3":False, "key2":None} 
        self.assertEqual(zson_encode(v), dumps(v))
        self.assertEqual(v, loads(dumps(v)))
        self.assertEqual(v, zson_decode(zson_encode(v)))

    def testNested(self):
        v = {
            "key1": ["a", False, None, 1.0],
            "key2": {
                "subkey1": ["a", "b", "c"],
                "key3": {"test1": "test2"}
            }
        }
        self.assertEqual(zson_encode(v), dumps(v))
        self.assertEqual(v, loads(dumps(v)))
        self.assertEqual(v, zson_decode(zson_encode(v)))

    def testObject(self):
        class Foo(object):
            def __init__(self, name):
                self.name = name

            def to_json(self): 
                return dict(name=self.name)

            @classmethod
            def from_json(cls, v):
                return cls(v["name"])

            def __eq__(self, other): 
                return self.name == other.name

        v = Foo("test123")
        self.assertEqual(v, zson_decode(zson_encode(v)))


if __name__ == "__main__":
    unittest.main()


