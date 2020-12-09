import sys

sys.path.append('..')

from plotter.plotter_solo import Plotter
from plotter.plotter_util import BackgroundManager
from pathlib import Path

bgfile = '../resources/naip_toy_pmerc_5.tif'
bgfile_lcc = '../resources/gamma3_res2.tif'

outdir = Path('results')
if not outdir.is_dir():
    outdir.mkdir()

def tester_bgm0():
    """no background or anything"""
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm0.png')


def tester_bgm1():
    """null background"""
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager()
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm1.png')


def tester_bgm2():
    """background file, tellling what projection it has"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(bgfile=bgfile,
                                                source_projection=ccrs.epsg(3857))
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm2.png')

def tester_bgm3():
    """background file, already processed to pseudo mercator"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(bgfile=bgfile),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm3.png')

def tester_bgm4():
    """background file, TCEQ lcc"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(bgfile=bgfile_lcc),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm4.png')


if __name__ == '__main__':
    # tester_bgm0()
    # tester_bgm1()
    # tester_bgm2()
    # tester_bgm3()
    tester_bgm4()