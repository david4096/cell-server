# This script generates a copy table statement that can be used to load data.
#
# Usage
#
# python tabletocopyto mytsv.tsv
#
import sys
# TODO needs to point to absolute path
print("COPY {} FROM '{}' [WITH (delimiter = '\t', header = 'false')];".format(sys.argv[1], sys.argv[2]))
