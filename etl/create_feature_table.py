# This script generates a create table statement
# for all of the feature columns of a TSV.
#
# This table is useful for creating select statements.
#
# usage
# cat mywellformedtsv.tsv | python create_feature_table.py > create_feature_table.sql

create_string = """
CREATE TABLE IF NOT EXISTS features (
    index INT,
    feature TEXT ENCODING DICT,
    name TEXT ENCODING DICT)"""

print(create_string)
