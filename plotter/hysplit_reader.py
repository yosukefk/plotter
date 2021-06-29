import pandas as pd
import numpy as np
import datetime
import pytz
from pathlib import Path
import warnings
from io import IOBase

from . import calpost_reader
calpost_cat = calpost_reader.calpost_cat


# old name...
def Reader(f, tslice=slice(None, None), x=None, y=None):
    warnings.warn('use hysplit_reader()', DeprecationWarning)
    return hysplit_reader(f, tslice, x, y)

def hysplit_reader_long(f, tslice=slice(None, None), x=None, y=None,
                        rdx_map=None):
    """reads hysplit output file, returns dict of numpy arrays


    :param FileIO f: either (1)opened hysplit output file, (2) hysplit output filename or (3) list of (1) or (2)
    :param slice tslice: slice of time index
    :param list x: list of x coords
    :param list y: list of y coords

    :return: dict, with ['v'] has data as 3d array (t, y, x)
    :rtype: dict
    """
    print(type(f))
    if isinstance(f, IOBase):
        raise ValueError('plese pass filename, not FileIO...')

    # assume file name passed if 'f' is string
    if isinstance(f, (str, Path)):
        df = pd.read_csv(f, sep=r'\s+')
        return hysplit_reader_long(df, tslice, x, y, rdx_map)


    # list of files may have different time period and locations.  So
    # first they are grouped by time perod, then each chunk got read.
    # then they got joined with the time stiching routine aware of
    # spin-up time
    if isinstance(f, list):
        lines = [next(pd.read_csv(fn, sep=r'\s+', nrows=1).itertuples()) for fn in f]
        # Pandas(Index=0, JDAY=268.208, YR1=19, MO1=9, DA1=25, HR1=5, MN1=0,
        # YR2=19, MO2=9, DA2=25, HR2=5, MN2=1, Pol=1, Lev=1, Station=1,
        # Value=0.0)
        print(lines)
        dtes = [datetime.datetime(_.YR1, _.MO1, _.DA1, _.HR1,
                                 _.MN1).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6'))
               for _ in lines]
        df_fnames = pd.DataFrame({'fname': f, 'datetime': dtes})

        # group the file names by the datetime
        dct_fnames = {}
        for fn,dte in zip(f, dtes):
            dct_fnames.setdefault(dte, []).append(fn)

        print(dct_fnames)

        dat = []
        for dte,fnames in dct_fnames.items():
            dfs = [pd.read_csv(fn, sep=r'\s+') for fn in fnames]
            df = pd.concat(dfs)
            dat.append(  hysplit_reader_long(df, tslice, x, y, rdx_map) )

        dat = calpost_cat(dat)
        dat['ts'] = dat['ts'][tslice]
        dat['v'] = dat['v'][tslice]
        return dat

    # now i should be getting dataframe
    df = f

    units = '???'

    df['Datetime'] = [datetime.datetime(_.YR1, _.MO1, _.DA1, _.HR1,
                                 _.MN1).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6')) 
                      for _ in df.itertuples()]

    df = df[['Datetime', 'Lev', 'Station', 'Value']]
    #grouped = df.groupby(['Datetime', 'Lev', 'Station'])

    nrec = len(df.index)


    df = df[['Datetime', 'Lev', 'Station', 'Value']].set_index( ['Datetime', 'Station', 'Lev'] )
    ts = df.index.levels[0]
    stations = df.index.levels[1]
    nz = len(df.index.levels[2])
    nsta = len(df.index.levels[1])
    nt = len(df.index.levels[0])
    assert nt * nz * nsta == nrec
    print(df.columns)

    df = df.unstack().unstack()
    print(df.columns)
    df.columns = df.columns.droplevel()
    print(df.columns)

    if rdx_map:
        x = rdx_map.x
        y = rdx_map.y
        nx = len(x)
        ny = len(y)
        grid = rdx_map.grid
        v = df.to_numpy()
        if rdx_map.coverage == 'full, c-order' and nsta==nx*ny:
            v = v.reshape(nt, nz, ny, nx)
        elif rdx_map.coverage == 'full, f-order' and nsta==nx*ny:
            raise NotImplementedError(
                'qa first! receptor def = "{}", '.format(rdx_map.coverage))
            v = v.reshape(nt, nz,  nx, ny)
            v = np.swapaxes(v, -1, -2)
        elif rdx_map.coverage in ('full, c-order', 'full, f-order', 'full, random', 'patial, random'):
            rdx = np.arange(nt*nz) + 1
            mymap = rdx_map.get_index(stations).to_numpy()
            mymap = mymap[:, ::-1]

            vv = np.empty((nt, nz, ny, nx))
            vv[...] = np.nan

            v = v.reshape(nt , nz, -1)
            for tt,t in zip(vv, v):
                for zz, z in zip(tt, t):
                    for ji,p in zip(mymap,z):
                        zz[tuple(ji)] = p
            v = vv
    else:
        ValueError('rdx_map is mandatory for now')

    dct = {'v': v, 'ts': ts, 'units': units, 'df': f, 'name': None}
    dct.update(  {'x': x, 'y': y, 'grid': grid, })
    return dct
    


    


