#!/usr/bin/env python

from thrift.protocol import TBinaryProtocol
from thrift.protocol import TJSONProtocol
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.transport import TTransport
from mapd import MapD
from mapd import ttypes
import time

'''
Contact support@mapd.com with any questions

Python 2.x instructions (with fix for recursive data structs)
pip install redbaron
pip install thrift
thrift -gen py mapd.thrift
mv gen-py/mapd/ttypes.py gen-py/mapd/ttypes-backup.py
python fix_recursive_structs.py gen-py/mapd/ttypes-backup.py gen-py/mapd/ttypes.py
export PYTHONPATH=/path/to/mapd2-1.x-gen-py:$PYTHONPATH

Python 3.x instructions (manual build of latest Thrift)
sudo apt-get install build-essential
git clone https://git-wip-us.apache.org/repos/asf/thrift.git
cd thrift/lib/py
pip install .
thrift -gen py mapd.thrift
export PYTHONPATH=/path/to/mapd2-1.x-gen-py:$PYTHONPATH

Example:
python MapDExample.py

Connection samples:
HTTP client - get_client('http://test.mapd.com:9091', portno, True)
Binary protocol - get_client('locahost', 9091, False)
'''


def get_client(host_or_uri, port, http):
  if http:
    transport = THttpClient.THttpClient(host_or_uri)
    protocol = TJSONProtocol.TJSONProtocol(transport)
  else:
    socket = TSocket.TSocket(host_or_uri, port)
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

  client = MapD.Client(protocol)
  transport.open()
  return client


def main():

    db_name = 'mapd'
    user_name = 'mapd'
    passwd = 'HyperInteractive'
    hostname = '10.50.101.58'
    portno = 9091

    client = get_client(hostname, portno, False)
    session = client.connect(user_name, passwd, db_name)
    print 'Connection complete'
    query = ""
    with open('./maketable.sql', 'r') as myfile:
        query += myfile.read().replace('\n', '')
    #query = "select sample, ENSG00000269752_1, ENSGR0000277120_4 from expressions"
    print 'Query is : ' + query

    # always use True for is columnar
    results = client.sql_execute(session, query, True, None, -1)
    dates = ['TIME', 'TIMESTAMP', 'DATE']

    if results.row_set.is_columnar == True:
        number_of_rows = list(range(0, len(results.row_set.columns[0].nulls)))
        number_of_columns = list(range(0, len(results.row_set.row_desc)))
        samples = {}
        for n in number_of_rows:
            row = {}
            for i in number_of_columns:
                column_type = ttypes.TDatumType._VALUES_TO_NAMES[
                    results.row_set.row_desc[i].col_type.type]
                column_name = results.row_set.row_desc[i].col_name
                column_array = results.row_set.row_desc[i].col_type.is_array
                if not column_array:
                    if column_type in ['SMALLINT', 'INT', 'BIGINT', 'TIME', 'TIMESTAMP', 'DATE', 'BOOL']:
                        column_value = results.row_set.columns[i].data.int_col[n]
                    if column_type in ['FLOAT', 'DECIMAL', 'DOUBLE']:
                        column_value = results.row_set.columns[i].data.real_col[n]
                    if column_type in ['STR']:
                        column_value = results.row_set.columns[i].data.str_col[n]
                else:
                    column_value = results.row_set.columns[i].data.arr_col[n].data.str_col
                print(column_name)
                if column_type in dates:
                    print(time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.localtime(column_value)))
                else:
                    print(column_value)
                    row[column_name] = column_value
            samples[row['sample']] = row



    else:
        print('Please use columns not rows in query execution')
        client.disconnect(session)
        quit()

    csv_string = ""
    feature_list = samples[samples.keys()[0]].keys()
    feature_list_string = ""
    for i, feature in enumerate(feature_list):
        if feature != "sample":
            feature_list_string += feature
        if i != len(feature_list) - 1:
            feature_list_string += ", "
    print("sample, {}")
    for i, sample in enumerate(samples):
        string = ""
        print(sample)
        for feature in feature_list:
            string += sample[feature]
        if i != len(samples) - 1:
            string += "\t"
        print(string)
    client.disconnect(session)


if __name__ == '__main__':
    main()
