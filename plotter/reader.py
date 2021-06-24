from . import calpost_reader as cpr
from . import hysplit_reader as hsr

import numpy as np
from pathlib import Path


def get_format(f):
    """tells if file is from calpost or hysplit"""
    if isinstance(f, (str, Path)):
        with open(f) as ff:
            return get_format(ff)

    line = next(f)
    f.seek(0)

    if line.startswith(' TIME-SERIES Output  --------  '):
        fmt = 'calpost'
    elif line.startswith('    JDAY  YR  MO DA1 HR1 MN1 DA2 HR2 MN2'):
        fmt = 'hysplit'
    else:
        raise ValueError(f'unknown file format: {line[:30]}')

    return fmt


def reader(f, tslice=slice(None, None), x=None, y=None):
    """reads calpost/hysplit tseries output file (gridded recep), returns dict of numpy arrays

    :param FileIO f: either (1) opened tseries file, (2) tseries file name or (3) list of (1) or (2)
    :param slice tslice: slice of time index
    :param list x: list of x coords
    :param list y: list of y coords

    :return: dict, with ['v'] has data as 3d array (t, y, x)
    :rtype: dict
    """

    # assume file name passed if 'f' is string
    if isinstance(f, (str, Path)):
        with open(f) as ff:
            return reader(ff, tslice, x, y)

    # read each input, and then cat
    if isinstance(f, list):
        dat = [reader(_, slice(None, None), x, y) for _ in f]
        dat = cat(dat)
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

    fmt = get_format(f)

    if fmt == 'calpost':
        return cpr.calpost_reader(f, tslice, x, y)
    elif fmt == 'hysplit':
        return hsr.hysplit_reader(f, tslice, x, y)
    else:
        raise ValueError('unknown file format')


def cat(lst):
    """
    concatenates list of hysplit/calpost tseries data, assuming they are continuous time series

    :param lst: list of data from reader()
    :return:  dict similar to the one from reader()
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

        raise ValueError('incompatible header: {}'.format(msg))

    # time step size
    td = [_['ts'][1] - _['ts'][0] for _ in lst]
    # print('td (timestep size) =',td)
    # print('(td == td[0]) = ',[_ == td[0] for _ in td])
    if not all([_ == td[0] for _ in td]):
        raise ValueError('incompatible time step size: {}'.format(td))

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
        raise ValueError('incompatible time series: {}'.format(msg))

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
