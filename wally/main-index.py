import os
from wally.elastic.index import Index

index = Index()
kuromoji_synonyms = ['京産大, 京都産業大学', '京都大学, 京大']
index.add_mapping_to_index_multi(delete_old_indices=True, kuromoji_synonyms=kuromoji_synonyms)

summary = index.index_bulk_from_dir(os.getcwd())
print("Successfully indexed {0}/{1} emails. Errors on json-convert: {2}, Errors in indexing: {3}".format(
    summary.cnt_success, summary.cnt_total, len(summary.errors_convert), len(summary.errors_index)))
