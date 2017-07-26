# <img src="https://github.com/david4096/celldb/blob/master/static/sammy_small.png" align="left"/> celldb <img src="https://img.shields.io/travis/david4096/celldb.svg" />
Database for functional genomics.


```
docker run -itd -p 6379:6379 redis
pip install celldb
jupyter notebook notebooks/getting-started.ipynb
```

## Installation

celldb uses Redis to store functional genomics data. To begin running you'll
need access to a redis instance, or can start one using docker:

`docker run -itd -p 6379:6379 redis`

## Connecting to the server

## Python client

The celldb python client communicates with Phoenix over protocol buffers using
the `phoenixdb` python module. It implements a superset of the DB 2.0 API and
can be used to execute arbitrary SQL easily.

```
import celldb
connection = celldb.connect("http://localhost:8765")
cursor = celldb.initialize(connection)
cursor.execute("SELECT * from Expression")
cursor.fetchall()
```

The client also contains a number of convenience functions. Check out the
[notebooks](https://github.com/david4096/celldb/blob/master/notebooks/python-getting-started.ipynb) for examples of how it can be used.

```
sampleIds = celldb.list_samples(cursor)
featureIds = celldb.list_features(cursor)
matrix = celldb.matrix(cursor, sampleIds, featureIds)
# ('sampleId', Decimal(10.2), Decimal(1.5))
```


## Development

If you'd like to contribute to celldb development there is a lot to be done!
