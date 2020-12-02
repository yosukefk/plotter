#!/usr/bin/env python3

import reader
import plotter_multi
import plotter_util as pu


import matplotlib as mpl
import matplotlib.colors as colors

from pathlib import Path
from importlib import reload
from multiprocessing import Pool
import subprocess
import shlex
#import psutil

reload(reader)
reload(plotter_multi)

# save better resolution image 
mpl.rcParams['savefig.dpi'] = 300

# input directory/file names
ddir = Path('../calpost')
fnames = [
        'tseries_ch4_1min_conc_co_fl.dat',
        'tseries_ch4_1min_conc_co_cip.dat',
        'tseries_ch4_1min_conc_co_tank.dat',
        ]


# intermediate
wdir = Path('./img2')

# output
odir = Path('.')
oname = 'tseries_ch4_1min_conc_co_trio.mpeg'

titles = ['Flare', 'CIP', 'Tank']

if not wdir.is_dir():
    wdir.mkdir()
else:
    for f in wdir.glob('*.png'):
        try:
            f.unlink()
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))


# read the data
data = []
for fname in fnames:
    with open(ddir / fname) as f:
        dat = reader.reader(f)
    data.append(dat)

# grab necessary info
arrays = [dat['v'] for dat in data]
tstamps = data[0]['ts']
grid = data[0]['grid']

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
arrays = [arr / 16.043 * 0.024465403697038 * 1e9 for arr in arrays]

# array need to flip upside down...
arrays = [arr[..., -1::-1, :] for arr in arrays]

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


bga = pu.background_adder( 'gamma3_res2.tif')


plotter_options = [
        { 
            'imshow_options': imshow_options, 
            'title' : ttle,
            'colorbar_options': None, # not to show cbar for each plot
#            'customize_after': bga,
            } for ttle in titles]
figure_options = {
        'colorbar_options' : {},  # default common color bar 
        }

# make a plot template
p = plotter_multi.plotter(arrays = arrays, tstamps = tstamps, extent=extent,
        plotter_options = plotter_options, figure_options = figure_options)

# function to save one time frame
def saveone(i):
    ts = tstamps[i]
    #oname = wdir / ts.strftime('img-%m%d%H%M.png')
    oname = wdir / f'{i:04}.png'
    footnote = ts.strftime('%Y-%m-%d %H:%M')
    p(oname, tidx=i, footnote=footnote)

# save all frames in parallel
nthreads = 68 # i overheard this # is good for stampede2
with Pool(nthreads) as pool:
    pool.map(saveone,range(len(tstamps)))

# make mpeg file
# this -threads didnt make it any faster... maybe ffmpeg optimizes itself??
#cmd = f'ffmpeg -threads {nthreads} -i {wdir}/%04d.png -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y { odir / oname }'
cmd = f'ffmpeg                     -i {wdir}/%04d.png -vf scale=1920:-2 -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y { odir / oname }'
subprocess.run(shlex.split(cmd))

