import pandas as pd
import datetime
import pytz
from functools import reduce



def Reader(f, tslice=slice(None,None), x=None, y=None):
    data = pd.read_csv(f, sep='\s+')
    data = data.iloc[tslice, :]
    units = 'ppb'

    v = data.iloc[:, 9:].to_numpy()
    ts = [ datetime.datetime(_[0]+200, *_[1:]).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6')) for _ in data.iloc[:, 1:6].itertuples(index=None)]

    if not all((x is None, y is None)):
        nx, ny = len(x), len(y)
        grid = {'x0': x.min(), 'x1': x.max(), 'y0': y.min(), 'y1':y.max(),
                'nx': nx, 'ny': ny, 'dx': x[1]-x[0],
                'dy':y[1]-y[0]}
        v = v.reshape(-1, ny, nx)

        dct0 = {'x': x, 'y': y, 'grid':grid}


    dct = {'v': v, 'ts': ts, 'units': units, 'df': data}
    if dct0:
        dct.update(dct0)

    return dct


def tester():
    with open( "../data/outconc.S2.pulse.NAM.txt") as f:
        x = Reader(f)
    return x
if __name__ == '__main__':
    x = tester()
