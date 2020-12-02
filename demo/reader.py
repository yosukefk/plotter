import pandas as pd
import numpy as np

from pathlib import Path
from itertools import islice
import datetime
import re
import pytz

def reader(f, tslice=slice(None,None)):
    name = next(f)[31:]
    next(f)
    units = next(f)
    m = re.search('\((.*)\)', units)
    assert m
    units = m[1]
    for i in range(3):
        next(f)
    typ = next(f)
    ix = next(f)
    iy = next(f)
    x = next(f)
    y = next(f)

    ix = np.fromstring(ix[16:], dtype=int, sep=' ')
    iy = np.fromstring(iy[16:], dtype=int, sep=' ')
    x = np.fromstring(x[16:], dtype=float, sep=' ')
    y = np.fromstring(y[16:], dtype=float, sep=' ')
    x = np.unique(x)
    y = np.unique(y)

    nx = max(ix)
    ny = max(iy)
    print(nx, ny)
    assert len(x) == nx
    assert len(y) == ny

    for i in range(3):
        next(f)

    dx = x[1] - x[0]
    dy = y[1] - y[0]
    x0 = x[0] - .5 * dx
    y0 = y[0] - .5 * dy
    grid = {'x0': x0, 'y0': y0, 'nx': nx, 'ny': ny, 'dx': dx, 'dy': dy}

    lst_v = []
    lst_ts = []
    for i,line in islice(enumerate(f), tslice.start, tslice.stop):
        ts = datetime.datetime.strptime(line[:16], ' %Y %j %H%M ')
        ts = ts.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6'))
        
        #print(ts)
        lst_ts.append(ts)

        v = np.fromstring(line[16:], dtype=float, sep=' ').reshape(ny, nx)
        #print(v)
        lst_v.append(v)
    ts = np.array(lst_ts)
    v = np.stack(lst_v, axis=0)
    return {'name': name, 'units': units, 'ts': ts, 'grid': grid, 'y':y, 'x':x, 'v': v}

        

def tester():
    ddir = Path('../calpost')
    fname = 'tseries_ch4_1min_conc_co_fl.dat'

    with open(ddir /fname) as f:
        dat = reader(f)
    return dat
