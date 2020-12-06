#!/usr/bin/env python3
import sys
sys.path.append('..')

from plotter import calpost_reader as reader
import plotter.plotter_solo as plotter_solo
from plotter.plotter_util import lcc_tceq

import rasterio
import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib as mpl
import matplotlib.colors as colors
from shapely.geometry import Polygon
from adjustText import adjust_text

from pathlib import Path
from importlib import reload
from multiprocessing import Pool
import shlex
import subprocess

reload(reader)
reload(plotter_solo)

# save better resolution image 
mpl.rcParams['savefig.dpi'] = 300

# input directory/file names
ddir = Path('../data')
fname = 'tseries_ch4_1min_conc_co_fl.dat'

# intermediate
wdir = Path('./img')

# output
odir = Path('.')
oname = 'tseries_ch4_1min_conc_co_fl.mp4'

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


# background (extent is used as plot's extent)
b = rasterio.open(bgfile)
bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
        b.transform[5] + b.transform[4] * b.height, b.transform[5]]

# source locations
df = gpd.read_file(shpfile)
df = df.to_crs('EPSG:3857')

# read the data
title = 'Flare'

with open(ddir / fname) as f:
    dat = reader.Reader(f)

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
# Define a normalization from values -> colors
bndry = [1, 10, 50, 100, 200, 500, 1000, 2000]
norm = colors.BoundaryNorm(bndry, len(bndry))

plotter_options = {
    'extent': bext, 'projection': ccrs.epsg(3857),
    'title': title,
    'contour_options': {
        'levels': bndry,
        'cmap': cmap,
        'norm': norm,
        'alpha': .5,
    },
    'colorbar_options': {
        'label': r'$CH_4$ (ppbV)',
    },
    'customize_once': [
        # background
        lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                              extent=bext, origin='upper'),
        # emission points
        lambda p: df.plot(ax=p.ax, column='kls', categorical=True, legend=False, zorder=10,
                          markersize=2,
                          # got red/blue/yellow from colorbrewer's Set1
                          cmap=colors.ListedColormap(['#e41a1c', '#377eb8', '#ffff33'])),
        # emission point annotations
        lambda p: 
            # adjust_text() repels labels from each other
            adjust_text(
            # make list of annotation
            list(
                # this part creates annotation for each point
                p.ax.text(_.geometry.x, _.geometry.y, _.Site_Label, zorder=11, size=6)
                # goes across all points but filter by Site_Label
                for _ in df.itertuples() if _.Site_Label in ('F1', 'op3_w1', 'S4')
            ),
        ),
        # modeled box
        lambda p: p.ax.add_geometries(
            [Polygon([(extent[x],extent[y]) for x,y in ((0,2), (0,3), (1,3), (1,2), (0,2))])],
            crs=lcc_tceq, facecolor='none', edgecolor='white', lw=.6,
        ),
    ]}

# make a plot template
p = plotter_solo.Plotter(array=arr, tstamps=tstamps, x=x, y=y,
                         plotter_options=plotter_options)


# function to save one time frame
def saveone(i):
    ts = tstamps[i]
    pname = wdir / f'{i:04}.png'
    footnote = str(ts)
    p(pname, tidx=i, footnote=footnote)


# save all frames in parallel
# 68 for stampede, 24 for ls5
nthreads = 24  # ls5
with Pool(nthreads) as pool:
    pool.map(saveone, range(len(tstamps)))

# make mpeg file
cmd = f'ffmpeg -i {wdir}/%04d.png -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y {odir / oname}'
subprocess.run(shlex.split(cmd))
