# -*- coding: utf-8 -*-
import os
from wally.elastic.index import Index

idx = Index()

idx.add_mapping_to_index_multi()

inDir = 'data_in'
basepath = os.getcwd()
inPath = os.path.join(basepath, inDir)
cnt = 0
cntErr = 0
for filename in os.listdir(inPath):
    if cnt % 1000 == 0:
        print(cnt)
    if os.path.isdir(os.path.join(inPath, filename)):
        continue
    mail = filename
    filepath = os.path.join(basepath, inDir, mail).replace('\\', '/')
    cntErr += idx.index_from_file(filepath)
    cnt += 1

print("Successfully indexed {0}/{1} emails".format(cnt - cntErr, cnt))