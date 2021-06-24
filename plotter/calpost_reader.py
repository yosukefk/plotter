import pandas as pd
import numpy as np

from pathlib import Path
from itertools import islice
import datetime
import re
import pytz
import warnings


class cprValueError(ValueError):
    pass


# old name...
def Reader(f, tslice=slice(None, None), x=None, y=None, z=None):
    warnings.warn('use calpost_reader()', DeprecationWarning)
    return calpost_reader(f, tslice, x, y)


def calpost_reader(f, tslice=slice(None, None), x=None, y=None, z=None):
    """reads calpost tseries output file (gridded recep), returns dict of numpy arrays

    :param FileIO f: either (1) opened calpost tseries file, (2) calpost tseries file name or (3) list of (1) or (2)
    :param slice tslice: slice of time index
    :param list x: list of x coords
    :param list y: list of y coords

    :return: dict, with ['v'] has data as 3d array (t, y, x)
    :rtype: dict
    """

    # assume file name passed if 'f' is string
    if isinstance(f, (str, Path)):
        with open(f) as ff:
            return calpost_reader(ff, tslice, x, y, z)

    # read each input, and then cat
    if isinstance(f, list):
        dat = [calpost_reader(_, slice(None, None), x, y, z) for _ in f]
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

    if z is not None:
        nz = len(z)
    else:
        nz = 1

    name = next(f)[31:]
    next(f)
    units = next(f)
    m = re.search(r'\((.*)\)', units)
    assert m
    units = m[1]
    for i in range(3):
        next(f)
    typ = next(f)
    ix = next(f)
    iy = next(f)
    xx = next(f)
    yy = next(f)

    typ = np.array(re.split(' +', typ[16:].strip()))
    ix = np.fromstring(ix[16:], dtype=int, sep=' ')
    iy = np.fromstring(iy[16:], dtype=int, sep=' ')
    # read x,y from file but, can be overwritten if user provide
    if any(_ is None for _ in (x, y)):
        x = np.fromstring(xx[16:], dtype=float, sep=' ')
        y = np.fromstring(yy[16:], dtype=float, sep=' ')
    print('len():', len(ix), len(iy), len(x), len(y))
    ptid = pd.DataFrame.from_dict({
        'ix': ix,
        'iy': iy,
        'x': np.tile(x, nz),
        'y': np.tile(y, nz),
        'sxy': np.tile(
            ['%d:%d' % (p, q) for (p, q) in zip(*[1000 * np.round(_, 2) for _
                                                     in (x, y)])],
            nz),
    })
    # hold on to each point's coordinates
    xr = x
    yr = y

    # get the unique values of x and y
    x = np.unique(x)
    y = np.unique(y)

    nx = max(ix)
    ny = max(iy)
    # print(typ)
    # print(nx, ny, nx*ny)
    # print(len(x), len(y), len(x)*len(y))
    # print(nx == len(x)*len(y))
    is_subregion = False
    map_subregion = None
    if len(x) == nx and len(y) == ny:
        # this is good, gridded data, 2D
        # print('GRID')
        pass
    elif len(x) * len(y) == nx / nz:
        # print('DESC')
        nx = len(x)
        ny = len(y)

    else:
        # see if the data is subset of array
        if len(x) * len(y) * .1 < nx / nz:

            nx = len(x)
            ny = len(y)

            is_subregion = True
            idx = [(_ == x).argmax() for _ in xr[:nx]]
            jdx = [(_ == y).argmax() for _ in yr[:ny]]
            map_subregion = [(j, i) for (j, i) in zip(jdx, idx)]

        else:
            print('len(x),len(y)=', len(x), len(y))
            print('nx,ny=', nx, ny)
            raise RuntimeError('non gridded data...')

    for i in range(3):
        next(f)

    dx = x[1] - x[0]
    dy = y[1] - y[0]
    x0 = x[0] - .5 * dx
    y0 = y[0] - .5 * dy
    grid = {'x0': x0, 'y0': y0, 'nx': nx, 'ny': ny, 'dx': dx, 'dy': dy}

    lst_v = []
    lst_ts = []
    for i, line in islice(enumerate(f), tslice.start, tslice.stop):
        ts = datetime.datetime.strptime(line[:16], ' %Y %j %H%M ')
        ts = ts.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6'))

        # print(ts)
        lst_ts.append(ts)

        v = np.fromstring(line[16:], dtype=float, sep=' ')

        if is_subregion:
            # TODO
            if nz > 1:
                vv = np.empty((nz, ny, nx))
                vv[:] = np.nan
                for k in nz:
                    for ji, val in zip(map_subregion,
                                       v[k*nz*ny*nx:(k+1)*nz*ny*nx]):
                        vv[k][ji] = val
            else:
                vv = np.empty((ny, nx))
                vv[:] = np.nan
                for ji, val in zip(map_subregion, v):
                    vv[ji] = val
        else:
            if nz > 1:
                vv = v.reshape(nz, ny, nx)
            else:
                vv = v.reshape(ny, nx)
        # print(v)
        lst_v.append(vv)
    ts = np.array(lst_ts)
    v = np.stack(lst_v, axis=0)
    return {'name': name, 'units': units, 'ts': ts, 'grid': grid, 'y': y,
            'x': x, 'v': v, 'ptid': ptid}


