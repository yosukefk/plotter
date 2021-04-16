#!/usr/bin/env python3
import sys

plotterdir = '..'
sys.path.append(plotterdir)

from plotter import calpost_reader
import plotter.plotter_solo as plotter_solo
from plotter.plotter_util import LambertConformalTCEQ
from plotter.plotter_background import BackgroundManager

import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib as mpl
import matplotlib.colors as colors
from shapely.geometry import Polygon
from adjustText import adjust_text

import numpy as np

from pathlib import Path
from multiprocessing import Pool
import shlex
import subprocess
import socket

# save better resolution image 
mpl.rcParams['savefig.dpi'] = 300

# input directory/file names
ddir = Path('../data')
# input file name
fname = 'tseries_ch4_1min_conc_toy_all.dat'

# intermediate
wdir = Path('./img')

# output
odir = Path('.')
oname = 'tseries_ch4_1min_conc_toy_all_nobg.mp4'

# prep workdir
if not wdir.is_dir():
    wdir.mkdir()
else:
    for f in wdir.glob('*.png'):
        try:
            f.unlink()
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))

# aux inputs
bgfile = Path(plotterdir) / 'resources/naip_toy_pmerc_5.tif'
shpfile = Path(plotterdir)  / 'resources/emitters.shp'


# source locations
df_shp = gpd.read_file(shpfile)
df_shp = df_shp.to_crs('EPSG:3857')

# title to use
title = 'Regular Sources'

with open(ddir / fname) as f:
    dat = calpost_reader.Reader(f)

# grab necessary info
arr = dat['v']
tstamps = dat['ts']
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

def add_gridlines(ax, attrs):
    gl = ax.gridlines()
    for k,v in attrs.items():
        setattr(gl, k, v)

plotter_options = {
        # no background, just use google map's projection with large extent
    'background_manager': BackgroundManager(projection=ccrs.Mercator.GOOGLE,
        extent=[-11344200., -11338900., 3724300., 3731100.]),
    'title': title,
    'contour_options': {
        'levels': bndry,
        'cmap': cmap,
        'norm': norm,
        'alpha': .5,
        'extend': 'max',
    },
    'colorbar_options': {
        'label': r'$CH_4$ (ppbV)',
    },
    'customize_once': [
        # emission points
        lambda p: df_shp.plot(ax=p.ax, column='kls', categorical=True, legend=False, zorder=10,
                          markersize=2,
                          # got red/blue/yellow from colorbrewer's Set1
                          cmap=colors.ListedColormap(['#e41a1c', '#377eb8', '#ffff33'])
                          ),

        # emission point annotations
        lambda p: 
            # adjust_text() repels labels from each other
            adjust_text(
            # make list of annotation
            list(
                # this part creates annotation for each point
                p.ax.annotate(_.Site_Label, (_.geometry.x, _.geometry.y,),
                    zorder=11, 
                    fontsize='xx-small',
                    )
                # goes across all points but filter by Site_Label
                for _ in df_shp.itertuples()
            ),
        ),
        # modeled box
        lambda p: p.ax.add_geometries(
            [Polygon([(extent[x], extent[y]) for x, y in ((0, 2), (0, 3), (1, 3), (1, 2), (0, 2))])],
            crs=LambertConformalTCEQ(), facecolor='none', edgecolor='black', lw=.6,
        ),
        # grid lines
        lambda p: add_gridlines(p.ax, {'bottom_labels': False,
            'right_labels':False})

    ]}

# make a plot template
p = plotter_solo.Plotter(array=arr, tstamps=tstamps, 
                         x=x, y=y, projection=LambertConformalTCEQ(),
                         plotter_options=plotter_options)


# function to save one time frame
def saveone(i, pname=None):
    #if pname is None: pname = wdir / f'{i:04}.png'
    if pname is None: pname = wdir / png_fmt_py.format(i)

    ts = tstamps[i]
    footnote = str(ts)
    p.savefig(pname, tidx=i, footnote=footnote)

ntsteps = len(tstamps)
# '{:04d}.png' for python
# '%04d.png' for shell
png_fmt_py = '{:0' + str(int(np.log10(ntsteps) + 1)) + 'd}.png'
png_fmt_sh = '%0' + str(int(np.log10(ntsteps) + 1)) + 'd.png'

# make single image file (for QA)
saveone(min(16*60, ntsteps-1), (odir / oname).with_suffix('.png'))

# you decide if you want to use many cores
# parallel processing
# save all frames in parallel
# 68 for stampede, 24 for ls5
nthreads = 24  # ls5

# except that you are on TACC login node
hn = socket.getfqdn()
if hn.startswith('login') and '.tacc.' in hn:
    ntheads = 1

if nthreads > 1:
    with Pool(nthreads) as pool:
        pool.map(saveone, range(len(tstamps)))
else:
    # serial processing
    for i in range(len(tstamps)):
        saveone(i)

# make mpeg file
#cmd = f'ffmpeg -i "{wdir / "%04d.png"}" -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y "{odir / oname}"'
cmd = f'ffmpeg -i "{wdir / png_fmt_sh }" -vframes {ntsteps} -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y "{odir / oname}"'
subprocess.run(shlex.split(cmd), check=True)
