#!/Users/antonov/miniforge3/envs/SciPyCentric/bin/python3
"""invoke-smr

Usage:
    invoke-smr.py -h|--help
    invoke-smr.py -v|--version
    invoke-smr.py [-f|--file=FILE] [--profile=PROF] [--must=MUST] [--mustnot=MUSTNOT] [--nrecs=NRECS] [--smr=SMRID] [--type=TYPE]
    invoke-smr.py --pipe
    invoke-smr.py <text>... [--profile=PROF] [--nrecs=NRECS] [--smr=SMRID] [--type=TYPE]

Options:
    -h --help                 Show this screen.
    -v --version              Show version.
    -p --profile=PROF         Profile tags[default : ""]
    --must=MUST               Must profile tags [default : ""]
    --mustnot=MUSTNOT         Must not profile tags [default : ""]
    -s --smr=SMRID            SMR identifier
    -t --type=TYPE            Type of the output, one of 'CSV', 'DF', 'JSON'. [default: DF]
    -n --nrecs=NRECS          Number of recommendations. [default: 12]
    -f --file=FILE            File with text
    --pipe                    Pipeline input
"""

from docopt import docopt
import sys
import ast
import pandas
import getpass

import time
import pickle

from SparseMatrixRecommender.SparseMatrixRecommender import *
from SparseMatrixRecommender.DataLoaders import *
from CompositeRecommenders.LSAEndowedSMR import *
from CompositeRecommenders.SMR_to_LSA import *


def recommend(profileArg: str, textArg: str, smr_id: str, nrecsArg: int = 12):
    with open('smrEndowed-' + smr_id + '.pickle', 'rb') as handle:
        smrEndowed = pickle.load(handle)

    if len(profileArg) == 0:
        profileLocal = []
    else:
        profileLocal = [x.strip() for x in profileArg.split(";")]

    recs = (smrEndowed
            .recommend_by_profile_and_text(profile=profileLocal,
                                           text=textArg,
                                           ignore_unknown=True,
                                           nrecs=nrecsArg)
            .take_value())

    # The result
    return recs


def retrieve(profileArg: str, mustArg: str, mustNotArg: str, smr_id: str):
    with open('smrObj-' + smr_id + '.pickle', 'rb') as handle:
        smrObj = pickle.load(handle)

    if len(profileArg) == 0:
        profileLocal = []
    else:
        profileLocal = [x.strip() for x in ast.literal_eval(profileArg).split(";")]

    if len(mustArg) == 0:
        mustLocal = []
    else:
        mustLocal = [x.strip() for x in ast.literal_eval(mustArg).split(";")]

    if len(mustNotArg) == 0:
        mustNotLocal = []
    else:
        mustNotLocal = [x.strip() for x in ast.literal_eval(mustNotArg).split(";")]

    recs = (smrObj
            .retrieve_by_query_elements(should=profileLocal,
                                        must=mustLocal,
                                        must_not=mustNotLocal,
                                        ignore_unknown=True)
            .take_value())

    # The result
    return recs


__version__ = "Invoke-SMR-0.0.1"

if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)

    if args['--pipe']:
        pipe = sys.stdin.read()
        args = docopt(__doc__, pipe)

    if args['--profile'] or args['--must'] or args['--mustnot'] or args['<text>'] or args['--file']:
        if args['--smr']:
            smrID = args['--smr']
        else:
            smrID = "ZefEcosystem"

        profile = ""
        if args['--profile']:
            profile = args['--profile']

        must = ""
        if args['--must']:
            must = args['--must']

        mustNot = ""
        if args['--mustnot']:
            mustNot = args['--mustnot']

        text = ""
        if args['<text>']:
            text = args['<text>']
        elif args['--file']:
            text = open(args['--file'][0]).read()

        nrecs = int(args['--nrecs'])

        if len(must) > 0 or len(mustNot) > 0:
            result = retrieve(profile, must, mustNot, smrID)
        else:
            result = recommend(profile, text, smrID, nrecs)

        dfResult = pandas.DataFrame(result.items(), columns=['Item', 'Score'])

        if str(args['--type']).lower() == 'csv':
            dfResult.to_csv('invoke-smr.csv', index=False)
        elif str(args['--type']).lower() == 'df':
            print(dfResult.to_string())
            dfResult
        else:
            print(result)

    else:
        print("Do not know what to do without profile or text arguments.")
