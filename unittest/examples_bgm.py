import sys

sys.path.append('..')

from plotter.plotter_solo import Plotter
from plotter.plotter_background import BackgroundManager
from plotter.plotter_util import LambertConformalTCEQ
from pathlib import Path

bgfile = '../resources/naip_toy_pmerc_5.tif'
bgfile_lcc = '../resources/gamma3_res2.tif'
# bgfile_lcc = '../resources/naip_lcc_larger.tif'

outdir = Path('results')
if not outdir.is_dir():
    outdir.mkdir()

def tester_bgm_n0():
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
    p(outdir / 'test_bgm_n0.png')


def tester_bgm_n1():
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
    p(outdir / 'test_bgm_n1.png')

def tester_bgm_n2():
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
    p(outdir / 'test_bgm_n2.png')


def tester_bgm_n3():
    """specify  only projection without bg image"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(projection=ccrs.epsg(3857)),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm_n3.png')


def tester_bgm_n4():
    """specify only extent without bg image"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(extent=[-465000.0, -460000.0, -902000.0, -907000.0]), # lcc extent larger than modeling
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm_n4.png')


def tester_bgm_b1a():
    """background file, dont have to tell its projection"""
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
    p(outdir / 'test_bgm_b1a.png')

def tester_bgm_b1b():
    """background file, telling what projection it has in case if they cant figure out"""
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
    p(outdir / 'test_bgm_b1b.png')

def tester_bgm_b1c():
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
    p(outdir / 'test_bgm_b1c.png')


def tester_bgm_b2a():
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
            projection=LambertConformalTCEQ(),
            extent=[-465000.0, -460000.0, -902000.0, -907000.0]),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm_b2a.png')

def tester_bgm_b2b():
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
    p(outdir / 'test_bgm_b2b.png')


def tester_bgm_b3():
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
        ),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm_b3.png')




















def tester_bgm_b4a():
    """background file, already processed to pseudo mercator, zoom in"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    plotter_options = {
        'contour_options': {'alpha': .2},
        'background_manager': BackgroundManager(
            bgfile=bgfile,
            extent=[-11342000, -11341000, 3727000, 3728000]),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm_b4a.png')


def tester_bgm_b4b():
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
    p(outdir / 'test_bgm_b4b.png')

def tester_bgm_w1():
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
    p(outdir / 'test_bgm_w1.png')


def tester_bgm_w2a():
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
    p(outdir / 'test_bgm_w2a.png')

def tester_bgm_w2b():
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
    p(outdir / 'test_bgm_w2b.png')

def tester_bgm_w2c():
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
    p(outdir / 'test_bgm_w2c.png')

def tester_bgm_w3():
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
        ),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm_w3.png')

def tester_bgm_w4():
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
            extent=[-11344200.0, -11338900.0, 3724300.0, 3731100.0]),
        'customize_once': lambda p: p.ax.gridlines(draw_labels=True),
    }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bgm_w4.png')


if __name__ == '__main__':


    tester_bgm_n0()
    tester_bgm_n1()
    tester_bgm_n2()
    tester_bgm_n3()
    tester_bgm_n4()

    tester_bgm_b1a()
    tester_bgm_b1b()
    tester_bgm_b1c()
    tester_bgm_b2a()
    tester_bgm_b2b()
    tester_bgm_b3()
    tester_bgm_b4a()
    tester_bgm_b4b()

    tester_bgm_w1()
    tester_bgm_w2a()
    tester_bgm_w2b()
    tester_bgm_w2c()
    tester_bgm_w3()
    tester_bgm_w4()
