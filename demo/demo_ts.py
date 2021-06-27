#!/usr/bin/env python
import sys

plotterdir = './repo/plotter'
sys.path.insert(0, plotterdir)

from plotter.reader import reader, get_format
import plotter.plotter_solo as plotter_solo

import matplotlib.colors as colors

import numpy as np
from pathlib import Path

fnames = [
    '/scratch1/01923/ling/hysplit/hysplit.v5.0.0_CentOS/scripts/outconc.S2.const.hrrr.2m75kghr.txt',
    '/scratch1/00576/yosuke/projects/astra/calpuff/work_yk/toy_mmif/calpost/tseries/tseries_ch4_1min_conc_toy_min_sys1_onesrc_byweek_20190925_20190927.dat',
]

fmts = [get_format(fn[0]) if isinstance(fn, list) else get_format(fn) for fn in fnames]

# i have to provide coords for toy region because inconsitency in hrrr
# projection and calpuff projecton
xc = np.repeat(np.arange(34) * 0.1 - 464.35, 47)
yc = np.tile(np.arange(47) * 0.1 - 906.65, 34)

# above should work for hysplit, but i did differently (linear location of x
# and y, instead of all points' x,y)
xh = np.arange(34) * 0.1 - 464.35
yh = np.arange(47) * 0.1 - 906.65


xs = []
ys = []
dats = []
for fn, fmt in zip(fnames, fmts):
    print(fmt)
    x = {'calpost': xc, 'hysplit': xh}[fmt] 
    y = {'calpost': yc, 'hysplit': yh}[fmt] 
    dat = reader(fn, x=x, y=y)
    xs.append(dat['x'])
    ys.append(dat['y'])
    dats.append(dat)

# find common time period
tstamps = [_['ts'] for _ in dats]

if tstamps[0][0] < tstamps[1][0]:
    s0 = np.where(tstamps[1][0] == tstamps[0])
    s1 = 0
    print('s0', s0)
    assert len(s0) == 1
    s0 = int(s0[0])
else:
    s1 = np.where(tstamps[0][0] == tstamps[1])
    s0 = 0
    print('s1', s1)
    assert len(s1) == 1
    s1 = int(s1[0])

if tstamps[0][-1] < tstamps[1][-1]:
    e1 = np.where(tstamps[0][-1] == tstamps[1])
    e0 = None
    print('e1', e1)
    assert len(e1) == 1
    e1 = int(e1[0]) + 1
else:
    e0 = np.where(tstamps[1][-1] == tstamps[0])
    e1 = None
    print('e0', e0)
    assert len(e0) == 1
    e0 = int(e0[0]) + 1

assert np.all(tstamps[0][s0:e0] == tstamps[1][s1:e1])

# extract necessary data
arrays = [dat['v'][s:e] for dat, s, e in zip(dats, (s0, s1), (e0, e1))]
tss = [ts[s:e] for ts, s, e in zip(tstamps, (s0, s1), (e0, e1))]
ts = tstamps[0][s0:e0]

# conversion factors
convfacs = [{'calpost': 1. / 16.043 * 0.024465403697038 * 1e9, 
             'hysplit': 1., }[_] for _ in fmts]

arrays = [arr*cf for arr, cf in zip(arrays, convfacs)]

# array has nan, so mask them
arrays = [np.ma.masked_invalid(arr) for arr in arrays]

dct_arrays = {k: v for k, v in zip(fmts, arrays)}

# # calpost knows location but hysplit needt to be told
# xs = [{'calpost': None, 'hysplit': get_receptor_coords.df.x}[_] for _ in
#       fmts]
# ys = [{'calpost': None, 'hysplit': get_receptor_coords.df.y}[_] for _ in
#       fmts]
#
# dats = [reader(fn, x=x, y=y,)
#         for fn, x, y in zip(fnames, xs, ys)]

if True:
    # solo, ts
    plotter_options = {'tseries': True}
    oname = 'ts_test.mp4'
    p = plotter_solo.Plotter(array=dct_arrays, tstamps=ts, 
                             plotter_options=plotter_options)
    p.savefig(Path(oname).with_suffix('.png'))
    p.savemp4(oname, wdir=None)

import plotter.plotter_multi as plotter_multi
from plotter.plotter_util import LambertConformalTCEQ
from plotter.plotter_background import BackgroundManager
import cartopy.io.img_tiles as cimgt

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
        'alpha': .5,
        'extend': 'max',
    }
colorbar_options = {
        'label': r'$CH_4$ (ppbV)',
    }

if True:
    tile_plotter_options = {
        'background_manager': BackgroundManager(
            add_image_options=[cimgt.GoogleTiles(style='satellite'), 13],
            ),
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

    listof_plotter_options = [
        tile_plotter_options.copy(),
        {'tseries': True},
        tile_plotter_options.copy(),
    ]
    listof_plotter_options[0].update({
        'title': 'Hysplit',
    })
    listof_plotter_options[2].update({
        'title': 'Calpuff',
    })

    oname = 'ts_test_trio.mp4'

    assert np.all(xs[0] == xs[1])
    assert np.all(ys[0] == ys[1])

    p = plotter_multi.Plotter(arrays=[dct_arrays['hysplit'], dct_arrays,
                                      dct_arrays['calpost']], tstamps=ts,
                              x=xs[0]*1000, y=ys[0]*1000,
                              projection=LambertConformalTCEQ(),
                              plotter_options=listof_plotter_options,
                              figure_options=figure_options)

    p.savefig(Path(oname).with_suffix('.png'), tidx=10)
    p.savemp4(oname, wdir=None)
