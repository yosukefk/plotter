import sys

sys.path.append('..')

from plotter.plotter_solo import Plotter
from plotter.plotter_util import BackgroundManager
from pathlib import Path

bgfile = '../resources/naip_toy_pmerc_5.tif'

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
    """background file"""
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'backgound_manager': BackgroundManager(bgfile=bgfile)
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm1.png')


if __name__ == '__main__':
    tester_bgm1()