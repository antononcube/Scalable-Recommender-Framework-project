import pandas
import time
import timeit
import pickle

from SparseMatrixRecommender.SparseMatrixRecommender import *
from SparseMatrixRecommender.DataLoaders import *
from SSparseMatrix import *

print("\n")

tstart = time.time()

dfSMRMatrix = pandas.read_csv("../Data/ZefEcosystem-dfSMRMatrix.csv.gz", compression='gzip')

tend = time.time()
print("\t\tTime to load CSV data : ", tend - tstart)
print(dfSMRMatrix.shape)

# ========================================================================================================================
print("=" * 120)

tstart = time.time()

smrObj = (SparseMatrixRecommender()
          .create_from_long_form(data=dfSMRMatrix,
                                 item_column_name="Item",
                                 tag_type_column_name="TagType",
                                 tag_column_name="Tag",
                                 weight_column_name="Weight",
                                 add_tag_types_to_column_names=False,
                                 tag_value_separator=":")
          .apply_term_weight_functions(global_weight_func="None",
                                       local_weight_func="None",
                                       normalizer_func="Cosine"))

print("\t\tSMR creation time : " + str(time.time() - tstart))

# ========================================================================================================================
print("=" * 120)

print(repr(smrObj))

print(smrObj)

# ========================================================================================================================
print("=" * 120)

print("\t\tProfile recommendations:")

nTimes = 1000
tstart = time.time()

prof = ["Tag:cli",
        "Tag:model",
        "Dependence:json::fast",
        "Word:sql",
        "Word:math"]

prof = list(set.intersection(set(prof), set(smrObj.take_M().column_names())))
print(prof)

for i in range(nTimes):
    recs = smrObj.recommend_by_profile(prof, 12)

tend = time.time()
print("\t\tTime to compute 1 profile recommendation: " + str((time.time() - tstart) / nTimes))
print("\t\tTime to compute " + str(nTimes) + " profile recommendations: " + str(time.time() - tstart))


# ========================================================================================================================
print("=" * 120)

print("\t\tItem recommendations:")

nTimes = 100
tstart = time.time()

hist = ["Data::Reshapers:ver<0.1.8>"]

for i in range(nTimes):
    recs = smrObj.recommend(hist, 12)

tend = time.time()
print("\t\tTime to compute 1 item recommendation: " + str((time.time() - tstart) / nTimes))
print("\t\tTime to compute " + str(nTimes) + " item recommendations: " + str(time.time() - tstart))

# ========================================================================================================================
print("=" * 120)

print("\t\tDump pickle:")

tstart = time.time()

with open('smrObj-ZefEcosystem.pickle', 'wb') as handle:
    pickle.dump(smrObj, handle)

tend = time.time()
print("\t\tTime to dump pickle: " + str(time.time() - tstart))

tstart = time.time()

with open('smrObj-ZefEcosystem.pickle', 'rb') as handle:
    smrObj2 = pickle.load(handle)

tend = time.time()
print("\t\tTime to load pickle: " + str(time.time() - tstart))

print(repr(smrObj2))