def reshape(v, x=None, y=None, rdx_map=None):

    if rdx_map is not None:

        dct0 = {'x': rdx_map.x, 'y': rdx_map.y, 'grid': rdx_map.grid}

        nx, ny =  [rdx_map.grid[_] for _ in ['nx', 'ny']]

        map_subregion = rdx_map.get_index(rdx)

        vv = np.empty((v.shape[0], ny, nx))
        vv[...] = np.nan
        for t in range(v.shape[0]):
            for ij, val in zip(map_subregion.itertuples(index=False), v[t, :]):
                #print(ij, val)
                #print(vv[t].shape)
                ji = ij[::-1]

                vv[t][ji] = val
        v = vv


    elif not all((x is None, y is None)):

        nx, ny = len(x), len(y)
        print(v.shape, nx, ny)

        if nx*ny == v.shape[1]:
            dx, dy = x[1] - x[0], y[1] - y[0]
            x0, y0 = x.min() - .5*dx, y.min() - .5*dy
            x1, y1 = x.max() + .5*dx, y.max() + .5*dy
            grid = {'x0':x0, 'x1': x1, 'y0': y0, 'y1': y1,
                    'nx': nx, 'ny': ny, 'dx': dx, 'dy': dy, }
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

            idx = [(_ == x).argmax() for _ in xr]
            jdx = [(_ == y).argmax() for _ in yr]
            map_subregion = [(j, i) for (j, i) in zip(jdx, idx)]

            dx, dy = x[1] - x[0], y[1] - y[0]
            x0, y0 = x.min() - .5*dx, y.min() - .5*dy
            x1, y1 = x.max() + .5*dx, y.max() + .5*dy
            grid = {'x0':x0, 'x1': x1, 'y0': y0, 'y1': y1,
                    'nx': nx, 'ny': ny, 'dx': dx, 'dy': dy, }

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


def hysplit_reader(f, tslice=slice(None, None), x=None, y=None, rdx_map=None):
    """reads hysplit output file, returns dict of numpy arrays

    :param FileIO f: either (1)opened hysplit output file, (2) hysplit output filename or (3) list of (1) or (2)
    :param slice tslice: slice of time index
    :param list x: list of x coords
    :param list y: list of y coords

    :return: dict, with ['v'] has data as 3d array (t, y, x)
    :rtype: dict
    """
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

    data = pd.read_csv(f, sep=r'\s+')

    data = data.iloc[tslice, :]
    # there is no way to tell units...?
    units = '???'

    v = data.iloc[:, 9:].values
    rdx = [int(_) for _ in data.columns[9:]]
    ts = np.array([datetime.datetime(_[0] + 2000, *_[1:]).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6'))
          for _ in data.iloc[:, 1:6].itertuples(index=False)])

    dct0 = {}
    if rdx_map is not None:
        dct0 = {'x': rdx_map.x, 'y': rdx_map.y, 'grid': rdx_map.grid}
        nx, ny =  [rdx_map.grid[_] for _ in ['nx', 'ny']]

        map_subregion = rdx_map.get_index(rdx)

        vv = np.empty((v.shape[0], ny, nx))
        vv[...] = np.nan
        for t in range(v.shape[0]):
            for ij, val in zip(map_subregion.itertuples(index=False), v[t, :]):
                #print(ij, val)
                #print(vv[t].shape)
                ji = ij[::-1]

                vv[t][ji] = val
        v = vv


    elif not all((x is None, y is None)):

        nx, ny = len(x), len(y)
        print(v.shape, nx, ny)

        if nx*ny == v.shape[1]:
            dx, dy = x[1] - x[0], y[1] - y[0]
            x0, y0 = x.min() - .5*dx, y.min() - .5*dy
            x1, y1 = x.max() + .5*dx, y.max() + .5*dy
            grid = {'x0':x0, 'x1': x1, 'y0': y0, 'y1': y1,
                    'nx': nx, 'ny': ny, 'dx': dx, 'dy': dy, }
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

            idx = [(_ == x).argmax() for _ in xr]
            jdx = [(_ == y).argmax() for _ in yr]
            map_subregion = [(j, i) for (j, i) in zip(jdx, idx)]

            dx, dy = x[1] - x[0], y[1] - y[0]
            x0, y0 = x.min() - .5*dx, y.min() - .5*dy
            x1, y1 = x.max() + .5*dx, y.max() + .5*dy
            grid = {'x0':x0, 'x1': x1, 'y0': y0, 'y1': y1,
                    'nx': nx, 'ny': ny, 'dx': dx, 'dy': dy, }

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

    # print(x)
    # ptid = pd.DataFrame.from_dict({
    #     'x': x,
    #     'y': y,
    #     'sxy': ['%d:%d' % (p,q) for (p,q) in zip(*[1000*np.round(_, 2) for _
    #         in (x, y)])]
    #     })
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
