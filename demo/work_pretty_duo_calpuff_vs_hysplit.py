#!/usr/bin/env python3
import sys

sys.path.append('..')

from plotter import hysplit_reader
from plotter import calpost_reader
import plotter.plotter_multi as plotter_multi
from plotter.plotter_util import LambertConformalTCEQ
from plotter.plotter_background import BackgroundManager

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
fnames = [ 
        'tseries_ch4_1min_conc_un_pu_s2.dat',
        'outconc.S2.pulse.NAM.txt',
        ]

# intermediate
wdir = Path('./img')

# output
odir = Path('.')
oname = 'calpuff_vs_hysplit_pulsate_s2.mp4'

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
bgfile = '../resources/naip_toy_pmerc_5.tif'
shpfile = '../resources/emitters.shp'


# source locations
df_shp = gpd.read_file(shpfile)
df_shp = df_shp.to_crs('EPSG:3857')

# title to use
titles = ['Calpuff', 'Hysplit']

data = [None, None]
# read calpuff
with open(ddir / fnames[0]) as f:
    data[0] = calpost_reader.Reader(f)

# read hysplit
with open(ddir / fnames[1]) as f:
    x = np.arange(34)*0.1 -464.35
    y = np.arange(47)*0.1 -906.65
    data[1] = hysplit_reader.Reader(f, x=x, y=y)

# grab necessary info
assert data[1]['ts'][60] == data[0]['ts'][0]
arrays = [ 
        data[0]['v'][:23*60],
        data[1]['v'][60:],
        ]
tstamps = data[0]['ts'][:23*60]
grid = data[0]['grid']

# get horizontal extent 
extent = [
    grid['x0'], grid['x0'] + grid['nx'] * grid['dx'],
    grid['y0'], grid['y0'] + grid['ny'] * grid['dy'],
]

# distance in calpost is in km
extent = [_ * 1000 for _ in extent]
x = data[0]['x'] * 1000
y = data[0]['y'] * 1000

assert data[0]['units'] == 'g/m**3'
# convert unit of array from g/m3 tp ppb
# mwt g/mol
# molar volume m3/mol
arrays[0] = arrays[0] / 16.043 * 0.024465403697038 * 1e9
assert data[1]['units'] == 'ppb'


# Mrinali/Gary's surfer color scale
cmap = colors.ListedColormap([
    '#D6FAFE', '#02FEFF', '#C4FFC4', '#01FE02',
    '#FFEE02', '#FAB979', '#EF6601', '#FC0100', ])
cmap.set_under('#FFFFFF')
cmap.set_over('#000000')
# Define a normalization from values -> colors
bndry = [1, 10, 50, 100, 200, 500, 1000, 2000]
norm = colors.BoundaryNorm(bndry, len(bndry))

plotter_options = {
    'background_manager': BackgroundManager(bgfile=bgfile,),
    'contour_options': {
        'levels': bndry,
        'cmap': cmap,
        'norm': norm,
        'alpha': .5,
        'extend': 'max',
    },
    'title_options': {'fontsize': 'medium'},
    'colorbar_options': None,
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
                    fontsize=4,
                    )
                # goes across all points but filter by Site_Label
                for _ in df_shp.itertuples()
            ),
        ),
        # modeled box
        lambda p: p.ax.add_geometries(
            [Polygon([(extent[x], extent[y]) for x, y in ((0, 2), (0, 3), (1, 3), (1, 2), (0, 2))])],
            crs=LambertConformalTCEQ(), facecolor='none', edgecolor='white', lw=.6,
        ),

    ]}

# clone the options and let each has own title
plotter_options = [{**plotter_options, 'title': title} for title in titles]

# colorbar goes to entire figure
figure_options = {
    'colorbar_options': {
        'label': r'$CH_4$ (ppbV)',
        }
    }

# make a plot template
p = plotter_multi.Plotter(arrays=arrays, tstamps=tstamps, 
                         x=x, y=y, projection=LambertConformalTCEQ(),
                         plotter_options=plotter_options,
                         figure_options=figure_options)


# function to save one time frame
def saveone(i, pname=None):
    if pname is None: pname = wdir / f'{i:04}.png'

    ts = tstamps[i]
    footnote = str(ts)
    p(pname, tidx=i, footnote=footnote)

# make single image file (for QA)
saveone(min(16*60, len(tstamps)-1), (odir / oname).with_suffix('.png'))

# you decide if you want to use many cores
# parallel processing
# save all frames in parallel
# 68 for stampede, 24 for ls5
nthreads = 24  # ls5

# except that you are on login node
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
cmd = f'ffmpeg -i "{wdir / "%04d.png"}" -vf scale=1920:-2 -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y "{odir / oname}"'
subprocess.run(shlex.split(cmd), check=True)
