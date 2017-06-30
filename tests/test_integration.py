# Requires having a running phoenix instance
#
# These tests modify the database and so caution should be made when attempting
# to parallelize.

URL = "http://localhost:8765"

import celldb

def _drop_tables(cursor):
    try:
        cursor.execute("DROP TABLE Expressions")
        cursor.execute("DROP TABLE Features")
    except Exception as e:
        print("Tables already existed, nothing to do")
    return cursor


class TestIntegration:
    @classmethod
    def setup_class(cls):
        connection = celldb.connect(URL)
        cursor = connection.cursor()
        _drop_tables(cursor)
        celldb.initialize(connection)

    @classmethod
    def teardown_class(cls):
        cursor = celldb.connect(URL).cursor()
        _drop_tables(cursor)


    def test_connect(self):
        """
        Attempts a connection to the database.
        :return:
        """
        assert celldb.connect(URL) is not None

    def test_good_upsert_sample(self):
        cursor = celldb.connect(URL).cursor()
        sampleId = "test_sample"
        featureId = "test_feature"
        value = 2.7127
        celldb.upsert_sample(cursor, sampleId, [featureId], [value])
        assert celldb.list_samples(cursor) == [sampleId]
        assert celldb.list_features(cursor) == [featureId]
        