# This script generates a create table statement from a TSV file that
# includes header information. It is expected that all TSVs have the form:
# sample    f1  f2  f3  f4  ...
#
# Where sample is a column for the sample identifier and f1 are labels for
# each feature column.
#
# usage
# cat mywellformedtsv.tsv | python create_table.py > create_table.sql

import fileinput
import csv

expression_type = "DECIMAL(10)"

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
    if i != len(features) - 1:
        feature_string += ",\n    "
create_string = """CREATE TABLE IF NOT EXISTS expressions (
    sample TEXT ENCODING DICT,
    {});""".format(feature_string)
print(create_string)
