import pandas as pd
import numpy as np
import datetime
import pytz
from pathlib import Path
from . import calpost_reader
calpost_cat = calpost_reader.calpost_cat


# old name...
def Reader(f, tslice=slice(None, None), x=None, y=None):
    warnings.warn('use hysplit_reader()', DeprecationWarning)
    return hysplit_reader(f, tslice, x, y)

def hysplit_reader(f, tslice=slice(None, None), x=None, y=None):
    # assume file name passed if 'f' is string
    if isinstance(f, (str, Path)):
        with open(f) as ff:
            return hysplit_reader(ff, tslice, x, y)

    # read each input, and then cat
    if isinstance(f, list):
        dat = [hysplit_reader(_, slice(None, None), x, y) for _ in f]
        dat = calpost_cat(dat)
        print('ts.shp=', dat['ts'].shape)
        print('v.shp=', dat['v'].shape)
        print('ts.typ=', type(dat['ts']))
        print('v.typ=', type(dat['v']))
        print('s=', tslice)
        print(dat['ts'][tslice].shape)
        print(dat['v'][tslice].shape)
        print(dat['ts'][60:].shape)
        print(dat['v'][60:].shape)
        dat['ts'] = dat['ts'][tslice]
        dat['v'] = dat['v'][tslice]
        print('ts.shp=', dat['ts'].shape)
        print('v.shp=', dat['v'].shape)
        return dat

    data = pd.read_csv(f, sep='\s+')
    data = data.iloc[tslice, :]
    # there is no way to tell units...?
    units = '???'

    v = data.iloc[:, 9:].values
    ts = [datetime.datetime(_[0] + 2000, *_[1:]).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6'))
          for _ in data.iloc[:, 1:6].itertuples(index=False)]

    dct0 = {}
    if not all((x is None, y is None)):
        nx, ny = len(x), len(y)
        print(v.shape, nx, ny)
        is_subregion = False
        if nx*ny == v.shape[1]:
            grid = {'x0': x.min(), 'x1': x.max(), 'y0': y.min(), 'y1': y.max(),
                    'nx': nx, 'ny': ny, 'dx': x[1] - x[0],
                    'dy': y[1] - y[0]}
            v = v.reshape(-1, ny, nx)

            dct0 = {'x': x, 'y': y, 'grid': grid}
        elif nx == v.shape[1] and ny == v.shape[1]: 
            # hold on to each point's coordinates
            xr = x
            yr = y

            # get the unique values of x and y
            x = np.unique(x)
            y = np.unique(y)

            nx = len(x)
            ny = len(y)

            is_subregion = True
            idx = [(_ == x).argmax() for _ in xr]
            jdx = [(_ == y).argmax() for _ in yr]
            map_subregion = [(j, i) for (j, i) in zip(jdx, idx)]
    

            grid = {'x0': x.min(), 'x1': x.max(), 'y0': y.min(), 'y1': y.max(),
                    'nx': nx, 'ny': ny, 'dx': x[1] - x[0],
                    'dy': y[1] - y[0]}

            vv = np.empty((v.shape[0], ny, nx))
            vv[:] = np.nan
            for t in range(v.shape[0]):
                for ji, val in zip(map_subregion, v[t, :]):
                    vv[t][ji] = val
            v = vv

            dct0 = {'x': x, 'y': y, 'grid': grid}

        else:
            raise ValueError(
                f'inconsistent shape: len(x),len(y),v.shape = {len(x)}, {len(y)}, {v.shape}'
            )
            



    #print(x)
    #ptid = pd.DataFrame.from_dict({
    #    'x': x,
    #    'y': y,
    #    'sxy': ['%d:%d' % (p,q) for (p,q) in zip(*[1000*np.round(_, 2) for _
    #        in (x, y)])]
    #    })
    dct = {'v': v, 'ts': ts, 'units': units, 'df': data, 'name': None}
    if dct0:
        dct.update(dct0)

    return dct


def tester():
    with open("../data/outconc.S2.pulse.NAM.txt") as f:
        x = np.arange(34) * 0.1 - 464.35
        y = np.arange(47) * 0.1 - 996.65
        dat = Reader(f, x=x, y=y)
    return dat


if __name__ == '__main__':
    x = tester()
