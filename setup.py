from setuptools import setup

setup(
    name = "zson",
    description = "A JSON serializer for Kombu (and therefore also Celery) that supports encoding objects by defining to_json and from_json methods.",
    version = "1.0.11",
    license = "Apache License, Version 2.0",
    author = "Zakir Durumeric",
    author_email = "zakird@gmail.com",
    maintainer = "Zakir Durumeric",
    maintainer_email = "zakird@gmail.com",

    keywords = "python kombu celery json",

    packages = [
        "zson"
    ],

    entry_points={
	'kombu.serializers': [
            'zson = zson:zson_registration_args'
        ]
    }
)