def calpost_cat(lst):
    """
    concatenates list of calpost data, assuming they are continuous time series

    :param lst: list of data from calpots_reader()
    :return:  dict similar to the one from calpost_reader()
    """

    chk = {}
    # name, units
    chk['name'] = all((_['name'] == lst[0]['name']) for _ in lst)
    chk['units'] = all((_['units'] == lst[0]['units']) for _ in lst)

    # test grid is identical
    if 'grid' in lst[0]:
        chk['grid'] = all((_['grid'] == lst[0]['grid']) for _ in lst)
    else:
        chk['grid'] = all('grid' not in _ for _ in lst)
    if 'x' in lst[0]:
        chk['x'] = all((all(_['x'] == lst[0]['x'])) for _ in lst)
        chk['y'] = all((all(_['y'] == lst[0]['y'])) for _ in lst)
    else:
        chk['x'] = all('x' not in _ for _ in lst)
        chk['y'] = all('y' not in _ for _ in lst)


    # ptid not checked, because x, y are checked

    if not all(chk.values()):
        msg = ', '.join([_ for _ in chk if not chk[_]])

        raise cprValueError('incompatible header: {}'.format(msg))

    # time step size
    td = [_['ts'][1] - _['ts'][0] for _ in lst]
    # print('td (timestep size) =',td)
    # print('(td == td[0]) = ',[_ == td[0] for _ in td])
    if not all([_ == td[0] for _ in td]):
        raise cprValueError('incompatible time step size: {}'.format(td))

    # done testing, find overlap of time period

    def get_overlap(x, y, td):
        if x[-1] + td == y[0]:
            return 0

        pos = (x == y[0]).argmax()
        if pos == 0:
            if x[0] == y[0]:
                # raise cprValueError('covers identical time period')
                return -1
            else:
                # raise cprValueError('time period has no overlap')
                return -2
        return len(x) - pos

    overlaps = [get_overlap(x['ts'], y['ts'], td[0]) for x, y
                in zip(lst[:-1], lst[1:])]

    # print('overlaps=',overlaps)
    if any(_ < 0 for _ in overlaps):
        pos = ['{}/{}'.format(p, p + 1) for p in range(len(lst) - 1)]
        msg1 = ', '.join([pos[_] for _ in overlaps if _ == -1])
        msg2 = ', '.join([pos[_] for _ in overlaps if _ == -2])
        if msg1:
            msg1 = 'non-advancing: ' + msg1
        if msg2:
            msg2 = 'non-contiguous: ' + msg2
        msg = '; '.join([msg1, msg2])
        raise cprValueError('incompatible time series: {}'.format(msg))

    # time series look ok, ready to roll!

    # get all the data from first one
    dat = {k: v for k, v in lst[0].items()}

    # v and ts need to be overwritten by concatenated array

    chop = [None if _ == 0 else _ for _ in overlaps]

    dat['ts'] = np.concatenate(
        [lst[0]['ts']] +
        [d['ts'][o:] for d, o in
         zip(lst[1:], chop)]
    )

    dat['v'] = np.concatenate(
        [lst[0]['v']] +
        [d['v'][o:] for d, o in
         zip(lst[1:], chop)]
    )
    return dat


def tester():
    ddir = Path('../data')
    fname = 'tseries_ch4_1min_conc_co_fl.dat'

    with open(ddir / fname) as f:
        dat = calpost_reader(f, slice(12 * 60, 12 * 60 + 10))
    return dat


if __name__ == '__main__':
    import sys

    with open(sys.argv[1]) as f:
        dat = calpost_reader(f, slice(12 * 60, 12 * 60 + 10))
    print(dat)
