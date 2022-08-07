#!/Users/antonov/miniforge3/envs/SciPyCentric/bin/python3
"""invoke-smr

Usage:
    invoke-smr.py -h|--help
    invoke-smr.py -v|--version
    invoke-smr.py [-f|--file=FILE] [--profile=PROF] [--nrecs=NRECS] [--smr=SMRID] [--type=TYPE]
    invoke-smr.py --pipe
    invoke-smr.py <text>... [--profile=PROF] [--nrecs=NRECS] [--smr=SMRID] [--type=TYPE]

Options:
    -h --help                 Show this screen.
    -v --version              Show version.
    -p --profile=PROF         Profile tags[default : ""]
    -s --smr=SMRID            SMR identifier
    -t --type=TYPE            Type of the output, one of 'CSV', 'DF', 'JSON'. [default: DF]
    -n --nrecs=NRECS          Number of recommendations. [default: 12]
    -f --file=FILE            File with text
    --pipe                    Pipeline input
"""

from docopt import docopt
import sys
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
        profileLocal = profileArg.split(" ")

    recs = (smrEndowed
            .recommend_by_profile_and_text(profile=profileLocal,
                                           text=textArg,
                                           ignore_unknown=True,
                                           nrecs=nrecsArg)
            .take_value())

    # The result
    return recs


__version__ = "Invoke-SMR-0.0.1"

if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)

    if args['--pipe']:
        pipe = sys.stdin.read()
        args = docopt(__doc__, pipe)

    if args['--profile'] or args['<text>'] or args['--file']:
        if args['--smr']:
            smrID = args['--smr']
        else:
            smrID = "ZefEcosystem"

        profile = ""
        if args['--profile']:
            profile = args['--profile']

        text = ""
        if args['<text>']:
            text = args['<text>']
        elif args['--file']:
            text = open(args['--file'][0]).read()

        nrecs = int(args['--nrecs'])

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
