#!/usr/bin/env python
import sys
plotterdir = './repo/plotter'
sys.path.insert(0, plotterdir)

from plotter.reader import reader, get_format

import plotter.plotter_multi as plotter_multi
from plotter.plotter_util import LambertConformalHRRR
from plotter.plotter_background import BackgroundManager

import matplotlib as mpl
import matplotlib.colors as colors

# save better resolution image 
mpl.use('Agg')
mpl.rcParams['savefig.dpi'] = 300


import pandas as pd
from io import StringIO

from shapely.geometry import Polygon
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

# from importlib import reload
import numpy as np
from pathlib import Path

import argparse

import get_receptor_coords


def read_what_to_do():

    p = argparse.ArgumentParser(
            description='tell me what tsereis file to process, you get mp4')

#    # this would be way to use multiple files in series for one scenario
#    p.add_argument('-i', '--input', help='(series of) input tseries files',
#                   type=str, nargs='+', action='append')

#    # list of tseries file, each file is treated as one time series
#    p.add_argument('input', help='input tseries files',
#                   type=str, nargs='+')

    # list of tseries file, each file is treated as one time series
    p.add_argument('input', help='input tseries files',
                   type=str, nargs=2)

    # output file name (mp4)
    p.add_argument('-o', '--output', 
                   help='output mp4 file name', 
                   default='animation.mp4', 
                   type=str,
                   )

    # embedded title to use
    p.add_argument('-t', '--title', 
                   help='title to use', 
                   default=None, 
                   type=str,
                   )


    args = p.parse_args()
    return args

# read command line options
args = read_what_to_do()

fnames = args.input
oname = args.output
title = args.title


fmts = [get_format(fn) for fn in fnames]

titles = [{'calpost': 'Calpuff', 'hysplit': 'Hysplit'}[_] for _ in fmts]

# calpost knows location but hysplit needt to be told
xs = [{'calpost': None, 'hysplit': get_receptor_coords.df.x}[_] for _ in
      fmts]
ys = [{'calpost': None, 'hysplit': get_receptor_coords.df.y}[_] for _ in
      fmts]

dats = [reader(fn, x=x, y=y,)
        for fn,x,y in zip(fnames, xs, ys)]

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
arrays = [dat['v'] for dat,s,e in zip(dats, (s0,s1), (e0,e1))]
ts = tstamps[0][s0:e0]
grid = dats[0]['grid']




# get horizontal extent 
extent = [
    grid['x0'], grid['x0'] + grid['nx'] * grid['dx'],
    grid['y0'], grid['y0'] + grid['ny'] * grid['dy'],
]

# convet distance to km
extent = [_ * 1000 for _ in extent]
x = dats[0]['x'] * 1000
y = dats[0]['y'] * 1000

# conversion factors
convfacs = [{'calpost': 1. / 16.043 * 0.024465403697038 * 1e9, 
             'hysplit': 1., }[_] for _ in fmts]

arrays = [arr*cf for arr,cf in zip(arrays, convfacs)]

# array has nan, so mask them
arrays = [np.ma.masked_invalid(arr) for arr in arrays]


# Ready to GO !!!

# Mrinali/Gary's surfer color scale
cmap = colors.ListedColormap([
    '#D6FAFE', '#02FEFF', '#C4FFC4', '#01FE02',
    '#FFEE02', '#FAB979', '#EF6601', '#FC0100', ])
cmap.set_under('#FFFFFF')
cmap.set_over('#000000')
# Define a normalization from values -> colors
bndry = [1, 10, 50, 100, 200, 500, 1000, 2000]
norm = colors.BoundaryNorm(bndry, len(bndry))


# receptor box defined by Shanon
df_corners = pd.read_csv(StringIO(
'''
box,lon,lat
receptor,-102.14119642699995,31.902587319000077
receptor,-102.06890715999998,31.928683642000067
receptor,-102.03957186099996,31.873156213000073
receptor,-102.11577420099997,31.85033867900006
receptor,-102.14119642699995,31.902587319000077
emitter,-102.1346819997111,31.80019199958484
emitter,-102.0045175208385,31.83711037948465
emitter,-102.046423081171,31.94509160994673
emitter,-102.1790300003915,31.90254999960113
emitter,-102.1346819997111,31.80019199958484
'''.strip()))
receptor_corners = df_corners.loc[df_corners['box'] == 'receptor', ['lon','lat']].values

plotter_options = {
    'background_manager': BackgroundManager(
        add_image_options=[cimgt.GoogleTiles(style='satellite'), 13],
        ),
    'contour_options': {
        'levels': bndry,
        'cmap': cmap,
        'norm': norm,
        'alpha': .5,
        'extend': 'max',
    },
    'colorbar_options': None,
    'footnote_options': {
        'text': "Min({imn}, {jmn}) = {vmn:.1f}, Max({imx}, {jmx}) = {vmx:.1f}",
        'fontsize': 'x-small',
    },
    'customize_once': [
        # add recetptor box
        lambda p: p.ax.add_geometries(
            [Polygon([_ for _ in receptor_corners])],  # four corners into polygon
            crs = ccrs.PlateCarree(),  # projection is unprojected ("PlateCarre")
            facecolor='none', edgecolor='black', lw=.6,  # plot styles
            ),

    ]}

# colorbar goes to entire figure
figure_options = {
    'colorbar_options': {
        'label': r'$CH_4$ (ppbV)',
        },
    'footnote_options': {'text': "{tstamp}"},
    'suptitle': title,
    }

# clone the options and let each has own title
plotter_options = [{**plotter_options, 'title': title} for title in titles]

# make a plot template
p = plotter_multi.Plotter(arrays, tstamps=ts, 
                         x=x, y=y, projection=LambertConformalHRRR(),
                         plotter_options=plotter_options,
                          figure_options=figure_options)

p.savefig(Path(oname).with_suffix('.png'), tidx=0)
p.savemp4(oname, wdir=None)
#p.savemp4(oname, wdir='./wdir')
