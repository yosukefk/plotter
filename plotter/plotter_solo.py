try:
    from . import plotter_core as pc
except ImportError:
    import plotter_core as pc

import matplotlib.pyplot as plt
from importlib import reload

reload(pc)



class Plotter:
    def __init__(self, array, tstamps, projection=None, extent=None, x=None, y=None,
                 plotter_options={}):
        self.p = pc.PlotterCore(array, tstamps, projection=projection,
                                extent=extent, x=x, y=y, plotter_options=plotter_options)
        self.ax = self.p.ax

    def __call__(self, oname, tidx=None, footnote=''):
        self.p(tidx, footnote)
        plt.savefig(oname)

    def customize(self, fnc, *args):
        # plotter_core has per axis customization accessed:
        # things like showwin boundaries
        self.p.customize(fnc, *args)



def tester_r1():
    # show array
    import numpy as np
    import datetime
    arr = np.random.random(34*47).reshape(1,47, 34, )
    print(arr)
    ext = [-464400, -906700, -461000, -902000]
    p = Plotter(arr, [datetime.date(2020,12,4)], extent=ext)
    p('test_r1.png')

def tester_tr2():
    # show raster
    import rasterio
    import datetime
    r = rasterio.open('test2.tif')
    arr = r.read(1)
    arr = arr.reshape(1, *arr.shape)

    print(arr.shape)
    ext = [r.transform[2], r.transform[2] + r.transform[0] * r.width,
           r.transform[5] + r.transform[4] * r.height, r.transform[5]]
    print(ext)
    p = Plotter(arr, [datetime.date(2020,12,4)], extent=ext)
    p('test_tr2.png')

def tester_tc2():
    # show contour
    import rasterio
    import datetime
    r = rasterio.open('test2.tif')
    arr = r.read(1)
    arr = arr.reshape(1, *arr.shape)

    print(arr.shape)
    ext = [r.transform[2], r.transform[2] + r.transform[0] * r.width,
           r.transform[5] + r.transform[4] * r.height, r.transform[5]]
    print(ext)
    p = Plotter(arr, [datetime.date(2020,12,4)], extent=ext, plotter_options={'contour_options':{}})
    p('test_tc2.png')

def tester_tr3():
    # show raster with different projection
    import rasterio
    import datetime
    import cartopy.crs as ccrs
    r = rasterio.open('test2.tif')
    arr = r.read(1)
    arr = arr.reshape(1, *arr.shape)

    print(arr.shape)
    ext = [r.transform[2], r.transform[2] + r.transform[0] * r.width,
           r.transform[5] + r.transform[4] * r.height, r.transform[5]]

    b = rasterio.open('../resources/naip_pmerc_larger.tif')
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
           b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'extent': bext, 'projection':ccrs.epsg(3857)}

    p = Plotter(arr, [datetime.date(2020,12,4)], extent=ext, plotter_options=plotter_options)
    p('test_tr3.png')

def tester_tc3():
    # show contour with different projection
    import rasterio
    import datetime
    import cartopy.crs as ccrs
    r = rasterio.open('test2.tif')
    arr = r.read(1)
    arr = arr.reshape(1, *arr.shape)

    print(arr.shape)
    ext = [r.transform[2], r.transform[2] + r.transform[0] * r.width,
           r.transform[5] + r.transform[4] * r.height, r.transform[5]]

    b = rasterio.open('../resources/naip_pmerc_larger.tif')
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
           b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'contour_options': {}, 'extent': bext, 'projection':ccrs.epsg(3857)}

    p = Plotter(arr, [datetime.date(2020,12,4)], extent=ext, plotter_options=plotter_options)
    p('test_tc3.png')

