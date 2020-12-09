import sys

sys.path.append('..')

from plotter.plotter_solo import Plotter
from plotter.plotter_util import BackgroundManager, LambertConformalTCEQ
from pathlib import Path

bgfile = '../resources/naip_toy_pmerc_5.tif'
bgfile_lcc = '../resources/gamma3_res2.tif'

outdir = Path('results')
if not outdir.is_dir():
    outdir.mkdir()

def tester_bgm0():
    """no background or anything"""
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm0.png')


def tester_bgm1():
    """null background"""
    from plotter import calpost_reader as reader
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm1.png')


def tester_bgm2():
    """background file, telling what projection it has"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(bgfile=bgfile,
                                                source_projection=ccrs.epsg(3857)),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm2.png')

def tester_bgm3():
    """background file, already processed to pseudo mercator"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(bgfile=bgfile),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm3.png')

def tester_bgm4():
    """background file, TCEQ lcc"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(bgfile=bgfile_lcc),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),

    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm4.png')

def tester_bgm5():
    """specify extent/projection without bg image"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(projection=ccrs.epsg(3857),
                                                extent=[-11344200.0, -11338900.0, 3724300.0, 3731100.0]),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm5.png')

def tester_bgm6():
    """background file, already processed to pseudo mercator, zoom in"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    bgm = BackgroundManager(bgfile=bgfile)
    ext = bgm.extent
    bgm.extent = [
        2/3*ext[0]+1/3*ext[1], 1/3*ext[0]+2/3*ext[1],
        2 / 3 * ext[2] + 1 / 3 * ext[3], 1 / 3 * ext[2] + 2 / 3 * ext[3],
    ]

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': bgm,
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm6.png')

def tester_bgm7():
    """specify extent/projection and bg image"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(
            bgfile=bgfile_lcc,
            projection=ccrs.epsg(3857),
                                                extent=[-11344200.0, -11338900.0, 3724300.0, 3731100.0]),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm7.png')

def tester_bgm8():
    """wms, specify projection/extent"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(wms_options = {
            'wms': 'https://services.nationalmap.gov/arcgis/services/USGSNAIPImagery/ImageServer/WMSServer',
            'layers':'0'},
            projection=ccrs.epsg(3857),
            extent=[-11344200.0, -11338900.0, 3724300.0, 3731100.0]),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm8.png')

def tester_bgm9():
    """specify projection/extent, then wms"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(
            projection=ccrs.epsg(3857),
            extent=[-11344200.0, -11338900.0, 3724300.0, 3731100.0]),
        'customize_once': [
            lambda p: p.ax.add_wms(
                'https://services.nationalmap.gov/arcgis/services/USGSNAIPImagery/ImageServer/WMSServer',
                layers='0'),
            lambda p: p.ax.gridlines(draw_labels=True),
        ]

    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm9.png')

def tester_bgm10():
    """wms, specify projection/extent lcc"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(wms_options = {
            'wms': 'https://services.nationalmap.gov/arcgis/services/USGSNAIPImagery/ImageServer/WMSServer',
            'layers':'0'},
            projection= LambertConformalTCEQ(),
            extent=[-465000, -460000, -908000, -901000]),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm10.png')

def tester_bgm11():
    """only specify wms, use data's projection/extent"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(wms_options = {
            'wms': 'https://services.nationalmap.gov/arcgis/services/USGSNAIPImagery/ImageServer/WMSServer',
            'layers':'0'},),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm11.png')



if __name__ == '__main__':
    # tester_bgm0()
    tester_bgm1()
    # tester_bgm2()
    # tester_bgm3()
    # tester_bgm4()
    # tester_bgm5()
    # tester_bgm6()
    # tester_bgm7()
    # tester_bgm8()
    # tester_bgm9()
    # tester_bgm10()
    # tester_bgm11()