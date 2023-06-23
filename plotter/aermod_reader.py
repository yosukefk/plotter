import pandas as pd
import numpy as np
import plotter.calpost_reader as cpr

class cprValueError(ValueError):
    pass

def aermod_reader(f, tslice=slice(None, None), x=None, y=None, z=None, rdx_map=None, is_subregion=None):
    # read each input, and then cat
    if isinstance(f, list):
        dat = [aermod_reader(_, slice(None, None), x, y, z, rdx_map, is_subregion) for _ in f]
        dat = cpr.calpost_cat(dat)
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



    width=[14, 14, 14, 9, 9, 9, 8,10,10, 10]
    colspecs = np.cumsum([0]+width)
    colspecs = [(p,q) for p,q in zip(colspecs[:-1], colspecs[1:])]
    df = pd.read_fwf(f, 
            #width=[14, 14, 14, 9, 9, 9, 8,10,10, 10],
            colspecs = colspecs,
            names = ['x', 'y', 'conc', 'zelev', 'zhill', 'zflag', 'ave', 'grp', 'datetime', 'netid'],
            skiprows=8,
            )
    df['datetime'] = pd.to_datetime(df['datetime']-1, format='%y%m%d%H') + pd.Timedelta(1, 'H')

    ii = (df.datetime > df.datetime[0]).idxmax()
    if ii == 0: ii = len(df.index)

    dfx = df.iloc[:ii, :]

    print((dfx.x > dfx.x[0]).idxmax())
    print((dfx.y > dfx.y[0]).idxmax())

    x = dfx.x
    y = dfx.y
    xr = x
    yr = y

    x = np.unique(x)
    y = np.unique(y)

    is_gridded = True
    if is_subregion is None:

        x = np.sort(x)
        y = np.sort(y)
        # * even better yet, allow non-grid data as input
        xd = x[1:] - x[:-1]
        yd = y[1:] - y[:-1]
        print('dmax, dmin, drng, dmean, dmean*.05, drng<dmean*.05')
        print(xd.max(), xd.min(), xd.max()-xd.min(), xd.mean(), xd.mean()*.05, (xd.max()-xd.min()) < (xd.mean()*.05))
        print(yd.max(), yd.min(), yd.max()-yd.min(), yd.mean(), yd.mean()*.05, (yd.max()-yd.min()) < (yd.mean()*.05))
        
        is_subregion = (
            ((xd.max() - xd.min()) < (xd.mean() * .05)) and 
            ((yd.max() - yd.min()) < (yd.mean() * .05))
        )
        print('is_subregion=', is_subregion)

    if is_subregion:
        print('is_subregion')

        nx = len(x)
        ny = len(y)
        print('len(xr), len(x)', len(xr), len(x))
        print('len(yr), len(y)', len(yr), len(y))
        print('nz', nz)
        print('len(xr)/nz', len(xr)/nz)
        print('len(yr)/nz', len(yr)/nz)

        idx = [(_ == x).argmax() for _ in xr[:int(len(xr)/nz)]]
        jdx = [(_ == y).argmax() for _ in yr[:int(len(yr)/nz)]]
        map_subregion = [(j, i) for (j, i) in zip(jdx, idx)]

    else:
        print('not is_subregion')
        is_gridded = False
        print('len(x),len(y)=', len(x), len(y))
        print('nx,ny=', nx, ny)
        print(len(x)*len(y), nx/nz)
        print(len(x)*len(y)*.1, nx/nz)
        #raise RuntimeError('non gridded data...')
        warnings.warn('non gridded data', pu.PlotterWarning)

        # restore x and y as in original order
        x = xr
        y = yr

    if is_gridded:
        dx = x[1] - x[0]
        dy = y[1] - y[0]
        x0 = x[0] - .5 * dx
        y0 = y[0] - .5 * dy
        grid = {'x0': x0, 'y0': y0, 'nx': nx, 'ny': ny, 'dx': dx, 'dy': dy}
    else:
        x0 = x[0]
        y0 = y[0]
        x1 = x[-1]
        y1 = y[-1]
        grid = {'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}

    ts = df.datetime.unique()
    nt = len(ts)
    if df['conc'].dtype.char == 'O':
        df['conc'].loc[df.conc.str.contains('****', regex=False)] = '+Inf'
        df['conc'] = df['conc'].astype(float)
    v = df.conc.to_numpy().reshape([nt, ny, nx])
    #print(v.dtype.type)
    #print(v.dtype)
    #print(v.dtype.char)

    return {'name': 'aermod', 'units': 'ug/m3', 'ts':ts, 'grid': grid, 'y':y, 'x':x, 'v': v}

def tester(fname):
    df = aermod_reader(fname)
    return df
if __name__ == '__main__':
    import sys
    df = tester(sys.argv[1])
