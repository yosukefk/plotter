#!/usr/bin/env python
import sys

plotterdir = '..'
#plotterdir = './repo/plotter'
sys.path.insert(0, plotterdir)

from plotter import calpost_reader as cpr
from plotter import plotter_reader as pr
from plotter import  plotter_footnote as pf
import plotter.hysplit_coords as hsc
import plotter.plotter_solo as plotter_solo
import plotter.plotter_multi as plotter_multi
import plotter.plotter_util as pu
from plotter.plotter_background import BackgroundManager

import cartopy.io.img_tiles as cimgt

import cartopy.crs as ccrs

import matplotlib as mpl
import matplotlib.colors as colors

# save better resolution image 
mpl.use('Agg')
mpl.rcParams['savefig.dpi'] = 300

import numpy as np
from itertools import chain
from pathlib import Path

from importlib import reload
reload(pr)

ddir = Path(plotterdir) / 'data'
resourcedir = Path(plotterdir) / 'resources'


# grid def...
#rname_toy = '../../scripts/toy_model_allstations.txt'
rname_toy = resourcedir / 'toy_model_allstations.txt'
grid_toy = {'x0': -464.4, 'y0': -906.7,
             'nx': 34, 'ny': 47,
             'dx': 0.1, 'dy': 0.1}
hsc_toy = hsc.HysplitReceptorCoords(rname_toy, grid_toy, pu.LambertConformalTCEQ())

#fname_calpuff = '/scratch1/00576/yosuke/projects/astra/calpuff/work_yk/toy_mmif/calpost/tseries/tseries_ch4_1min_conc_toy_min_onesrc_3d_byweek_20190925_20190927.dat'
#fname_hysplit = [
#    f'../../scripts/outconc.S2.const.hrrr.2m75kghr.3d.station_{_+1}.txt' for _ in range(11)]
fname_calpuff = ddir / 'tseries_ch4_1min_conc_toy_min_onesrc_3d_byweek_20190925_20190927.dat'
fname_hysplit = [
    ddir / f'outconc.S2.const.hrrr.2m75kghr.3d.station_{_+1}.txt' for _ in range(11)]

pt_s2 = (-101.8762665,31.7313145)

oname = f'vprof_toy_hextet_hysplit_vs_calpuff_sep.mp4'

# i have to provide coords for toy region because inconsitency in hrrr
# projection and ccalpuff projecton
xo = np.repeat(np.arange(34)*0.1 -464.35, 47)
yo = np.tile(np.arange(47)*0.1 -906.65, 34)

# this is what i did when i ran calpuff
zo = [2, 10, 30, 50, 80, 120]

dat_cp = cpr.calpost_reader(fname_calpuff, x=xo, y=yo, z=zo)
dat_hs = pr.reader(fname_hysplit, rdx_map=hsc_toy)

dats = [dat_hs, dat_cp]

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


# convert unit of array from g/m3 tp ppb
# mwt g/mol
# molar volume m3/mol
arrays[1] = arrays[1] / 16.043 * 0.024465403697038 * 1e9
# no change for hysplit
arrays[0] = arrays[0]



# get horizontal extent 
extent = [
    grid['x0'], grid['x0'] + grid['nx'] * grid['dx'],
    grid['y0'], grid['y0'] + grid['ny'] * grid['dy'],
]

# distance in calpost is in km
extent = [_ * 1000 for _ in extent]
x = dats[0]['x'] * 1000
y = dats[0]['y'] * 1000

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
#        'alpha': .5,
        'extend': 'max',
    }
colorbar_options = {
        'label': r'$CH_4$ (ppbV)',
    }

# hextet vprof/horozontal

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
    #'footnote_options': {'text': "{tstamp}", 'y':.05},  #'fontsize': 'small'},
    'footnote_options': {'text': "{tstamp}", 'y':.01},  #'fontsize': 'small'},
#    'figsize': (10,4),
}



x24 = float((x[24]+x[23]) * .5)
x25 = float((x[25]+x[24]) * .5)


listof_plotter_options = [plotter_options.copy() for _ in range(6)]

