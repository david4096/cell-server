# Requires having a running phoenix instance
#
# These tests modify the database and so caution should be made when attempting
# to parallelize.

from celldb.client import client as celldb

import random
import time

URL = "localhost"

# We will try to sneak a regression test into our integration test by placing
# lower bounds on the acceptable response time from phoenix. By constraining
# these timeouts we can put bounds on the performance of working with data
# of various shapes.


def _random_dataset(n_samples=10, n_features=10):
    """
    Generates a random dataset by returning a tuple of sampleIds, featureIds,
    and a list of vectors based on input parameters.
    :param n_samples:
    :param n_features:
    :return: (sampleIds, featureIds, vectors) tuple
    """
    sampleIds = ["sample_{}".format(x) for x in range(n_samples)]
    featureIds = ["feature_{}".format(x) for x in range(n_features)]
    vectors = [
        [random.random() for x in range(len(featureIds))]
        for x in range(len(sampleIds))]
    return sampleIds, featureIds, vectors


def _drop_tables(cursor):
    # try:
    #     cursor.execute("DROP TABLE Expressions")
    #     cursor.execute("DROP TABLE Features")
    # except:
    #     print("Tables already existed, nothing to do")
    cursor.flushall()
    return cursor


class TestIntegrationSimple:
    @classmethod
    def setup_class(cls):
        connection = celldb.connect(URL)
        cursor = connection
        _drop_tables(cursor)

    @classmethod
    def teardown_class(cls):
        cursor = celldb.connect(URL)
        _drop_tables(cursor)

    def test_connect(self):
        """
        Attempts a connection to the database.
        :return:
        """
        assert celldb.connect(URL) is not None

    def test_good_upsert_sample(self):
        cursor = celldb.connect(URL)
        sampleId = "test_sample"
        featureId = "test_feature"
        value = 2.7127
        celldb.upsert_sample(cursor, sampleId, [featureId], [value])
        print(list(celldb.list_samples(cursor)))
        assert list(celldb.list_samples(cursor)) == [sampleId]
        assert list(celldb.list_features(cursor)) == [featureId]


class TestUpsertSamples:
    @classmethod
    def setup_class(cls):
        connection = celldb.connect(URL)
        cursor = connection
        _drop_tables(cursor)

    @classmethod
    def teardown_class(cls):
        cursor = celldb.connect(URL)
        _drop_tables(cursor)

    def test_connect(self):
        """
        Attempts a connection to the database.
        :return:
        """
        assert celldb.connect(URL) is not None

    def test_upsert_samples(self):
        cursor = celldb.connect(URL)
        sample_ids = ["sample_{}".format(x) for x in range(20)]
        feature_ids = ["feature_{}".format(x) for x in range(10)]
        vectors = [
            [random.random() for x in range(len(feature_ids))]
            for x in range(len(sample_ids))]
        celldb.upsert_samples(cursor, sample_ids, feature_ids, vectors)
        assert set(celldb.list_samples(cursor)) == set(sample_ids)
        assert set(celldb.list_features(cursor)) == set(feature_ids)

    def test_upsert_tuple(self):
        """
        Checks to make sure that the client accepts both tuples and lists.
        :return:
        """
        connection = celldb.connect(URL)
        celldb.upsert_samples(
            connection, ('sample_tuple',), ('feature_tuple',), ((0.1,),))


class TestUpsertTimes:
    """
    These tests attempt to demonstrate baseline performance expectations for
    vectors of varying size. These figures are not meant to present practical
    performance measurements, but instead the minimum expected under CI.
    """
    @classmethod
    def setup_class(cls):
        connection = celldb.connect(URL)
        cursor = connection
        _drop_tables(cursor)

    @classmethod
    def teardown_class(cls):
        cursor = celldb.connect(URL)
        _drop_tables(cursor)

    def test_upsert_10_wide(self):
        cursor = celldb.connect(URL)
        per_sample = 0.01   # set the minimum threshold of time per sample
        n_samples = 1000
        n_features = 10
        sampleIds, featureIds, vectors = _random_dataset(n_samples, n_features)
        start = time.time()
        celldb.upsert_samples(cursor, sampleIds, featureIds, vectors)
        end = time.time()
        assert (end - start) / float(n_samples) < per_sample

    def test_upsert_100_wide(self):
        cursor = celldb.connect(URL)
        per_sample = 0.1   # set the minimum threshold of time per sample
        n_samples = 1000
        n_features = 100
        sampleIds, featureIds, vectors = _random_dataset(n_samples, n_features)
        start = time.time()
        celldb.upsert_samples(cursor, sampleIds, featureIds, vectors)
        end = time.time()
        assert (end - start) / float(n_samples) < per_sample

    def test_upsert_1000_wide(self):
        cursor = celldb.connect(URL)
        per_sample = 0.1   # set the minimum threshold of time per sample
        n_samples = 100
        n_features = 1000
        sampleIds, featureIds, vectors = _random_dataset(n_samples, n_features)
        start = time.time()
        celldb.upsert_samples(cursor, sampleIds, featureIds, vectors)
        end = time.time()
        assert (end - start) / float(n_samples) < per_sample

    def test_upsert_10000_wide(self):
        cursor = celldb.connect(URL)
        per_sample = 10   # set the minimum threshold of time per sample
        n_samples = 10
        n_features = 10000
        sampleIds, featureIds, vectors = _random_dataset(n_samples, n_features)
        start = time.time()
        celldb.upsert_samples(cursor, sampleIds, featureIds, vectors)
        end = time.time()
        assert (end - start) / float(n_samples) < per_sample

    def test_upsert_100000_wide(self):
        cursor = celldb.connect(URL)
        per_sample = 200   # set the minimum threshold of time per sample
        n_samples = 1
        n_features = 100000
        sampleIds, featureIds, vectors = _random_dataset(n_samples, n_features)
        start = time.time()
        celldb.upsert_samples(cursor, sampleIds, featureIds, vectors)
        end = time.time()
        assert (end - start) / float(n_samples) < per_sample

    def test_list_many(self):
        """
        Makes sure both upsert and list happen in appropriate time
        :return:
        """
        connection = celldb.connect(URL)
        _drop_tables(connection)
        list_time = 30
        per_sample = 1
        n_samples = 10000
        n_features = 10
        sample_ids, feature_ids, vectors = _random_dataset(
            n_samples, n_features)
        start = time.time()
        celldb.upsert_samples(connection, sample_ids, feature_ids, vectors)
        end = time.time()
        assert (end - start) / float(n_samples) < per_sample
        start = time.time()
        sample_list = list(celldb.list_samples(connection))
        end = time.time()
        assert (end - start) < list_time
        assert len(sample_list) == len(sample_ids)