def tester_tr4():
    # show raster with different projection background
    import rasterio
    import datetime
    import cartopy.crs as ccrs
    r = rasterio.open('test2.tif')
    arr = r.read(1)
    arr = arr.reshape(1, *arr.shape)

    print(arr.shape)
    ext = [r.transform[2], r.transform[2] + r.transform[0] * r.width,
           r.transform[5] + r.transform[4] * r.height, r.transform[5]]

    b = rasterio.open('../resources/naip_pmerc_larger.tif')
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
           b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'imshow_options': {'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    p = Plotter(arr, [datetime.date(2020,12,4)], extent=ext, plotter_options=plotter_options)
    plt.savefig('ooo.tif')
    p('test_tr4.png')

def tester_tc4():
    # show contour with different projection background
    import rasterio
    import datetime
    import cartopy.crs as ccrs
    import numpy as np
    r = rasterio.open('test2.tif')
    arr = r.read(1)
    arr = arr.reshape(1, *arr.shape)

    print(arr.shape)
    ext = [r.transform[2], r.transform[2] + r.transform[0] * r.width,
           r.transform[5] + r.transform[4] * r.height, r.transform[5]]
    x = (np.arange(r.width) + .5) * r.transform[0] + r.transform[2]
    y = (np.arange(r.height) + .5) * r.transform[4] + r.transform[5]

    b = rasterio.open('../resources/naip_pmerc_larger.tif')
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
           b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'contour_options': {'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    p = Plotter(arr, tstamps=[datetime.date(2020,12,4)], extent=ext, plotter_options=plotter_options)
    p('test_tc4.png')


def tester_pr2a():
    import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    g = dat['grid']
    ext = [g['x0'], g['x0'] + g['nx'] * g['dx'],
           g['y0'], g['y0'] + g['ny'] * g['dy'],]
    # distance in calpost is in km
    ext = [_*1000 for _ in ext]

    plotter_options = {
        'imshow_options' : {
            'origin': 'lower', # showing array as image require to specifie that grater y goes upward
        }
    }
    p = Plotter(dat['v'], dat['ts'], extent=ext,
                plotter_options=plotter_options)
    p('test_pr2a.png')

def tester_pr2b():
    import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    plotter_options = {
        'imshow_options' : {
            'origin': 'lower', # showing array as image require to specifie that grater y goes upward
        }
    }

    # since calpost tells x,y coordinates of each point, it is easier just pass those coords
    # dont forget that calpost has distance in km
    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p('test_pr2b.png')

def tester_pc2():
    import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    plotter_options = { 'contour_options' :{}}
    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x = x, y=y,
                plotter_options=plotter_options)
    p('test_pc2.png')

def tester_pr3():
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open('../resources/naip_pmerc_larger.tif')
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
           b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'extent': bext, 'projection':ccrs.epsg(3857),
                       'imshow_options': {'origin': 'lower',  }
                       }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x = x, y=y, plotter_options=plotter_options)
    p('test_pr3.png')

def tester_pc3():
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open('../resources/naip_pmerc_larger.tif')
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
           b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'extent': bext, 'projection':ccrs.epsg(3857),
                       'contour_options': {}}

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x = x, y=y, plotter_options=plotter_options)
    p('test_pc3.png')

def tester_pr4():
    # show raster with different projection background
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open('../resources/naip_pmerc_larger.tif')
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
           b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'imshow_options': {'origin': 'lower', 'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p('test_pr4.png')

def tester_pc4():
    # show contour with different projection background
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open('../resources/naip_pmerc_larger.tif')
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
           b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'contour_options': {'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x = x, y=y, plotter_options=plotter_options)
    p('test_pc4.png')



if __name__ == '__main__':
    # tester_r1()
    # tester_tr2() # this sometime fails, when done in series with others, weird...
    # tester_tc2()
    # tester_tr3()
    # tester_tc3()
    # tester_tr4()
    # tester_tc4()
    #
    tester_pr2a()
    tester_pr2b() # this sometime fails, when done in series with others, weird...
    tester_pc2()
    tester_pr3()
    tester_pc3()
    tester_pr4()
    tester_pc4()