listof_plotter_options[0].update({
    'idx' : 24, 
    # 'title': 'Hysplit, vprof idx=24',
    'customize_once': [
        lambda q: q.ax.text(.05, .95, f'idx = 24',
                            ha='left', va='top',
                            transform=q.ax.transAxes),
        lambda q: q.ax.set_ylabel('height (m AGL)'), 
        lambda q: q.ax.set_xticks([]),
    ], 
})

listof_plotter_options[1].update({
    'kdx' : 0, 
    # 'title': 'Hysplit, surface',
    'title': 'Hysplit', 
    'background_manager': BackgroundManager( 
        add_image_options=[cimgt.GoogleTiles(style='satellite'), 
                           13]), 
    'contour_options': { k:v for k,v in chain(
        contour_options.items(), 
        {'alpha':.5}.items())
    },
    'customize_once': [ 
        lambda q: q.ax.set_anchor((.5, .5)), 
        lambda q: q.ax.axvline(x24, zorder=1, linewidth=.5, color='white', alpha=.5),
        lambda q: q.ax.axvline(x25, zorder=1, linewidth=.5, color='white', alpha=.5),
        lambda q: q.ax.scatter([pt_s2[0]], [pt_s2[1]],
                               transform=ccrs.PlateCarree(),
                               color='white',marker='x',),
    ], 
})

listof_plotter_options[2].update( {
    'idx' : 25, 
     # 'title': 'Hysplit, vprof, idx=25',
    'customize_once': [ 
        lambda q: q.ax.text(.05, .95, f'idx = 25',
                            ha='left', va='top',
                            transform=q.ax.transAxes),
        lambda q: q.ax.set_yticks([]), 
        lambda q: q.ax.set_xticks([]),
    ], 
})

listof_plotter_options[3].update({
    'idx' : 24, 
    #'title': 'Calpuff, vprof idx=24',
    'customize_once': [
        lambda q: q.ax.text(.05, .95, f'idx = 24',
                            ha='left', va='top',
                            transform=q.ax.transAxes),
        lambda q: q.ax.set_xticks([y.min(), y.max()]),
        lambda q: q.ax.set_xticklabels(['0', '4.7']),
        lambda q: q.ax.set_xlabel('northing (km)'), 
        lambda q: q.ax.set_ylabel('height (m AGL)'), 
    ], 
})

listof_plotter_options[4].update({
    'kdx' : 0, 
    #'title': 'Calpuff, surface', 
    'title': 'Calpuff', 
    'background_manager': BackgroundManager( 
        add_image_options=[cimgt.GoogleTiles(style='satellite'), 
                           13]), 
    'contour_options': {k:v for k,v in chain(
        contour_options.items(), 
        {'alpha':.5}.items()) 
                        }, 
    'customize_once': [ 
        lambda q: q.ax.set_anchor((.5, .5)), 
        lambda q: q.ax.axvline(x24, zorder=1, linewidth=.5, color='white', alpha=.5),
        lambda q: q.ax.axvline(x25, zorder=1, linewidth=.5, color='white', alpha=.5),
        lambda q: q.ax.scatter([pt_s2[0]], [pt_s2[1]],
                               transform=ccrs.PlateCarree(),
                               color='white',marker='x',),
    ], 
})

listof_plotter_options[5].update({
    'idx' : 25, 
    #'title': 'Calpuff, vprof, idx=25', 
    'customize_once': [ 
        lambda q: q.ax.text(.05, .95, f'idx = 25',
                            ha='left', va='top',
                            transform=q.ax.transAxes),
        lambda q: q.ax.set_xticks([y.min(), y.max()]),
        lambda q: q.ax.set_xticklabels(['0', '4.7']),
        lambda q: q.ax.set_xlabel('northing (km)'), 
        lambda q: q.ax.set_yticks([]), 
    ], 
})

# make a plot template
p = plotter_multi.Plotter(arrays=[arrays[0], arrays[0], arrays[0],
                                  arrays[1], arrays[1], arrays[1]], tstamps=ts, x=x, y=y,
                         z=zo, plotter_options=listof_plotter_options,
                          figure_options=figure_options)

p.savefig(Path(oname).with_suffix('.png'), tidx=0)
p.savefig(Path(oname).with_suffix('.60.png'), tidx=60)
p.savemp4(oname, wdir=None, nthreads=24)
