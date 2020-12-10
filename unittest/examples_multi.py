#!/usr/bin/env python3

import sys
sys.path.append('..')

from plotter.plotter_multi import Plotter
from pathlib import Path

bgfile = '../resources/naip_toy_pmerc_5.tif'
shpfile = '../resources/emitters.shp'
outdir = Path('results')
if not outdir.is_dir():
    outdir.mkdir()

def tester_md1():
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))
    titles = ['example', 'even more example....']
    arrays = [dat['v'], dat['v']]
    x = dat['x'] * 1000
    y = dat['y'] * 1000

    plotter_options = {
        'imshow_options': {
            'origin': 'lower',  # showing array as image require to specifie that grater y goes upward
        }
    }
    plotter_options = [{**plotter_options, 'title': _} for _ in titles]

    p = Plotter(arrays, dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_md1.png')

def tester_md2():
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))
    titles = ['example', 'even more example....']
    arrays = [dat['v'], dat['v']]
    x = dat['x'] * 1000
    y = dat['y'] * 1000

    plotter_options = {
        'imshow_options': {
            'origin': 'lower',  # showing array as image require to specifie that grater y goes upward
        },
        'colorbar_options': None
    }
    plotter_options = [{**plotter_options, 'title': _} for _ in titles]
    figure_options = {
            'colorbar_options': { 
            }
            }

    # make default font size smaller (default is 10)
    #mpl.rcParams.update({'font.size': 8})
    p = Plotter(arrays, dat['ts'], x=x, y=y,
            plotter_options=plotter_options, figure_options=figure_options)
    p(outdir / 'test_md2.png')

def tester_md3():
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))
    titles = ['example', 'even more example....']
    arrays = [dat['v'], dat['v']]
    x = dat['x'] * 1000
    y = dat['y'] * 1000

    plotter_options = {
        'imshow_options': {
            'origin': 'lower',  # showing array as image require to specifie that grater y goes upward
        },
        'colorbar_options': None
    }
    plotter_options = [{**plotter_options, 'title': _} for _ in titles]
    figure_options = {
            'colorbar_options': {
            }
            }

    # make default font size smaller (default is 10)
    #mpl.rcParams.update({'font.size': 8})
    p = Plotter(arrays, dat['ts'], x=x, y=y,
            plotter_options=plotter_options, figure_options=figure_options)
    p(outdir / 'test_md3.png', footnote=dat['ts'][0])

def tester_md4():
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))
    titles = ['example', 'even more example....']
    arrays = [dat['v'], dat['v']]
    x = dat['x'] * 1000
    y = dat['y'] * 1000

    plotter_options = {
        'imshow_options': {
            'origin': 'lower',  # showing array as image require to specifie that grater y goes upward
        },
        'colorbar_options': None
    }
    plotter_options = [{**plotter_options, 'title': _} for _ in titles]
    figure_options = {
            'colorbar_options': {
            }
            }

    # make default font size smaller (default is 10)
    #mpl.rcParams.update({'font.size': 8})
    p = Plotter(arrays, dat['ts'], x=x, y=y,
            plotter_options=plotter_options, figure_options=figure_options)
    p(outdir / 'test_md4.png', suptitle=dat['ts'][0])

def tester_mt1():
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))
    titles = ['example', 'more example', 'even more example....']
    arrays = [dat['v'], dat['v'], dat['v']]
    x = dat['x'] * 1000
    y = dat['y'] * 1000

    plotter_options = {
        'imshow_options': {
            'origin': 'lower',  # showing array as image require to specifie that grater y goes upward
        }
    }
    plotter_options = [{**plotter_options, 'title': _} for _ in titles]

    p = Plotter(arrays, dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_mt1.png')

def tester_mt2():
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))
    titles = ['example', 'more example', 'even more example....']
    arrays = [dat['v'], dat['v'], dat['v']]
    x = dat['x'] * 1000
    y = dat['y'] * 1000

    plotter_options = {
        'imshow_options': {
            'origin': 'lower',  # showing array as image require to specifie that grater y goes upward
        },
        'colorbar_options': None
    }
    plotter_options = [{**plotter_options, 'title': _} for _ in titles]
    figure_options = {
            'colorbar_options': { 
            }
            }

    # make default font size smaller (default is 10)
    mpl.rcParams.update({'font.size': 8})
    p = Plotter(arrays, dat['ts'], x=x, y=y,
            plotter_options=plotter_options, figure_options=figure_options)
    p(outdir / 'test_mt2.png')

if __name__ == '__main__':
    # save better resolution image
    import matplotlib as mpl

    mpl.rcParams['savefig.dpi'] = 300
    # tester_md1()
    # tester_md2()
    # tester_md3()
    tester_md4()
    # tester_mt1()
    # tester_mt2()
    # tester_mt3()

