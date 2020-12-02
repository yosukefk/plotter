import reader
import plotter_solo as psolo
from cartopy.io.img_tiles import GoogleTiles
import matplotlib as mpl
import matplotlib.pylab as plt
import gdal
from importlib import reload
import plotter_util as pu
reload(psolo)
reload(pu)

# save better resolution image 
mpl.rcParams['savefig.dpi'] = 300

fname = '../calpost/tseries_ch4_1min_conc_co_fl.dat'
with open(fname) as f:
    dat = reader.reader(f, slice(60*12, 60*12+1))

g = dat['grid']
ext = (g['x0'], g['x0'] + g['dx']*g['nx'],
g['y0'], g['y0'] + g['dy']*g['ny'])
ext = [_*1000 for _ in ext]
print(ext)

arr = dat['v'][:,::-1,:]

#https://ocefpaf.github.io/python4oceanographers/blog/2015/03/02/geotiff/
bga = pu.background_adder('gamma3_res2.tif')

p = psolo.plotter(arr, dat['ts'], extent=ext,
        plotter_options={
            'customize_after': bga})


p('q.png')

# i may get image from NAIP or something and use it as background?


