# Graciously adopted from https://github.com/ucscXena/xenaH5
#
# Generates a tsv compatible for making a create table statement from a
# 10xgenomics HDF5 file.
#
# Usage
#
# python maketsv.py fname 0
#
# Will generate a tsv file with the 0th slice of the h5 file named
# `out0.tsv`.

import string, sys
import h5py
import numpy as np

hF = h5py.File(sys.argv[1])

group = "mm10"
indptr = hF[group +"/indptr"]
indices = hF[group + "/indices"]
data = hF[group + "/data"]
genes = hF[group + "/genes"]
gene_names = hF[group + "/gene_names"]
barcodes = hF[group + "/barcodes"]
shape = hF[group + "/shape"]
rowN = shape[0]
colN = shape[1]
counter_indptr_size = rowN

fout0 = open("columns.tsv", "w")
line = "sample\t{}".format("\t".join(genes))
fout0.write(line)
fout0.close()

fout = open("features.tsv",'w')
fout.write("index\tfeature\tfeature_name\n")
for i in range (0, len(genes)):
    fout.write("{}\t{}\t{}\n".format(i, genes[i], gene_names[i]))