class TestMatrix:
    """
    These tests attempt an upsert and then demonstrate the functionality
    of the "matrix" query function.
    :return:
    """
    @classmethod
    def setup_class(cls):
        connection = celldb.connect(URL)
        cursor = connection
        _drop_tables(cursor)

    @classmethod
    def teardown_class(cls):
        cursor = celldb.connect(URL)
        _drop_tables(cursor)

    def test_matrix(self):
        cursor = celldb.connect(URL)
        sampleIds, featureIds, vectors = _random_dataset(4, 4)
        celldb.upsert_samples(cursor, sampleIds, featureIds, vectors)
        matrix = celldb.matrix(cursor, sampleIds, featureIds)
        for k, row in enumerate(matrix):
            assert row[0] == sampleIds[k]
            assert len(row) == len(featureIds) + 1
            for i, value in enumerate(row[1:]):
                assert value == vectors[k][i]
        assert len(matrix) == len(sampleIds)
        _drop_tables(cursor)

    def test_singleton_matrix(self):
        """
        Tests to make sure a single sample doesn't throw an exception and
        returns the expected results.
        :return:
        """
        connection = celldb.connect(URL)
        sampleIds, featureIds, vectors = _random_dataset(1, 4)
        celldb.upsert_samples(connection, sampleIds, featureIds, vectors)
        sample_ids = celldb.list_samples(connection)
        assert list(sample_ids)[0] == sampleIds[0]
        feature_ids = celldb.list_features(connection)
        assert len(featureIds) == len(list(feature_ids))
        matrix = celldb.matrix(connection, sampleIds, featureIds)
        for k, row in enumerate(matrix):
            assert row[0] == sampleIds[k]
            # The row has the sample_id in the first position
            assert len(row) == len(featureIds) + 1
            for i, value in enumerate(row[1:]):
                assert value == vectors[k][i]
        _drop_tables(connection)

    def test_single_feature_matrix(self):
        """
        Tests to make sure that making a single feature is upserted as
        expected and that retrieving the resulting matrix doesn't error.
        :return:
        """
        connection = celldb.connect(URL)
        sampleIds, featureIds, vectors = _random_dataset(1, 4)
        celldb.upsert_samples(connection, sampleIds, featureIds, vectors)
        feature_ids = celldb.list_features(connection)
        assert set(feature_ids) == set(featureIds)
        _drop_tables(connection)

    def test_large_matrix(self):
        """
        Tests to make sure that when request a large matrix we get satisfactory
        results.

        :return:
        """
        connection = celldb.connect(URL)
        #  The amount of time in seconds per point we're willing to accept
        per_point = 0.01
        n_samples = 10000
        n_features = 40
        points = float(n_samples * n_features)
        sampleIds, featureIds, vectors = _random_dataset(10000, 40)
        celldb.upsert_samples(connection, sampleIds, featureIds, vectors)
        start = time.time()
        matrix = celldb.matrix(connection, sampleIds, featureIds)
        assert len(matrix) == len(sampleIds)
        end = time.time()
        assert (end - start) / points < per_point


class TestSparseMatrix:
    """
    These tests attempt an upsert and then demonstrate the functionality
    of the "sparse_matrix" query function.
    :return:
    """
    @classmethod
    def setup_class(cls):
        connection = celldb.connect(URL)
        cursor = connection
        _drop_tables(cursor)

    @classmethod
    def teardown_class(cls):
        cursor = celldb.connect(URL)
        _drop_tables(cursor)

    def test_sparse_matrix(self):
        cursor = celldb.connect(URL)
        sample_ids, feature_ids, vectors = _random_dataset(4, 4)
        celldb.upsert_samples(cursor, sample_ids, feature_ids, vectors)
        matrix = celldb.sparse_matrix(cursor, sample_ids, feature_ids)
        # The sparse matrix has the list of samples and features at the top
        # level for convenience. These become indices into the `values` map.
        assert len(matrix['sample_ids']) == len(sample_ids)
        assert len(matrix['feature_ids']) == len(feature_ids)

        for k, v in enumerate(matrix['values']):
            assert vectors[int(k)][int(v)] == vectors[int(k)][int(v)]
        _drop_tables(cursor)
