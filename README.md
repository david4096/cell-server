# <img src="https://github.com/david4096/cell-server/blob/master/static/sammy_small.png" align="left"/> cell-server 
Database for functional genomics



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
on data in the cell-server. It is expected that phenotypic data, and metadata
regarding features will be gathered through other databases and services.

### Tables

### features

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

### expressions

After normalizing to the expected feature-space, expression vectors are added
to this table row wise. Each row contains a sample identifier, and a column
for each feature that contains a precision decimal value representing that
sample's expression.

```

select sample, ENST123 from expressions limit 1;

sample1|0.0

```

* may need to change to include an array or blob column that contains the whole
vector to ease recreating the whole feature vector
