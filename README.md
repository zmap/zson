# ZSON

## Installation

Install the egg as you would any other egg.

```
pip install zson
```
or

```
easy_install zson
```

## Usage 

If you want an object to be JSON decodable, you need to define a to_json instance method that returns a dict of json-encodable objects. If you want your object to be encodable, define a from_json class method that takes back that dictionary. Yes, you can do that recursively and put a json-encodable object in your dict. And that's it. You must also use a newstyle class. It's 2014... if you're not already, you're _actually_ doing something wrong. You also get free json-able datetime objects... because really, it's pretty freaking nonsensicle that this doesn't work out of the box. An example is below if it would help. 

```python

class MyObject(object):

    def __init__(self, name):
        self._name = name

    def to_json(self):
        return {'name':self._name}

    @classmethod
    def from_json(self, obj):
        return cls(obj["name"])

```

## Celery Usage
