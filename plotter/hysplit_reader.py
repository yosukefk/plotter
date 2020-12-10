import pandas as pd
from functools import reduce



def Reader(fnames):
    assert len(fnames) == 11
    data = [pd.read_csv(_, sep='\s+') for _ in fnames]
    data = reduce(lambda p,q: p.merge(q), data)

    v = data.iloc[:, 9:]

    return {'v': v}

def tester():
    x = Reader( "outconc.S2.pulse.NAM.txt")
