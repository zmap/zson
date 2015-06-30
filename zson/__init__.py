import unittest
import datetime
from anyjson import loads, dumps
import json

def __inner_encode(obj, raw=False):
    if isinstance(obj, (str, unicode, int, float, bool, None.__class__)):
        return obj
    elif isinstance(obj, datetime.datetime):
        out = {
            "year":obj.year,
            "month":obj.month,
            "day":obj.day,
            "hour":obj.hour,
            "minute":obj.minute,
            "second":obj.second,
            "microsecond":obj.microsecond
        }
        if not raw:
            out["__zson_class_name"] = "datetime"
    elif isinstance(obj, (list, tuple, set)):
        return list(map(lambda x: __inner_encode(x), obj))
    elif isinstance(obj, dict):
        return dict([(__inner_encode(k), __inner_encode(v)) for k,v in obj.items()])
    elif hasattr(obj, "to_json"):
        d = obj.to_json()
        if d is None and raw:
            return d
        elif d is None:
            d = dict()
        if "__zson_class_name" in d:
             raise Exception("Object is not allowed to define __zson_class_name in to_json")
        if not raw:
             d["__zson_class_name"] = obj.__class__.__name__
        return d
    else:
        raise Exception("unable to encode object %s to json" % repr(obj))


def zson_encode(obj, raw=False):
    return dumps(__inner_encode(obj, raw))

def dict_encode(obj):
    return __inner_encode(obj, True)
   
def zson_decode(str_):
    def __inner_decode(temp):
        if isinstance(temp, (list, tuple, set)):
            return list(map(lambda x: __inner_decode(x), temp))
        elif isinstance(temp, dict) and "__zson_class_name" in temp:
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
                def iter_classes(kls):
                    try:
                        for klass in kls.__subclasses__():
                            for klass2 in iter_classes(klass):
                                yield klass2
                    except TypeError:
                        try:
                            for klass in kls.__subclasses__(kls):
                                for klass2 in iter_classes(klass):
                                    yield klass2
                        except:
                            pass
                    yield kls   
                for klass in iter_classes(object):
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
        elif isinstance(temp, dict):
            return dict([(k, __inner_decode(v)) for k,v in temp.items()])
        else: 
            return temp
    if str_ == "None":
        return None
    elif isinstance(str_, dict):
        return __inner_decode(str_)
    else:
        return __inner_decode(loads(str_))


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

    class Foo(object):
        def __init__(self, name):
            self.name = name

        def to_json(self): 
            return dict(name=self.name)

        @classmethod
        def from_json(cls, v):
            return cls(v["name"])

        def __eq__(self, other): 
            return self.__class__ == other.__class__ \
                    and self.name == other.name
 
    def testObject(self):
        v = self.Foo("test123")
        self.assertEqual(v, zson_decode(zson_encode(v)))

    def testListObject(self):
        v = [self.Foo("test123"), self.Foo("asdf")]
        self.assertEqual(v, zson_decode(zson_encode(v)))

    def testDictObject(self):
        v = {"a":self.Foo("test123"), "b":self.Foo("asdf")}
        self.assertEqual(v, zson_decode(zson_encode(v)))

    def testRawEncode(self):
        x = {'a':1, 'b':2, 'c': "x"}
        class IsAClass(object):

            def to_json(self):
                return x

        v = IsAClass()
        self.assertEqual(json.dumps(x), zson_encode(v, raw=True))
        class EdgeCase(object):
            def to_json(self):
                return None
        z = EdgeCase()
        self.assertEqual('null', zson_encode(z, raw=True))

    def testCeleryRealistic(self):
        # taken from celery except tuples converted into lists
        # given that this happens according to default python
        # JSON behavior
        v = {
            'expires': None, 'utc': True,
            'args': [self.Foo("asdf"),self.Foo("abcd")],
            'chord': None, 'callbacks': None, 'errbacks': None,
            'taskset': None, 'id': 'd04caa97-4a5e-43e8-88cc-9f8e6c3ce4af',
            'retries': 0, 'task': 'get-system-information',
            'timelimit': [None, None], 'eta': None,
            'kwargs': {"a":self.Foo("test123"), "b":self.Foo("asdf")}
        }
        self.assertEqual(v, zson_decode(zson_encode(v)))


if __name__ == "__main__":
    unittest.main()


