try:
    from . import plotter_core as pc
except ImportError:
    import plotter_core as pc

import matplotlib.pyplot as plt
from importlib import reload

reload(pc)



class Plotter:
    def __init__(self, array, tstamps, projection=None, extent=None,
                 plotter_options={}):
        self.p = pc.PlotterCore(array, tstamps, projection, extent, plotter_options)
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

def tester_r2():
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
    p('test_r2.png')

def tester_c2():
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
    p('test_c2.png')

def tester_r3():
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
    p('test_r3.png')

def tester_r4():
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
    p('test_r4.png')

def tester_c4():
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
        'contour_options': {'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    p = Plotter(arr, [datetime.date(2020,12,4)], extent=ext, plotter_options=plotter_options)
    plt.savefig('ooo.tif')
    p('test_c4.png')

if __name__ == '__main__':
#    tester_r1()
    tester_r2()
    tester_c2()
#    tester_r3()
#    tester_r4()
    tester_c4()