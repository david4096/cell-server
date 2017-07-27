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


def _upsert_sample(cursor, sample_id, feature_ids, values):
    """
    Attempt to execute an upsert statement that includes the `values`.

    :param cursor:
    :param sample_id:
    :param feature_ids:
    :param values:
    :return:
    """
    keys = ["expression:{}:{}".format(sample_id, f) for f in feature_ids]
    # add a sample key/value pair
    cursor.sadd("samples", sample_id)
    return _multi_upsert(cursor, keys, values)


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
    for k, sampleId in enumerate(sampleIds):
        _upsert_sample(cursor, sampleId, featureIds, vectors[k])
    return cursor


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
    return [float(x) if x else None for x in iterable]


def _get_safe_float_vector(connection, keys):
    """
    Attempts to get a float vector from the database using a connection and
    list of keys.
    :param connection:
    :param keys:
    :return:
    """
    return _safe_float_vector(connection.mget(*keys))


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
    keys = []
    ret_matrix = []
    for sample_id in sample_ids:
        for feature_id in feature_ids:
            keys.append("expression:{}:{}".format(sample_id, feature_id))
    values = _get_safe_float_vector(connection, keys)
    k = 0
    for sample_id in sample_ids:
        limit = len(feature_ids)
        offset = k * len(feature_ids)
        ret_matrix.append([sample_id] + values[offset:offset+limit])
        k += 1
    return ret_matrix


def _fetchall_keys(cursor):
    """
    A private convenience function that gets the first item from every row
    of a fetch. This is useful for gathering keys of samples and features.
    :param cursor:
    :return: One dimensional list of first value gathered from a cursor.
    """
    return [x[0] for x in cursor.fetchall()]


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
