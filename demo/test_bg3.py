#!/usr/bin/env python3

import sys

sys.path.append('..')
from plotter import plotter_solo as psolo, calpost_reader as reader
import matplotlib as mpl
from importlib import reload
from plotter import plotter_util as pu

reload(psolo)
reload(pu)

# save better resolution image 
mpl.rcParams['savefig.dpi'] = 300

fname = '../data/tseries_ch4_1min_conc_co_fl.dat'
with open(fname) as f:
    dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 1))

g = dat['grid']
ext = (g['x0'], g['x0'] + g['dx'] * g['nx'],
       g['y0'], g['y0'] + g['dy'] * g['ny'])
ext = [_ * 1000 for _ in ext]
print(ext)

arr = dat['v'][:, ::-1, :]

# https://ocefpaf.github.io/python4oceanographers/blog/2015/03/02/geotiff/
bga = pu.background_adder('../resources/gamma3_res2.tif')

p = psolo.Plotter(arr, dat['ts'], extent=ext,
                  plotter_options={
                      'customize_once': bga.set_background,
                      'customize_after': bga.refresh_background,
                  })

p('r.png')

# i may get image from NAIP or something and use it as background?
