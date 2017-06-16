# This script starts a number of forked processes to generate TSV files.
#
# Usage
#
# python run_h5_to_tsv.py h5file 0
#
# Where 0 is the slice that will be converted into a CSV.

import os, sys
os.system("python " + os.path.dirname(os.path.realpath(__file__)) + "/make_feature_tsv_from_h5.py {}&".format(sys.argv[1]))
os.system("cat columns.tsv | python " + os.path.dirname(os.path.realpath(__file__)) + "/create_feature_table.py {}&".format(sys.argv[1]))

for k in range(0, 31):
     os.system("python " + os.path.dirname(os.path.realpath(__file__)) + "/h5_to_tsv.py {} {}&".format(sys.argv[1], k))
