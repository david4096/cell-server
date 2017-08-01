#!/usr/bin/env python
# celldb
#
import redis


def _upsert_feature(cursor, feature_id):
    """
    Attempts to upsert a row in Features table.
    :param cursor:
    :return:
    """
    return cursor.sadd("features", feature_id)


def _multi_upsert(cursor, keys, values):
    """
    Takes a dictionary of key:value pairs and upserts them using a multiset.
    :param cursor:
    :param upsert_dict:
    :return:
    """
    upsert_dict = dict(zip(keys, values))
    return cursor.mset(upsert_dict)


def _multi_hash_upsert(cursor, key, keys, values):
    """
    Upserts a set of hash values at the given key by combining the keys
    and values arguments into a dictionary and performing hmset.
    :param cursor:
    :param key:
    :param keys:
    :param values:
    :return:
    """
    return cursor.hmset(key, dict(zip(keys, values)))


def _upsert_sample(cursor, sample_id, feature_ids, values):
    """
    Attempt to execute an upsert statement that includes the `values`.

    :param cursor:
    :param sample_id:
    :param feature_ids:
    :param values:
    :return:
    """
    # add a sample key/value pair
    cursor.sadd("samples", sample_id)
    return _multi_hash_upsert(cursor, sample_id, feature_ids, values)


def _upsert_features(cursor, feature_ids):
    """
    Attempts to upsert a featureId row for every featureId.
    :param cursor:
    :param featureIds:
    :return:
    """
    # Consider creating the transposed table here as well in Features
    # to easily find the samples associated with a given key. In this case
    # we simply upsert the key for every feature.
    return cursor.sadd("features", *feature_ids)


def upsert_sample(cursor, sampleId, featureIds, values, upsert_features=True):
    """
    Attempts to add a sample using dynamic columns. The list of features do
    not need to be present in the database.
    :param cursor:
    :param sampleId:    A string that will uniquely identify the Sample.
    :param featureIds:  A list of `featureId` strings that uniquely identify
                        the feature and retains the order of the `values`
                        argument.
    :param values:      A list of numeric values retaining the order of the
                        `featureIds` argument.
    :return cursor:
    """
    _upsert_sample(cursor, sampleId, featureIds, values)
    if upsert_features:
        _upsert_features(cursor, featureIds)
    return cursor


def upsert_samples(cursor, sampleIds, featureIds, vectors):
    """
    Attempts to upsert a list of expression vectors ordered by the list of
    sampleIds and featureIds provided.
    :param cursor:
    :param sampleIds:
    :param featureIds:
    :param vectors:
    :return:
    """
    _upsert_features(cursor, featureIds)
    return map(
            lambda (k, x): _upsert_sample(cursor, x, featureIds, vectors[k]),
            enumerate(sampleIds))


def connect(url, **kwargs):
    """
    A loose layer over phoenixdb's connect method.
    :param url:
    :return:
    """
    return redis.StrictRedis(host=url, port=6379, db=0)


def list_features(cursor):
    """
    A convenience function for accessing the list of featureIds from the
    Features table.
    :param cursor:
    :return:
    """
    # We set our count to be excessively high to optimize listing of all of
    # the features at once. Providing this via the client might be nice.
    # number of transcripts ~ 200k
    return cursor.sscan_iter("features", count=200000)


def list_samples(cursor):
    """
    A convenience function for accessing the list of sampleIds from the
    Samples table.
    :param cursor:
    :return:
    """

    return cursor.sscan_iter("samples", count=5000)


def _string_to_float(string_list):
    """
    Converts a list of string values to float values.
    :param string_list:
    :return:
    """
    return map(float, string_list)


def _safe_float_vector(iterable):
    """
    Takes an iterable and returns a vector of floats. Respects the null
    return value.
    :param iterable:
    :return:
    """
    # FIXME workaround in client to deal with data ingestion problem
    return [float(x) if x and x != 'NA' else None for x in iterable]


def _get_safe_float_vector(connection, keys):
    """
    Attempts to get a float vector from the database using a connection and
    list of keys.
    :param connection:
    :param keys:
    :return:
    """
    return _safe_float_vector(connection.mget(*keys))


def _build_matrix_row(connection, sample_id, feature_ids):
    """
    Takes a sample_id to build a row of the matrix.

    :param connection:
    :param sample_id:
    :param feature_ids:
    :return:
    """
    vector = _safe_float_vector(connection.hmget(sample_id, feature_ids))
    return [sample_id] + vector


def matrix(connection, sample_ids, feature_ids):
    """
    A convenience function for gathering matrices of expression data from the
    expressions table.
    :param cursor:
    :param sampleIds:   A list of `sampleId` strings for which one would like
                        expression data.
    :param featureIds:  A list of featureId strings for which one would like
                        expression data.
    :return:
    """
    return map(
        lambda x: _build_matrix_row(connection, x, feature_ids), sample_ids)


def _safe_fn(fn, *args):
    """
    A catch all higher order function for general exception handling.
    :param fn:
    :param args:
    :return:
    """
    ret = None
    try:
        ret = fn(*args)
    except Exception as e:
        print(e)
    return ret
