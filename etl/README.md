# Extract / Transform / Load

This directory assembles the scripts needed to process data from a few sources
into the cell-server data model.

For 10xgenomics h5:

1) Copy HDF5 local
2) run_h5_to_tsv to generate both the features.tsv and to spawn processes that
will make out*.tsv to be added to the database.
3) Create feature table will generate a create table statement from the
features.tsv. Run this
4) create_table on 0.tsv which is a one line TSV that simply has the columns.
Run this statement
5) Create copy from statements for each of the out*.tsv files and run them.
