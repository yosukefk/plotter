import pandas as pd
import numpy as np

from pathlib import Path
from itertools import islice
import datetime
import re
import pytz
from . import plotter_util as pu

import warnings
import logging, sys

# Configure logging to print to stdout
logging.basicConfig( 
        level=logging.INFO,  # Set the logging level 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the log message format 
        handlers=[logging.StreamHandler(sys.stdout)]  # Set the handler to print to stdout
        )

class cprValueError(ValueError):
    pass


# old name...
def Reader(f, tslice=slice(None, None), x=None, y=None, z=None):
    warnings.warn('use calpost_reader()', DeprecationWarning)
    return calpost_reader(f, tslice, x, y)

def arr2df(arrays, ts, tags=None, n=None):
    # take arr, ts from reader, return dataframe for ggplot

    if isinstance(arrays, np.ndarray):
        arrays = [arrays]
    if tags is None:
        tags = [None] * len(arrays)

    longging.debug('shpin',[_.shape for _ in arrays])
    vs = [arr.reshape(arr.shape[0], -1) for arr in arrays]

    logging.debug('vs',[_.shape for _ in vs])
    logging.debug('nan', [sum(np.isnan(_)) for _ in vs])

    ## drop nans
    #vs = [v[:, ~np.isnan(v[0, :])] for v in vs]
    #logging.debug('vs',[_.shape for _ in vs])

    nn = [_.shape[-1] for _ in vs]
    logging.debug('nn', nn)
    nn = nn[0]
    if n is None:
        n = nn
    sel = sorted(np.random.choice(np.arange(nn), n, replace=False))
    logging.debug('sel', sel)

    dfs = []
    for v, tag in zip(vs, tags):
        logging.debug('tag', tag)
        df = pd.DataFrame( 
            dict( 
                tag=tag,
                t=np.repeat(ts, n),
                v=v[:, sel].reshape(-1),
            ))
        df['hr'] = (df['t'] - df['t'][0]).dt.total_seconds() / 3600
        dfs.append(df)

    df = pd.concat(dfs, axis=0)
    return df

def calpost_df(f, tslice=slice(None, None), x=None, y=None, z=None,
                   rdx_map=None):
    dat = calpost_reader(f, tslice, x, y, z, rdx_map)


