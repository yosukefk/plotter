import pandas as pd
import datetime
import pytz
from functools import reduce



def Reader(f):
    data = pd.read_csv(f, sep='\s+')

    v = data.iloc[:, 9:]
    ts = [datetime.datetime(*_).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6')) for _ in data.iloc[:, 1:6].itertuples(index=None)]


    return {'v': v, 'ts': ts, 'df': data}

def tester():
    with open( "../data/outconc.S2.pulse.NAM.txt") as f:
        x = Reader(f)
    return x
if __name__ == '__main__':
    x = tester()
