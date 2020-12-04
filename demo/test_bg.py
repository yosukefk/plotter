#!/usr/bin/env python3

import calpost_reader as reader
import sys

sys.path.append('..')
from plotter import plotter_solo as psolo
from cartopy.io.img_tiles import GoogleTiles
import matplotlib as mpl
import matplotlib.pylab as plt

try:
    import gdal
except ModuleNotFoundError:
    from osgeo import gdal
gdal.UseExceptions()
from importlib import reload

reload(psolo)

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

p = psolo.Plotter(arr, dat['ts'], extent=ext)
# the number is "zoom level"
# i found max i can go is 22, but it still ugly
# p.ax.add_image(GoogleTiles(), 22)#, alpha=.1)
# p.ax.add_image(GoogleTiles(style='satellite'), 22)#, alpha=.1)

# https://ocefpaf.github.io/python4oceanographers/blog/2015/03/02/geotiff/
ds = gdal.Open('../resources/gamma3_res2.tif')
data = ds.ReadAsArray()
gt = ds.GetGeoTransform()
projection = p.ax.projection  # i know they match
extent = (gt[0], gt[0] + ds.RasterXSize * gt[1],
          gt[3] + ds.RasterYSize * gt[5], gt[3])
print(extent)
extent = p.ax.get_xlim() + p.ax.get_ylim()
print(extent)

p('o.png')
p.ax.imshow(data[:3, :, :].transpose((1, 2, 0)), extent=extent,
            origin='upper', alpha=0.2)

plt.savefig('p.png')

# i may get image from NAIP or something and use it as background?