def calpost_reader(f, tslice=slice(None, None), x=None, y=None, z=None,
                   rdx_map=None, is_subregion=None):
    """reads calpost tseries output file (gridded recep), returns dict of numpy arrays

    :param FileIO f: either (1) opened calpost tseries file, (2) calpost tseries file name or (3) list of (1) or (2)
    :param slice tslice: slice of time index
    :param list x: list of x coords
    :param list y: list of y coords

    :return: dict, with ['v'] has data as 3d array (t, y, x)
    :rtype: dict
    """

    # https://stackoverflow.com/a/23796737/1013786
    class ConfidentialFile():
        # behave like a while but cut first 13 chars from each rows if
        # it is confidential file
        #
        # sample usage
        #
        # with ConfidentialFile(fname) as f:
        #     for i in range(14):
        #         sys.stdout.write(next(f))

        def __init__(self, *args,**kwds):
            self.args = args
            self.kwds = kwds
            self.file_obj = open(*self.args, **self.kwds)
            firstline = next(self.file_obj)
            if 'CONFIDENTIAL' in firstline:
                logging.debug('confidential!!')
                self.confidential = True
            else:
                logging.debug('not condidential!!')
                self.confidential = False
            self.file_obj.seek(0)


        def __enter__(self):
            return self
        def __exit__(self, *args, **kwds):
            return

        def __next__(self):
            line = next(self.file_obj)
            if self.confidential:
                line = line[13:]
            return line

        def __iter__(self):
            return iter(self.file_obj)
        def __getattr__(self, attr):
            return gettatr(self.file_obj, attr)


    # assume file name passed if 'f' is string
    if isinstance(f, (str, Path)):
        #with open(f) as ff:
        with ConfidentialFile(f) as ff:
            return calpost_reader(ff, tslice, x, y, z, rdx_map, is_subregion)

    # read each input, and then cat
    if isinstance(f, list):
        dat = [calpost_reader(_, slice(None, None), x, y, z, rdx_map, is_subregion) for _ in f]
        dat = calpost_cat(dat)
        logging.debug('ts.shp=', dat['ts'].shape)
        logging.debug('v.shp=', dat['v'].shape)
        logging.debug('ts.typ=', type(dat['ts']))
        logging.debug('v.typ=', type(dat['v']))
        logging.debug('s=', tslice)
        logging.debug(dat['ts'][tslice].shape)
        logging.debug(dat['v'][tslice].shape)
        logging.debug(dat['ts'][60:].shape)
        logging.debug(dat['v'][60:].shape)
        dat['ts'] = dat['ts'][tslice]
        dat['v'] = dat['v'][tslice]
        logging.debug('ts.shp=', dat['ts'].shape)
        logging.debug('v.shp=', dat['v'].shape)
        return dat

    if z is not None:
        nz = len(z)
    else:
        nz = 1


    line = next(f)
    name_lay =line[31:] 
    name, lay = [_.strip() for _ in (name_lay[:13], name_lay[13:])]
    logging.info('name: %s', name)
    logging.info('layer: %s', lay)
    next(f)
    units = next(f)
    m = re.search(r'\((.*)\)', units)
    assert m
    units = m[1]
    logging.info('units: %s', units)
    nrec = next(f)
    #m = re.search(r'(\d+)\s+ Receptors', nrec)
    m = re.search(r'(\d+)\s+ (Receptors|Sources)', nrec)
    assert m
    nrec = m[1]
    nrec = int(nrec)
    logging.debug(m[2])
    if m[2] == 'Sources':
        is_source = True
        is_gridded = False
    else:
        is_source = False
    row_per_rec = 1 + nrec // 10000 # calpost has hard-wired max ncol
    #logging.debug('nr, row_per_rec', nrec, row_per_rec)
    next(f) # line for hour spec

    line=next(f)
    if 'Run Title' in line:
        # modified tseries format which export calpuff run title
        rtitle = [next(f) for _ in range(3)]
        # and one empty rline
        line = next(f)
    elif line.strip() == '':
        # original format has one empty line
        rtitle = None

    else:
        raise ValueError(line)


    # calpost tseries file may have multiple line for one record
    class multiline:
        def __init__(self, f,nlines):
            self.f = f
            self.nlines = nlines
        def __iter__(self):
            return self
        def __next__(self):
            if self.nlines == 1:
                return next(self.f)
            buf = [next(self.f).rstrip('\n')  for _ in range(self.nlines)]
            buf[1:] = [_[16:] for _ in buf[1:]]
            return ''.join(buf) + '\n'
            
        def waste(self):
            return next(self.f)



    ff = multiline(f, row_per_rec)

    typ = next(ff)
    ix = next(ff)
    iy = next(ff)
    xx = next(ff)
    yy = next(ff)

    typ = np.array(re.split(' +', typ[16:].strip()))
    ix = np.fromstring(ix[16:], dtype=int, sep=' ')
    iy = np.fromstring(iy[16:], dtype=int, sep=' ')

    if rdx_map:
        if x is None:
            x = rdx_map.x
        if y is None:
            y = rdx_map.y

    # read x,y from file but, can be overwritten if user provide
    if any(_ is None for _ in (x, y)):
        x = np.fromstring(xx[16:], dtype=float, sep=' ')
        y = np.fromstring(yy[16:], dtype=float, sep=' ')
        if nz > 1:
            assert len(x) % nz == 0

            x = x[:int(len(x)/nz)]
            y = y[:int(len(y)/nz)]
    logging.debug('len():', len(ix), len(iy), len(x), len(y))
    logging.debug('len()*nz:', len(ix), len(iy), len(x)*nz, len(y)*nz)
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
    logging.debug('typ: %s', typ)
    logging.debug('nx,ny,nx*ny: %s, %s, %s', nx, ny, nx*ny)
    logging.debug('len(x),len(y),len(x)*len(y), %s %s %s', len(x), len(y), len(x)*len(y))
    logging.debug('nx==len(x)*len(y): %s', nx == len(x)*len(y))
    is_gridded = True
    map_subregion = None
    logging.info('nrec=%s',nrec)
    if is_source:
        # not receptor but source attribution!
        is_gridded=False
    elif nrec < 4:
        # no way to be a grid
        logging.info('discrete, nrec = %s', nrec)
        is_gridded=False
    elif len(x) == nx and len(y) == ny:
        logging.info('gridded 2d')
        # this is good, gridded data, 2D
        # logging.debug('GRID')
        pass
    elif len(x) * len(y) == nx / nz:
        logging.info('gridded 3d')
        # logging.debug('DESC')
        nx = len(x)
        ny = len(y)

    else:
        logging.info('discrete')
        # see if the data is subset of array
        # if len(x) * len(y) * .1  < nx / nz:
        # TODO
        # better test would be needed.
        # * deal with precision of float for x,y coords, to reconstruct
        #   grid.
        # * if selected x, y are approximately evenly spqced, and if not
        #   interpolat
        # * or allow user to specify extent
        logging.debug('is_subregion= %s', is_subregion)
        if is_subregion is None:
            x = np.sort(x)
            y = np.sort(y)
            # * even better yet, allow non-grid data as input
            xd = x[1:] - x[:-1]
            yd = y[1:] - y[:-1]
            logging.debug('dmax, dmin, drng, dmean, dmean*.05, drng<dmean*.05')
            logging.debug('%s %s %s %s %s %s', xd.max(), xd.min(), xd.max()-xd.min(), xd.mean(), xd.mean()*.05, (xd.max()-xd.min()) < (xd.mean()*.05))
            logging.debug('%s %s %s %s %s %s', yd.max(), yd.min(), yd.max()-yd.min(), yd.mean(), yd.mean()*.05, (yd.max()-yd.min()) < (yd.mean()*.05))
            
            is_subregion = (
                ((xd.max() - xd.min()) < (xd.mean() * .05)) and 
                ((yd.max() - yd.min()) < (yd.mean() * .05))
            )
        logging.debug('is_subregion= %s', is_subregion)
        #is_subregion = True

        if is_subregion:
            logging.debug('is_subregion')

            nx = len(x)
            ny = len(y)
            logging.debug('len(xr), len(x) = %s %s', len(xr), len(x))
            logging.debug('len(yr), len(y) = %s %s', len(yr), len(y))
            logging.debug('nz = %s', nz)
            logging.debug('len(xr)/nz = %s', len(xr)/nz)
            logging.debug('len(yr)/nz = %s', len(yr)/nz)

            idx = [(_ == x).argmax() for _ in xr[:int(len(xr)/nz)]]
            jdx = [(_ == y).argmax() for _ in yr[:int(len(yr)/nz)]]
            map_subregion = [(j, i) for (j, i) in zip(jdx, idx)]

        else:
            logging.debug('not is_subregion')
            is_gridded = False
            logging.debug('len(x),len(y)= %s %s', len(x), len(y))
            logging.debug('nx,ny= %s %s', nx, ny)
            logging.debug('%s %s', len(x)*len(y), nx/nz)
            logging.debug('%s %s', len(x)*len(y)*.1, nx/nz)
            #raise RuntimeError('non gridded data...')
            warnings.warn('non gridded data', pu.PlotterWarning)

            # restore x and y as in original order
            x = xr
            y = yr

    for i in range(3):
        #next(f)
        ff.waste()
    

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


    lst_v = []
    lst_ts = []
    for i, line in islice(enumerate(ff), tslice.start, tslice.stop):
        ts = datetime.datetime.strptime(line[:16], ' %Y %j %H%M ')
        ts = ts.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT+6'))

        # logging.debug(ts)
        lst_ts.append(ts)

        v = np.fromstring(line[16:], dtype=float, sep=' ')

        if not is_gridded:
            if nz > 1:
                vv = v.reshape(nz, -1)
            else:
                vv = v


        elif is_subregion:
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
        # logging.debug(v)
        lst_v.append(vv)
    ts = np.array(lst_ts)
    v = np.stack(lst_v, axis=0)
    o = {'name': name, 'units': units, 'ts': ts, 'grid': grid, 'y': y,
            'x': x, 'v': v, 'ptid': ptid, 'cpruntitle': rtitle}
    if nz > 1:
        o.update({'z': np.array(z)})

    return o




