#!/usr/bin/env python

from thrift.protocol import TBinaryProtocol
from thrift.protocol import TJSONProtocol
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.transport import TTransport
from mapd import MapD
from mapd import ttypes
import time

import numpy as np
import pandas as pd

import pmap

#debug

DEBUG = True

from timeit import default_timer as timer

import sys
from numbers import Number
from collections import Set, Mapping, deque

try: # Python 2
    zero_depth_bases = (basestring, Number, xrange, bytearray)
    iteritems = 'iteritems'
except NameError: # Python 3
    zero_depth_bases = (str, bytes, Number, range, bytearray)
    iteritems = 'items'

class Client(object):
    def __init__(self,
            host="10.50.101.58",
            port=9090,
            http=False,
            user_name="mapd",
            passwd="HyperInteractive",
            db_name="mapd"):
        self._client = self._get_client(host, port, http)
        self._user_name = user_name
        self._passwd = passwd
        self._db_name = db_name
        self._sessions = []

    def _get_results(self, query):
        # TODO intelligently reuse sessions
        session = None
        if len(self._sessions) == 0:
            session = self.get_session()
        else:
            session = sessions[0]
        # TODO expose arguments
        return self._client.sql_execute(session, query, True, None, -1)

    def _get_client(self, host_or_uri, port, http):
      if http:
        transport = THttpClient.THttpClient(host_or_uri)
        protocol = TJSONProtocol.TJSONProtocol(transport)
      else:
        socket = TSocket.TSocket(host_or_uri, port)
        transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
      self._client = MapD.Client(protocol)
      transport.open()
      return self._client

    def get_session(self):
        session = self._client.connect(self._user_name, self._passwd, self._db_name)
        self._sessions.append(session)
        return session

    #https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
    def get_size(obj_0):
        """Recursively iterate to sum size of object & members."""
        def inner(obj, _seen_ids = set()):
            obj_id = id(obj)
            if obj_id in _seen_ids:
                return 0
            _seen_ids.add(obj_id)
            size = sys.getsizeof(obj)
            if isinstance(obj, zero_depth_bases):
                pass # bypass remaining control flow and return
            elif isinstance(obj, (tuple, list, Set, deque)):
                size += sum(inner(i) for i in obj)
            elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
                size += sum(inner(k) + inner(v) for k, v in getattr(obj, iteritems)())
            # Check for custom object instances - may subclass above too
            if hasattr(obj, '__dict__'):
                size += inner(vars(obj))
            if hasattr(obj, '__slots__'): # can have __slots__ with __dict__
                size += sum(inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
            return size
        return inner(obj_0)

    def _get_tuple(self, results, i, j):
        """
        Takes MapD thrift results by row and returns column/value tuples.
        """
        dates = ['TIME', 'TIMESTAMP', 'DATE']
        column_type = ttypes.TDatumType._VALUES_TO_NAMES[
            results.row_set.row_desc[j].col_type.type]
        column_name = results.row_set.row_desc[j].col_name
        column_array = results.row_set.row_desc[j].col_type.is_array
        if not column_array:
            if column_type in ['SMALLINT', 'INT', 'BIGINT', 'TIME', 'TIMESTAMP', 'DATE', 'BOOL']:
                column_value = results.row_set.columns[j].data.int_col[i]
            if column_type in ['FLOAT', 'DECIMAL', 'DOUBLE']:
                column_value = results.row_set.columns[j].data.real_col[i]
            if column_type in ['STR']:
                column_value = results.row_set.columns[j].data.str_col[i]
        else:
            column_value = results.row_set.columns[j].data.arr_col[i].data.str_col
        if column_type in dates:
            value = time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(column_value))
        else:
            value = column_value
        return (column_name, value)

    def _results_to_dataframe(self, results):
        if results.row_set.is_columnar == True:
            number_of_rows = list(range(0, len(results.row_set.columns[0].nulls)))
            #skip the sample column
            number_of_columns = list(range(0, len(results.row_set.row_desc)))
            columns = map(lambda x: self._get_tuple(results, 0, x)[0], number_of_columns)
            rows = map(lambda x: self._get_tuple(results, x, 0)[1], number_of_rows)
            # we remove the sample names from the data as labels
            number_of_columns = number_of_columns[1:]
            # initialize a square matrix of zeros
            matrix = np.zeros((len(results.row_set.columns[0].nulls), len(results.row_set.row_desc)))
            for i in number_of_rows:
                for j in number_of_columns:
                    matrix[i][j] = self._get_tuple(results, i, j)[1]

            return pd.DataFrame(matrix, index=rows, columns=columns)


    def query(self, query):
        start = timer()
        results = self._get_results(query)
        end = timer()
        print(end - start)
        return self._results_to_dataframe(results)

    def disconnect(self):
        for session in self._sessions:
            self._client.disconnect(session)




#https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
def getsize(obj_0):
    """Recursively iterate to sum size of object & members."""
    def inner(obj, _seen_ids = set()):
        obj_id = id(obj)
        if obj_id in _seen_ids:
            return 0
        _seen_ids.add(obj_id)
        size = sys.getsizeof(obj)
        if isinstance(obj, zero_depth_bases):
            pass # bypass remaining control flow and return
        elif isinstance(obj, (tuple, list, Set, deque)):
            size += sum(inner(i) for i in obj)
        elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
            size += sum(inner(k) + inner(v) for k, v in getattr(obj, iteritems)())
        # Check for custom object instances - may subclass above too
        if hasattr(obj, '__dict__'):
            size += inner(vars(obj))
        if hasattr(obj, '__slots__'): # can have __slots__ with __dict__
            size += sum(inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
        return size
    return inner(obj_0)

def main():
    c = Client(
        host="10.50.101.58",
        port="9090",
        http=False,
        db_name="mapd",
        user_name="mapd",
        passwd="HyperInteractive")
    start = timer()
    df = c.query("SELECT ENSMUSG00000095041 from expressions limit 100")
    print(df.describe())
    print(timer() - start)


if __name__ == '__main__':
    main()
