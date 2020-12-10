#!/usr/bin/env python3
import sys

sys.path.append('..')

from plotter import calpost_reader
import plotter.plotter_multi as plotter_multi
from plotter.plotter_util import LambertConformalTCEQ
from plotter_background import BackgroundManager

import geopandas as gpd
import matplotlib as mpl
import matplotlib.colors as colors
from shapely.geometry import Polygon
from adjustText import adjust_text

from pathlib import Path
from multiprocessing import Pool
import shlex
import subprocess

# save better resolution image
mpl.rcParams['savefig.dpi'] = 300

# input directory
ddir = Path('../../data')
# input file names
site = 'S2'
fnames = [
    'tseries_ch4_1min_conc_toy_all.dat',
    f'tseries_ch4_1min_conc_un_co_{site.lower()}.dat',  # continuous upset
    f'tseries_ch4_1min_conc_un_pu_{site.lower()}.dat',  # pulsate upset
]

# intermediates
wdir = Path('./img8')

# output
odir = Path('../results')
oname = f'example_pretty2.mp4'

# prep workdir
if not wdir.is_dir():
    wdir.mkdir()
else:
    for f in wdir.glob('*.png'):
        try:
            f.unlink()
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))

# aux input files:  background image and point shapefile of sources
bgfile = '../../resources/naip_toy_pmerc_5.tif'
shpfile = '../../resources/emitters.shp'

# source locations, read the shape file, and change projection to PseudoMercator (same as GoogleMap)
df_shp = gpd.read_file(shpfile)
df_shp = df_shp.to_crs('EPSG:3857')

# title to use for each input
titles = [
    'Regular Only',
    f'Regular +\nUnintended,\nContinous {site}',
    f'Regular +\nUnintended,\nPulsated {site}',
]

# read the input, using calpost_reader.Reader()
data = []
for fname in fnames:
    with open(ddir / fname) as f:
        # i am using only 16:00 to 16:10, for demo purpose
        dat = calpost_reader.Reader(f, tslice=slice(16 * 60, 16 * 60 + 10))
    data.append(dat)

# grab necessary info
arrays = [dat['v'] for dat in data]
tstamps = data[0]['ts']
grid = data[0]['grid']

# get horizontal extent
# by matplotlib's convention, extent is expresses as [x0, x1, y0, y1]
extent = [
    grid['x0'], grid['x0'] + grid['nx'] * grid['dx'],
    grid['y0'], grid['y0'] + grid['ny'] * grid['dy'],
]

# distance in calpost output is in km.  change that to meters
extent = [_ * 1000 for _ in extent]
x = dat['x'] * 1000
y = dat['y'] * 1000

# convert mass unit  from g/m3 tp ppb
# mwt g/mol
# molar volume m3/mol
arrays = [arr / 16.043 * 0.024465403697038 * 1e9 for arr in arrays]

# sum of regular and unintended emission
arrays[1] += arrays[0]
arrays[2] += arrays[0]

# Reproduce Mrinali/Gary's surfer color scale
# matplotlib.colors.ListedColormap
# https://matplotlib.org/api/_as_gen/matplotlib.colors.ListedColormap.html
# https://matplotlib.org/tutorials/colors/colormap-manipulation.html
cmap = colors.ListedColormap([
    '#D6FAFE', '#02FEFF', '#C4FFC4', '#01FE02',
    '#FFEE02', '#FAB979', '#EF6601', '#FC0100', ])
# also setting colors for under/overflow
cmap.set_under('#FFFFFF')
cmap.set_over('#000000')

# Define a normalization from values -> colors
# https://matplotlib.org/api/_as_gen/matplotlib.colors.BoundaryNorm.html
# https://matplotlib.org/tutorials/colors/colormapnorms.html
bndry = [1, 10, 50, 100, 200, 500, 1000, 2000]
norm = colors.BoundaryNorm(bndry, len(bndry))

