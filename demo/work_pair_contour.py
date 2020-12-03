#!/usr/bin/env python3
import sys
sys.path.append('..')

import calpost_reader as reader
import plotter.plotter_multi as plotter_multi


import matplotlib as mpl
import matplotlib.colors as colors

from pathlib import Path
from importlib import reload
from multiprocessing import Pool
import shlex
import subprocess


reload(reader)
reload(plotter_multi)

# save better resolution image 
mpl.rcParams['savefig.dpi'] = 300

# input directory/file names
ddir = Path('../data')
fname = 'tseries_ch4_1min_conc_co_fl.dat'

# intermediate
wdir = Path('./img5')
odir = wdir

# output
odir = Path('.')
oname = 'tseries_ch4_1min_conc_co_fl_cnt.mp4'

titles = ['raster', 'contour']

if not wdir.is_dir():
    wdir.mkdir()
else:
    for f in wdir.glob('*.png'):
        try:
            f.unlink()
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))


# read the data
with open(ddir /fname) as f:
    dat = reader.Reader(f)

# grab necessary info
arr = dat['v']
tstamps = dat['ts']
grid = dat['grid']

# get horizontal extent 
extent = [
    grid['x0'], 
    grid['x0'] + grid['nx']*grid['dx'], 
    grid['y0'], 
    grid['y0'] + grid['ny']*grid['dy'], 
    ]
extent = [_*1000 for _ in extent]
print(extent)

# convert unit of array from g/m3 tp ppb
# g/m3 to ppb
# arr is in g/m3
# mwt g/mol
# molar volume m3/mol
arr = arr / 16.043 * 0.024465403697038 * 1e9

# surfer's color scale
cmap = colors.ListedColormap([
    '#D6FAFE',
    '#02FEFF',
    '#C4FFC4',
    '#01FE02',
    '#FFEE02',
    '#FAB979',
    '#EF6601',
    '#FC0100',])
cmap.set_under('#FFFFFF')
## Define a normalization from values -> colors
bndry = [1,10,50,100,200,500,1000,2000]
norm = colors.BoundaryNorm(bndry, len(bndry))

imshow_options = { 
        'cmap' : cmap, 
        'norm' : norm, 
        }
contour_options = {
        'levels' : bndry, 
        'cmap': cmap, 
        'norm': norm,
    }


plotter_options = [
        {
            'imshow_options': imshow_options, 
            'title' : titles[0],
            'colorbar_options': None,
            },
        {
            'contour_options': contour_options, 
            'title' : titles[1],
            'colorbar_options': None,
            },
        ]

figure_options = {
        'colorbar_options' : {},  # default common color bar 
        }

# make a plot template
p = plotter_multi.Plotter(arrays = [arr[..., -1::-1, :], arr], tstamps = tstamps, extent=extent,
        plotter_options = plotter_options, figure_options=figure_options)

# function to save one time frame
def saveone(i):
    ts = tstamps[i]
    #oname = wdir / ts.strftime('img-%m%d%H%M.png')
    oname = wdir / f'{i:04}.png'
    #footnote = ts.strftime('%Y-%m-%d %H:%M')
    #footnote = str(ts)
    footnote = None
    suptitle = str(ts)
    #p(oname, tidx=i, footnote=footnote)#, suptitle={'t':suptitle, 'y':0.02})
    #p(oname, tidx=i, footnote=footnote, suptitle={'t':suptitle})#, 'y':0.02, 'va': 'bottom'})
    # this y=0.2  is magic number..  0.3 will put suptitle inside plot, and
    # smaller y makes huge gap between plot and suptitle
    p(oname, tidx=i, footnote=footnote, suptitle={'t':suptitle, 'y':0.2, 'va': 'top'})

# save all frames in parallel
# 68 for stampede, 24 for ls5
with Pool(24) as pool:
    pool.map(saveone,range(len(tstamps)))

# make mpeg file
#cmd = f'ffmpeg                     -i {wdir}/%04d.png                   -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y { odir / oname }'
cmd = f'ffmpeg                     -i {wdir}/%04d.png -vf scale=1920:-2 -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y { odir / oname }'
subprocess.run(shlex.split(cmd))


