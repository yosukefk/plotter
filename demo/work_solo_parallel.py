#!/usr/bin/env python3
import sys
sys.path.append('..')

import calpost_reader as reader
import plotter.plotter_solo as plotter_solo


import matplotlib as mpl
import matplotlib.colors as colors

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
odir = wdir

# output
odir = Path('.')
oname = 'tseries_ch4_1min_conc_co_fl.mp4'

title = 'Flare'

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

# array need to flip upside down...
arr = arr[..., -1::-1, :]

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

plotter_options = {
        'imshow_options': {
            'cmap': cmap,
            'norm': norm,
            },
        'title': title,
        }

# make a plot template
p = plotter_solo.Plotter(array = arr, tstamps = tstamps, extent=extent,
        plotter_options = plotter_options)

# function to save one time frame
def saveone(i):
    ts = tstamps[i]
    #oname = wdir / ts.strftime('img-%m%d%H%M.png')
    oname = wdir / f'{i:04}.png'
    footnote = str(ts)
    p(oname, tidx=i, footnote=footnote)

# save all frames in parallel
# 68 for stampede, 24 for ls5
with Pool(24) as pool:
    pool.map(saveone,range(len(tstamps)))

# make mpeg file
cmd = f'ffmpeg -i {wdir}/%04d.png -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y { odir / oname }'
subprocess.run(shlex.split(cmd))

