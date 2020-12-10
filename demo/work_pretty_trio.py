#!/usr/bin/env python3
import sys

sys.path.append('..')

from plotter import calpost_reader
import plotter.plotter_multi as plotter_multi
from plotter.plotter_util import LambertConformalTCEQ
from plotter.plotter_background import BackgroundManager

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

# input directory/file names
ddir = Path('../data')
# input file names
site = 'S2'
fnames = [
        'tseries_ch4_1min_conc_toy_all.dat',
        f'tseries_ch4_1min_conc_un_co_{site.lower()}.dat', # continuous upset
        f'tseries_ch4_1min_conc_un_pu_{site.lower()}.dat', # pulsate upset
        ]

# intermediate
wdir = Path('./img9')

# output
odir = Path('.')
oname = f'tseries_ch4_1min_conc_co_all_un_{site.lower()}.mp4'

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

# title to use for each input
titles = ['Regular Sources', f'Unintended,\nContinuous {site}',
          f'Unintended,\nPulsated {site}']

data = []
for fname in fnames:
    with open(ddir / fname) as f:
        dat = calpost_reader.Reader(f)
    data.append(dat)

# grab necessary info
arrays = [dat['v'] for dat in data]
tstamps = data[0]['ts']
grid = data[0]['grid']

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
arrays = [arr / 16.043 * 0.024465403697038 * 1e9 for arr in arrays]

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
                    fontsize=4
                    )
                # goes across all points but filter by Site_Label
                for _ in df_shp.itertuples() #if _.Site_Label in (f'{site}',)
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
saveone(16*60, (odir / oname).with_suffix('.png'))

run_parallel = True
if run_parallel:
    # parallel processing
    # save all frames in parallel
    # 68 for stampede, 24 for ls5
    nthreads = 24  # ls5
    with Pool(nthreads) as pool:
        pool.map(saveone, range(len(tstamps)))
else:
    # serial processing
    for i in range(len(tstamps)):
        saveone(i)

# make mpeg file
cmd = f'ffmpeg -i "{wdir / "%04d.png"}" -vf scale=1920:-2 -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y "{odir / oname}"'
subprocess.run(shlex.split(cmd), check=True)
