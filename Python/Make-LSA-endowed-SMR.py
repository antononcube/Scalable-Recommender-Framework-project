import pandas
import time
import timeit
import pickle

from SparseMatrixRecommender.SparseMatrixRecommender import *
from SparseMatrixRecommender.DataLoaders import *
from CompositeRecommenders.LSAEndowedSMR import *
from CompositeRecommenders.SMR_to_LSA import *

recommenderID = "ZefEcosystem"

derive_LSA_from_tags = False

# In case we want to see the original SMR matrix data frame.
if recommenderID == "ZefEcosystem":
    dfSMRMatrix =  pandas.read_csv("../Data/ZefEcosystem-dfSMRMatrix.csv.gz", compression='gzip')
else:
    print("Do not know what to do for the given recommender ID.")

# ===========================================================
# Ingest SMR object
# ===========================================================

tstart = time.time()

with open('smrObj-' + recommenderID + '.pickle', 'rb') as handle:
    smrObj = pickle.load(handle)

tend = time.time()
print("\t\tTime to load pickle: " + str((time.time() - tstart)))

print(repr(smrObj))

# ===========================================================
# Make LSA object
# ===========================================================

print("-" * 120)

if derive_LSA_from_tags:

    tstart = time.time()

    lsaObj = SMR_to_LSA(smrObj, number_of_topics=60, min_number_of_documents_per_term=200)

    tend = time.time()
    print("\t\tTime to create LSA from SMR: " + str((time.time() - tstart)))

    smatWords = lsaObj.take_doc_term_mat().copy()
    smatWords01 = smatWords.unitize()
    cns = smatWords01.column_sums_dict()
    cns = [k for (k, v) in cns.items() if v >= 200]
    smatWords = smatWords[:, cns]
    smatWords = smatWords.set_column_names(["Word:" + c for c in smatWords.column_names()], )

    smatTopics = lsaObj.take_W().copy()
    smatTopics = smatTopics.set_column_names(["Topic:" + c for c in smatTopics.column_names()])

    smrObj = smrObj.annex_sub_matrices(mats={"Word": smatWords, "Topic": smatTopics})
    smrObj = smrObj.apply_term_weight_functions("None", "None", "Cosine")

    # Make LSA endowed SMR object

    smrEndowed = LSAEndowedSMR(smrObj, lsaObj)

else:
    # This is somewhat of a shortcut: creating LSA from SMR instead of ingesting the corresponding files.
    smatWords = smrObj.sub_matrix("Word")
    smatWords.set_column_names([x.replace("Word:", "") for x in smatWords.column_names()])
    print(repr(smatWords))

    lsaObj = (LatentSemanticAnalyzer()
              .set_document_term_matrix(smatWords)
              .apply_term_weight_functions("None", "None", "Cosine")
              .extract_topics(number_of_topics=60,
                              method="SVD",
                              max_steps=120))

    print(repr(lsaObj))

    # Make LSA endowed SMR object
    smrEndowed = LSAEndowedSMR(smrObj, lsaObj)

# ===========================================================
# Show the LSA endowed SMR
# ===========================================================

print("-" * 120)
print(repr(smrEndowed))

# ===========================================================
# Combined recommendations
# ===========================================================

print("-" * 120)

recs = (smrEndowed
        .recommend_by_profile_and_text(profile=[],
                                       text="symbolic mathematics and trigonometry functions",
                                       ignore_unknown=True)
        .take_value())

print(recs)

# ===========================================================
# Combined recommendations
# ===========================================================

print("=" * 120)

print("\t\tDump pickle:")

tstart = time.time()

with open('smrEndowed-' + recommenderID + '.pickle', 'wb') as handle:
    pickle.dump(smrEndowed, handle)

tend = time.time()
print("\t\tTime to dump pickle: " + str(time.time() - tstart))
