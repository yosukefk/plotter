#!/usr/bin/env python
import sys

plotterdir = './repo/plotter'
sys.path.insert(0, plotterdir)

from plotter import calpost_reader as cpr
from plotter import plotter_footnote as pf
import plotter.plotter_solo as plotter_solo
import plotter.plotter_multi as plotter_multi
from plotter.plotter_util import LambertConformalTCEQ
from plotter.plotter_background import BackgroundManager

import cartopy.io.img_tiles as cimgt

import matplotlib as mpl
import matplotlib.colors as colors

# save better resolution image 
mpl.use('Agg')
mpl.rcParams['savefig.dpi'] = 300

import numpy as np
from itertools import chain
from pathlib import Path

fname = '../calpost/tseries/tseries_ch4_1min_conc_toy_min_onesrc_3d_byweek_20190925_20190927.dat'
fname0 = '../calpost/tseries/tseries_ch4_1min_conc_toy_min_sys1_onesrc_byweek_20190925_20190927.dat'

oname = 'vprof_test.mp4'

# i have to provide coords for toy region because inconsitency in hrrr
# projection and ccalpuff projecton
xo = np.repeat(np.arange(34) * 0.1 - 464.35, 47)
yo = np.tile(np.arange(47) * 0.1 - 906.65, 34)

# this is what i did when i ran calpuff
zo = [2, 10, 30, 50, 80, 120]

dat = cpr.calpost_reader(fname, x=xo, y=yo, z=zo)  # , tslice=(60,None,None))
# dat0 = cpr.calpost_reader(fname0, x=xo, y=yo)

arr = dat['v']
ts = dat['ts']
grid = dat['grid']

# get horizontal extent 
extent = [
    grid['x0'], grid['x0'] + grid['nx'] * grid['dx'],
    grid['y0'], grid['y0'] + grid['ny'] * grid['dy'],
]

# distance in calpost is in km
extent = [_ * 1000 for _ in extent]
x = dat['x'] * 1000
y = dat['y'] * 1000

# convert unit of array from g/m3 tp ppb
# mwt g/mol
# molar volume m3/mol
arr = arr / 16.043 * 0.024465403697038 * 1e9

# Mrinali/Gary's surfer color scale
cmap = colors.ListedColormap([
    '#D6FAFE', '#02FEFF', '#C4FFC4', '#01FE02',
    '#FFEE02', '#FAB979', '#EF6601', '#FC0100', ])
cmap.set_under('#FFFFFF')
cmap.set_over('#000000')
# Define a normalization from values -> colors
bndry = [1, 10, 50, 100, 200, 500, 1000, 2000]
norm = colors.BoundaryNorm(bndry, len(bndry))
contour_options = {
        'levels': bndry,
        'cmap': cmap,
        'norm': norm,
        # 'alpha': .5,
        'extend': 'max',
    }
colorbar_options = {
        'label': r'$CH_4$ (ppbV)',
    }

if True:
    # solo, vprof

    # TODO check if this value is right
    idx = 25 - 1
    # idx = 25 - 1 + 1
    oname = f'vprof_test_idx{idx}.mp4'

    plotter_options = {
        'idx': idx,
        'title': f'vprof test, idx={idx}',
        'contour_options': contour_options,
        'colorbar_options': {
            'label': r'$CH_4$ (ppbV)',
        },
    }

    # make a plot template
    p = plotter_solo.Plotter(array=arr, tstamps=ts, 
                             z=zo, plotter_options=plotter_options)

    p.savefig(Path(oname).with_suffix('.0.png'), tidx=0)
    p.savefig(Path(oname).with_suffix('.1.png'), tidx=1)
    # p.savemp4(oname, wdir=None)

if True:
    # solo, horizontal
    kdx = 0
    plotter_options = {
        'kdx': 0,
        'background_manager': BackgroundManager(
            add_image_options=[cimgt.GoogleTiles(style='satellite'), 13],
            ),
        'title': f'vprof test, kdx=0',
        'contour_options': {k: v for k, v in chain(contour_options.items(),
                                                   {'alpha': .5}.items())},
        'colorbar_options': {
            'label': r'$CH_4$ (ppbV)',
        },
    }
    oname = f'vprof_test_kdx{kdx}.mp4'
    # make a plot template
    p = plotter_solo.Plotter(array=arr, tstamps=ts, x=x, y=y,
                             projection=LambertConformalTCEQ(),
                             z=zo, plotter_options=plotter_options)

    p.savefig(Path(oname).with_suffix('.png'), tidx=0)

if True:
    # duo vprof

    plotter_options = {
        # 'title': f'vprof test, idx={idx}',
        'contour_options': contour_options,
        'colorbar_options': None, 
        'footnote': '',
        # 'footnote_options': {'text':''},
    }
    figure_options = {
        'colorbar_options': {
            'label': r'$CH_4$ (ppbV)',
        },
        'footnote_options': {'text': "{tstamp}", 'y': .05},  # 'fontsize': 'small'},
    }

    listof_plotter_options = [plotter_options.copy(), plotter_options.copy()]
    listof_plotter_options[0].update({'idx': 24,
                                      'title': 'vprof test, idx=24'})
    listof_plotter_options[1].update({'idx': 25,
                                      'title': 'vprof test, idx=25'})

    oname = f'vprof_test_duo.mp4'
    # make a plot template
    p = plotter_multi.Plotter(arrays=[arr, arr], tstamps=ts,
                              z=zo, plotter_options=listof_plotter_options,
                              figure_options=figure_options)
    p.savefig(Path(oname).with_suffix('.png'), tidx=0)

if True:
    # trio vprof/horozontal

    plotter_options = {
        'contour_options': contour_options,
        'colorbar_options': None, 
        'footnote': '',
        # 'footnote_options': {'text':''},
    }
    figure_options = {
        'colorbar_options': {
            'label': r'$CH_4$ (ppbV)',
        },
        'footnote_options': {'text': "{tstamp}", 'y': .05},  # 'fontsize': 'small'},
        'figsize': (10, 4),
    }

    listof_plotter_options = [plotter_options.copy() for _ in range(3)]
    listof_plotter_options[0].update({'idx': 24,
                                      'title': 'vprof test, idx=24'})
    listof_plotter_options[1].update({'kdx': 0,
                                      'title': 'vprof test, surface',
                                      'background_manager': BackgroundManager( 
                                          add_image_options=[cimgt.GoogleTiles(style='satellite'),
                                                             13]),
                                      'contour_options': {k: v for k, v in chain(contour_options.items(),
                                                                                 {'alpha': .5}.items())},
                                      })
    listof_plotter_options[2].update({'idx': 25,
                                      'title': 'vprof test, idx=25'})

    oname = f'vprof_test_trio.mp4'
    # make a plot template
    p = plotter_multi.Plotter(arrays=[arr, arr, arr], tstamps=ts, x=x, y=y,
                              z=zo, plotter_options=listof_plotter_options,
                              figure_options=figure_options)
    p.savefig(Path(oname).with_suffix('.png'), tidx=0)
    p.savemp4(oname, wdir=None)
