# This script generates a create table statement
# for all of the feature columns of a TSV.
#
# This table is useful for creating select statements.
#
# usage
# cat mywellformedtsv.tsv | python create_feature_table.py > create_feature_table.sql

import fileinput
import csv

csv_reader = csv.reader(
    fileinput.input(),
    delimiter='\t')
features = []
for i, row in enumerate(csv_reader):
    if i == 0:
        features = row[1:]
        break
def feature_sql_string(feature):
    # to lower, replace illegal char
    normalized_feature = feature.replace('.', '_')
    return "{} {}".format(normalized_feature, expression_type)

feature_string = ""
for i, feature in enumerate(features):
    feature_string += feature_sql_string(feature)
    print("{}\t{}").format(i, feature.replace('.', '_'))
create_string = """
CREATE TABLE IF NOT EXISTS features (
    index INT,
    name TEXT ENCODING DICT)"""