# options passed to each of three plots
plotter_options = {
    # plotter_backgrond.BackgroundManager() controls extend and background of the plot
    'background_manager': BackgroundManager(bgfile=bgfile),

    # options passed to Axes.contourf()
    # https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.contourf.html
    # https://matplotlib.org/gallery/images_contours_and_fields/contour_demo.html
    'contour_options': {
        'levels': bndry,
        'cmap': cmap,
        'norm': norm,
        'alpha': .5,
        'extend': 'max',
    },

    # options passed to Axes.set_title()
    # https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.set_title.html#matplotlib.axes.Axes.set_title
    'title_options': {'fontsize': 'medium'},

    # turned off colorbar for individual plot
    'colorbar_options': None,

    # series of functions applied to PlotterCore
    'customize_once': [

        # emission points
        # using geopandas.GeoDataFrame.plot()
        # https://geopandas.org/reference.html#geopandas.GeoDataFrame.plot
        # https://geopandas.org/mapping.html
        lambda p: df_shp.plot(ax=p.ax, column='kls', categorical=True, legend=False, zorder=10,
                              markersize=2,
                              # got red/blue/yellow from colorbrewer's Set1
                              cmap=colors.ListedColormap(['#e41a1c', '#377eb8', '#ffff33'])
                              ),

        # emission point annotations
        # using GeoAxes.annotate(), which is subclass of matplotlib's Axes.annotate()
        # https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.annotate.html#matplotlib.axes.Axes.annotate
        # I also used adjust_text() repels labels from each other (not as fancy as GIS program would do)
        # https://adjusttext.readthedocs.io/en/latest/
        # lim=30 tells that give it up after 30 itereations (default 500)
        lambda p:
        adjust_text(
            # make list of annotation
            list(
                # this part creates annotation for each point
                p.ax.annotate(_.Site_Label, (_.geometry.x, _.geometry.y,),
                              zorder=11,
                              fontsize=4,
                              # fontsize=4,
                              )
                # goes across all points but filter by Site_Label
                for _ in df_shp.itertuples()), # if _.Site_Label.startswith(('F', 'S'))),
            lim=30
        ),

        # showing modeling extent
        # using GeoAxes.add_geometries()
        # https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.add_geometries
        # I am constructing rectangle using shapely.geometry.Polygon(), using the extent i read from input file
        lambda p: p.ax.add_geometries(
            [Polygon([(extent[x], extent[y]) for x, y in ((0, 2), (0, 3), (1, 3), (1, 2), (0, 2))])],
            crs=LambertConformalTCEQ(), facecolor='none', edgecolor='white', lw=.6,
        ),

    ]}

# clone the plotter_options into three, and let each has its own title
plotter_options = [{**plotter_options, 'title': title} for title in titles]

# figure options affects figure as a whole (not to each of three plots)
# Plotter always uses plt.figure() to create Figure first, then use add_subplot() method to create plot
# (Axes in matplotlib terms). figure_options will work on this Figure, like plotter_option mostly worked on plot (Axes)
figure_options = {
    # One colorbar for the entire figure
    # passed as arguments to Figure.colorbar()
    # https://matplotlib.org/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.colorbar
    # also using mathematical mode with $ sign
    # https://matplotlib.org/tutorials/text/mathtext.html
    'colorbar_options': {
        'label': r'$CH_4$ (ppbV)',
    }
}

# make a "multi" version of Plotter, having multiple cores
p = plotter_multi.Plotter(arrays=arrays, tstamps=tstamps,
                          x=x, y=y, projection=LambertConformalTCEQ(),
                          plotter_options=plotter_options,
                          figure_options=figure_options)


# function to save one time frame
def saveone(i, pname=None):
    # if png name is not specified, use a serial number and put into workdir
    if pname is None: pname = wdir / f'{i:04}.png'

    ts = tstamps[i]
    footnote = str(ts)

    # calling plotter with png file name, with time index, saves an image
    p(pname, tidx=i,
      footnote=footnote)


# make single image file (for QA)
saveone(0, (odir / oname).with_suffix('.png'))

# save images for all time frames
run_parallel = False
if run_parallel:
    # for parallel processing
    # save all frames in parallel
    # 68 for stampede, 24 for ls5
    nthreads = 24  # ls5
    with Pool(nthreads) as pool:
        pool.map(saveone, range(len(tstamps)))
else:
    # for serial processing, make image one by one
    for i in range(len(tstamps)):
        saveone(i)

# make mpeg file
# I asked TACC guy for tips for making animation from series of files.
cmd = f'ffmpeg -i "{wdir / "%04d.png"}" -vf scale=1920:-2 -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y "{odir / oname}"'
subprocess.run(shlex.split(cmd), check=True)
