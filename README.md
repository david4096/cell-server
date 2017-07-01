# <img src="https://github.com/david4096/celldb/blob/master/static/sammy_small.png" align="left"/> celldb <img src="https://img.shields.io/travis/david4096/celldb.svg" />
Database for functional genomics.


```
docker run -itd -p 8765:8765 david4096/docker-phoenix
pip install https://github.com/david4096/celldb.git@master
jupyter notebook notebooks/getting-started.ipynb
```

## Installation

celldb uses the Phoenix adapter over HBase to enable SQL queries over sparse
data at scale. However, not everyone has a Hadoop cluster lying around and so
you can use the [docker-phoenix](https://https://github.com/david4096/docker-phoenix) image
for your experimentation.

`docker run -it -p 8765:8765 david4096/docker-phoenix`

## Connecting to the server

There are two interfaces available for executing SQL queries. A JDBC interface
allows one to connect legacy systems to the server easily, and Spark dataframes
provide an interface for performing analysis at scale.

### Python client

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
import pandas as pd
sql = celldb.matrix_sql(samples, features)
df = pd.read_sql(sql, connection, index_col="SAMPLEID")
df.describe()
```

### Spark Client

Data can be accessed using the Spark dataframes interface. This allows
map-reduce jobs to push down to Phoenix SQL to create a comfortable interface
for performing analysis at scale.

```
df = sqlContext.read \
  .format("org.apache.phoenix.spark") \
  .option("table", "TABLE1") \
  .option("zkUrl", "localhost:2181") \
  .load()
```

https://phoenix.apache.org/phoenix_spark.html

## Data Model

The cell server aims to organize functional genomics data for rapid genomic
analysis by focusing on the problems of handling RNA expression vectors. It
stores expressions, that are indexed row-wise by sample and column-wise by gene.

This makes it easy to construct requests for subsets of genes that span some,
or all of the samples:

```

select gene1, gene2, gene3, gene4 from expressions;

```

Since the value for each expression is stored as a precision decimal value,
we can constrain our results to rows that have expressed a gene of interest:

```

select gene1, gene2, gene3 from expressions where gene1 > 0.5

```

In this way, the `expressions` table provides the primary interface for acting
on data in the celldb. It is expected that phenotypic data, and metadata
regarding features will be gathered through other databases and services.

#### Tables

##### features

To facilitate rudimentary analysis, each sample is expected to use the latest
reference gencode genes (FIXME is another approach plausible?). This table is
called `features` and provides a way for constructing lists of features to use
in a query. Each row of the `features` table contains only an index to that
feature's position in the `expressions` table.

```

select * from features limit 10;

0|ENST123
1|ENST125
2|ENST512
3|ENST631

```

##### expressions

Expression vectors are added to this table row wise. Each row contains a sample
identifier, and a column for each feature that contains a precision decimal
value representing that sample's expression.

```

select sample, ENST123 from expressions limit 1;

sample1|0.0

```

* may need to change to include an array or blob column that contains the whole
vector to ease recreating the whole feature vector (not if we use a sparse
representation)

## Development

If you'd like to contribute to celldb development there is a lot to be done!
