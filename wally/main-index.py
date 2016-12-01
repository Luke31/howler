import os
from wally.elastic.index import Index

index = Index()
index.add_mapping_to_index_multi(delete_old_indices=True)

summary = index.index_bulk_from_dir(os.getcwd())
print("Successfully indexed {0}/{1} emails. Errors on json-convert: {2}, Errors in indexing: {3}".format(
    summary.cnt_success, summary.cnt_total, len(summary.errors_convert), len(summary.errors_index)))
