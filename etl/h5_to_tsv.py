# Graciously adopted from https://github.com/ucscXena/xenaH5
#
# Converts the sparse HDF5 files provided by 10xgenomics into a dense
# representation as TSV. The script is design to be used with a runner
# script and WARNING currently hardcodes values for the number of
# available processes.
#
# Usage
#
# python maketsv.py 0
#
# Will generate a tsv file with the 0th slice of the h5 file named
# `out0.tsv`.

import string, sys
import h5py
import numpy as np

hF = h5py.File("1M_neurons_filtered_gene_bc_matrices_h5.h5")

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

k = int(sys.argv[2])
fout0 = open("columns.tsv", "w")
line = "sample {}".format("\t".join(genes))
fout0.write(line)
fout0.close()

fout = open("out{}.tsv".format(k),'w')

for i in range (k * len(barcodes) / 31, (k + 1) * len(barcodes) / 31):
    barcode = barcodes[i]
    indices_range = indices[indptr[i]:indptr[i+1]]
    data_range = data[indptr[i]:indptr[i+1]]
    values = np.zeros(counter_indptr_size, dtype=int)

    for j in range(0, len(data_range)):
        index = indices_range[j]
        value = data_range[j]
        values[index] = value
    fout.write(barcode+'\t'+string.join(map(lambda x: str(x), values),'\t')+'\n')
fout.close()
