import pandas as pd
import numpy as np
import datetime
import pytz
from pathlib import Path
import warnings
from io import IOBase

from . import calpost_reader
calpost_cat = calpost_reader.calpost_cat


def hysplit_reader_long(f, tslice=slice(None, None), x=None, y=None, z=None,
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
        return hysplit_reader_long(df, tslice, x, y, z, rdx_map)


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
        df_fnames.to_csv('fnames.csv')

        # group the file names by the datetime
        dct_fnames = {}
        for fn,dte in zip(f, dtes):
            dct_fnames.setdefault(dte, []).append(fn)


        file_dates = list(dct_fnames.keys())

        dat = []
        for dte,fnames in dct_fnames.items():
            dfs = [pd.read_csv(fn, sep=r'\s+') for fn in fnames]
            df = pd.concat(dfs)
            dat.append(  hysplit_reader_long(df, tslice, x, y, z, rdx_map) )

        dat = calpost_cat(dat, use_later_files=True)

        dat['ts'] = dat['ts'][tslice]
        dat['v'] = dat['v'][tslice]
        return dat

    # now i should be getting dataframe
    df = f

    units = '???'

    print('dt')
    # extremely slow!
    #df['Datetime'] = [datetime.datetime(_.YR1, _.MO1, _.DA1, _.HR1,
    #                             _.MN1).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6')) 
    #                  for _ in df.itertuples()]
    df['Datetime'] =  pd.to_datetime(df[['YR1', 'MO1', 'DA1', 'HR1', 'MN1']].assign(
         YR1= lambda df: df['YR1'] + 2000).rename(
             columns={'YR1':'year', 'MO1':'month', 'DA1': 'day', 'HR1': 'hour', 'MN1': 'minute'}), 
                    utc=True).dt.tz_convert('Etc/GMT+6')
    # bad idea!
    #df['Datetime_tup'] =  [_ for _ in  df[['YR1', 'MO1', 'DA1', 'HR1',
    #                            'MN1']].itertuples(index=False)]

    df = df[['Datetime', 'Lev', 'Station', 'Value']]
    #grouped = df.groupby(['Datetime', 'Lev', 'Station'])


    nrec = len(df.index)


    print('set_index')
    df = df[['Datetime', 'Lev', 'Station', 'Value']].set_index(
        ['Datetime', 'Station', 'Lev'] )

    print('dt')
    ts = df.index.levels[0]
    #xxx = pd.DataFrame(ts, columns=('year', 'month', 'day', 'hour',
    #                                'minute'))
    #print(xxx)
    #xxx = xxx.assign(year=lambda x: x['year']+2000)
    #print(xxx)
    #
    #ts = pd.to_datetime(
    #    pd.DataFrame(
    #        ts, 
    #        columns=('year', 'month', 'day', 'hour', 'minute')
    #    ).assign(
    #        year=lambda x: x['year']+2000
    #    ))
    #print(ts)

    print('cont')
    stations = df.index.levels[1]
    nz = len(df.index.levels[2])
    nsta = len(df.index.levels[1])
    nt = len(df.index.levels[0])
    print('nt,nz,nsta,nrec=', nt, nz, nsta, nrec)
    # ........ bad idea
    #assert nt * nz * nsta == nrec
    if not nt * nz * nsta == nrec:
        print(f'expected {nt*nz*nsta} rec, got {nrec}, short by {nt*nz*nsta-nrec}')
        print('  f:', f)
        print('  rng:', df.index.levels[0][0], df.index.levels[0][-1])
        

    print('unstack')
    df = df.unstack().unstack()
    df.columns = df.columns.droplevel()

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
        raise ValueError('rdx_map is mandatory for now')

    #dct = {'v': v, 'ts': ts, 'units': units, 'df': f, 'name': None}
    dct = {'v': v, 'ts': ts, 'units': units,          'name': None}
    dct.update(  {'x': x, 'y': y, 'grid': grid, })
    del df
    return dct
    


    