def calpost_cat(lst, use_later_files=False):
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
    # logging.debug('td (timestep size) =',td)
    # logging.debug('(td == td[0]) = ',[_ == td[0] for _ in td])
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

    # logging.debug('overlaps=',overlaps)
    if any(_ < 0 for _ in overlaps):
        pos = ['{}/{}'.format(p, p + 1) for p in range(len(lst) - 1)]
        msg1 = ', '.join([pos[i] for i,_ in enumerate(overlaps) if _ == -1])
        msg2 = ', '.join([pos[i] for i,_ in enumerate(overlaps) if _ == -2])
        if msg1:
            msg1 = 'non-advancing: files ' + msg1
        if msg2:
            msg2 = 'non-contiguous: files ' + msg2
        msg = '; '.join([msg1, msg2])
        raise cprValueError('incompatible time series: {}'.format(msg))

    # time series look ok, ready to roll!

    # get all the data from first one
    dat = {k: v for k, v in lst[0].items()}

    # v and ts need to be overwritten by concatenated array

    logging.info('overlaps: %s', overlaps)
    if use_later_files:
        chop = [None if _ == len(overlaps) else _ for _ in overlaps]

        logging.debug('file trange:', [d['ts'][::(len(d['ts'])-1)] for d in lst])

        logging.debug('piked trange:', 
              [ d['ts'][:-o][::(-o-1)] for d, o in
             zip(lst[:-1], chop)] 
              + [ lst[-1]['ts'][::(len(lst[-1]['ts'])-1)] ] )

        dat['ts'] = np.concatenate(
            [d['ts'][:-o] for d, o in
             zip(lst[:-1], chop)]
            + [lst[-1]['ts']]
        )

        dat['v'] = np.concatenate(
            [d['v'][:-o] for d, o in
             zip(lst[:-1], chop)] +
            [lst[-1]['v']]
        )
        
    else:
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
