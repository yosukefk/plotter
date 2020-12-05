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


# TODO make these into unittest

bgfile = '../resources/naip_toy_pmerc_5.tif'
shpfile = '../resources/emitters.shp'


def tester_r1():
    # show array
    import numpy as np
    import datetime
    arr = np.random.random(34 * 47).reshape(1, 47, 34, )
    print(arr)
    ext = [-464400, -906700, -461000, -902000]
    p = Plotter(arr, [datetime.date(2020, 12, 4)], extent=ext)
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
    p = Plotter(arr, [datetime.date(2020, 12, 4)], extent=ext)
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
    p = Plotter(arr, [datetime.date(2020, 12, 4)], extent=ext, plotter_options={'contour_options': {}})
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

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'extent': bext, 'projection': ccrs.epsg(3857)}

    p = Plotter(arr, [datetime.date(2020, 12, 4)], extent=ext, plotter_options=plotter_options)
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

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'contour_options': {}, 'extent': bext, 'projection': ccrs.epsg(3857)}

    p = Plotter(arr, [datetime.date(2020, 12, 4)], extent=ext, plotter_options=plotter_options)
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

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'imshow_options': {'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    p = Plotter(arr, [datetime.date(2020, 12, 4)], extent=ext, plotter_options=plotter_options)
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

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'contour_options': {'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    p = Plotter(arr, tstamps=[datetime.date(2020, 12, 4)], extent=ext, plotter_options=plotter_options)
    p('test_tc4.png')


def tester_pr2a():
    import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    g = dat['grid']
    ext = [g['x0'], g['x0'] + g['nx'] * g['dx'],
           g['y0'], g['y0'] + g['ny'] * g['dy'], ]
    # distance in calpost is in km
    ext = [_ * 1000 for _ in ext]

    plotter_options = {
        'imshow_options': {
            'origin': 'lower',  # showing array as image require to specifie that grater y goes upward
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
        'imshow_options': {
            'origin': 'lower',  # showing array as image require to specifie that grater y goes upward
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

    plotter_options = {'contour_options': {}}
    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y,
                plotter_options=plotter_options)
    p('test_pc2.png')


def tester_pr3():
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'extent': bext, 'projection': ccrs.epsg(3857),
                       'imshow_options': {'origin': 'lower', }
                       }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p('test_pr3.png')


def tester_pc3():
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'extent': bext, 'projection': ccrs.epsg(3857),
                       'contour_options': {}}

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p('test_pc3.png')


def tester_pr4():
    # show raster with different projection background
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open(bgfile)
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

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'contour_options': {'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p('test_pc4.png')


def tester_s1a():
    import cartopy.crs as ccrs
    import geopandas as gpd
    import numpy as np
    import datetime

    # tried cartopy.io.shapereader.Reader, fiona.open but
    # geopanda probably makes most sense
    df = gpd.read_file(shpfile)

    arr = np.zeros(34 * 47).reshape(1, 47, 34, )
    ext = [-101.90, -101.86, 31.71, 31.75]
    plotter_options = {
        'imshow_options': None,
        'contour_options': None,
        'projection': ccrs.PlateCarree(),
        'extent' : [-101.90, -101.86, 31.71, 31.75],
        'customize_once': [
            lambda p: p.ax.scatter(df.geometry.x, df.geometry.y, color='r', marker='o'),
            # lambda p: p.ax.set_xticks(np.arange(-101.90, -101.86, 0.01), crs=ccrs.PlateCarree()),
            lambda p: p.ax.gridlines(draw_labels=True),
        ]
    }
    p = Plotter(arr, [datetime.date(2020, 12, 4)], extent=ext, projection=ccrs.PlateCarree(),
                plotter_options=plotter_options)
    p('test_s1a.png')

def tester_s1b():
    import cartopy.crs as ccrs
    import geopandas as gpd
    import numpy as np
    import datetime

    # tried cartopy.io.shapereader.Reader, fiona.open but
    # geopanda probably makes most sense
    df = gpd.read_file(shpfile)

    arr = np.zeros(34 * 47).reshape(1, 47, 34, )
    ext = [-101.90, -101.86, 31.71, 31.75]
    plotter_options = {
        'imshow_options': None,
        'contour_options': None,
        'projection': ccrs.PlateCarree(),
        'extent' : [-101.90, -101.86, 31.71, 31.75],
        'customize_once': [
            lambda p: df.plot(ax=p.ax, column='kls', categorical=True, legend=True),
            # seems like i have to iterate over records and add label.  Also, position of label, leadline etc,
            # i still need to search some tool for that, or manally adjust position which i dont want to...
            lambda p: [p.ax.annotate(_.Site_Label, (_.geometry.x, _.geometry.y)) for _ in df.itertuples()
                       if _.Site_Label in ('F1', 'op3_w1', 'S4')],
            lambda p: p.ax.gridlines(draw_labels=True),
        ]
    }
    p = Plotter(arr, [datetime.date(2020, 12, 4)], extent=ext, projection=ccrs.PlateCarree(),
                plotter_options=plotter_options)
    p('test_s1b.png')

def tester_s2():
    import calpost_reader as reader
    import geopandas as gpd

    df = gpd.read_file(shpfile)
    df = df.to_crs('+proj=lcc +lat_1=33 +lat_2=45 +lat_0=40 +lon_0=-97 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m +no_defs')

    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    plotter_options = {
        'contour_options': {},
        'customize_once': [
            lambda p: df.plot(ax=p.ax, column='kls', categorical=True, legend=True, zorder=10),
            lambda p: [p.ax.annotate(_.Site_Label, (_.geometry.x, _.geometry.y)) for _ in df.itertuples()
                       if _.Site_Label in ('F1', 'op3_w1', 'S4')],
            lambda p: p.ax.gridlines(draw_labels=True),
        ]
    }
    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y,
                plotter_options=plotter_options)
    p('test_s2.png')

def tester_s3():
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    import geopandas as gpd

    df = gpd.read_file(shpfile)
    df = df.to_crs('EPSG:3857')

    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {'extent': bext, 'projection': ccrs.epsg(3857),
                       'contour_options': {},
                       'customize_once': [
                           lambda p: df.plot(ax=p.ax, column='kls', categorical=True, legend=True, zorder=10),
                           lambda p: [p.ax.annotate(_.Site_Label, (_.geometry.x, _.geometry.y)) for _ in df.itertuples()
                                      if _.Site_Label in ('F1', 'op3_w1', 'S4')],
                           lambda p: p.ax.gridlines(draw_labels=True),
                       ]
                       }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p('test_s3.png')


def tester_s4():
    # show contour with different projection background
    import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    import geopandas as gpd

    df = gpd.read_file(shpfile)
    df = df.to_crs('EPSG:3857')

    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'contour_options': {'alpha': .5},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': [
            lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper'),
            lambda p: df.plot(ax=p.ax, column='kls', categorical=True, legend=True, zorder=10),
            lambda p: [p.ax.annotate(_.Site_Label, (_.geometry.x, _.geometry.y)) for _ in df.itertuples()
                       if _.Site_Label in ('F1', 'op3_w1', 'S4')],
            lambda p: p.ax.gridlines(draw_labels=True),
        ]}

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p('test_s4.png')



if __name__ == '__main__':
    # save better resolution image
    import matplotlib as mpl

    mpl.rcParams['savefig.dpi'] = 300

    # tester_r1()
    # tester_tr2() # this sometime fails, when done in series with others, weird...
    # tester_tc2()
    # tester_tr3()
    # tester_tc3()
    # tester_tr4()
    # tester_tc4()
    #
    # tester_pr2a()
    # tester_pr2b()  # this sometime fails, when done in series with others, weird...
    # tester_pc2()
    # tester_pr3()
    # tester_pc3()
    # tester_pr4()
    # tester_pc4()

    # tester_s1a()
    # tester_s1b()
    # tester_s2()
    # tester_s3()
    tester_s4()
