import sys

sys.path.append('..')

from plotter.plotter_solo import Plotter
from pathlib import Path

bgfile = '../resources/naip_toy_pmerc_5.tif'

outdir = Path('results')
if not outdir.is_dir():
    outdir.mkdir()



def tester_bg1():
    """load background tif file and use it"""
    from plotter import calpost_reader as reader
    import rasterio
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    b = rasterio.open(bgfile)
    bext = [b.transform[2], b.transform[2] + b.transform[0] * b.width,
            b.transform[5] + b.transform[4] * b.height, b.transform[5]]
    plotter_options = {
        'contour_options': {'alpha': .2},
        'extent': bext, 'projection': ccrs.epsg(3857),
        'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
                                                extent=bext, origin='upper')}

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bg1.png')


def tester_bg2():
    """load background tif file and use extent without showing it"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    bext = [-11344200.0, -11338900.0, 3724300.0, 3731100.0]
    plotter_options = {
        'contour_options': {'alpha': .2},
        'extent': bext, 'projection': ccrs.epsg(3857),
        # 'customize_once': lambda p: p.ax.imshow(b.read()[:3, :, :].transpose((1, 2, 0)),
        #                                         extent=bext, origin='upper')
        }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bg2.png')

def tester_bg3():
    """specify extent, and use caropy.io.img_tiles.GootleTiles"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
    import cartopy.io.img_tiles as cimgt
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    # background
    bext = [-11344200.0, -11338900.0, 3724300.0, 3731100.0]
    plotter_options = {
        'contour_options': {'alpha': .2},
        'extent': bext, 'projection': ccrs.epsg(3857),
        # GoogleMap, we may need license
        'customize_once': lambda p: p.ax.add_image(cimgt.GoogleTiles(style='satellite'), 15)
        }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bg3.png')

def tester_bg4():
    """specify extent, and use NAIP images with cartopy.io.ogc_clients.WMSRasterSource"""
    from plotter import calpost_reader as reader
    import cartopy.crs as ccrs
#    import cartopy.io.ogc_clients as cogcc
    with open('../data/tseries_ch4_1min_conc_co_fl.dat') as f:
        dat = reader.Reader(f, slice(60 * 12, 60 * 12 + 10))

    def my_add_naip(p):
        img = p.ax.add_wms(
            'https://services.nationalmap.gov/arcgis/services/USGSNAIPImagery/ImageServer/WMSServer',
            layers='0'
        )
        # TODO how can i save this...?, or should I save this?


    # background
    bext = [-11344200.0, -11338900.0, 3724300.0, 3731100.0]
    plotter_options = {
        'contour_options': {'alpha': .2},
        'extent': bext, 'projection': ccrs.epsg(3857),
        # 'customize_once': lambda p: p.ax.add_wms(
        #     'https://services.nationalmap.gov/arcgis/services/USGSNAIPImagery/ImageServer/WMSServer',
        #                layers='0'
        # )
        'customize_once': my_add_naip,
        }

    x = dat['x'] * 1000
    y = dat['y'] * 1000
    p = Plotter(dat['v'], dat['ts'], x=x, y=y, plotter_options=plotter_options)
    p(outdir / 'test_bg4.png')




if __name__ == '__main__':
    tester_bg1()
    tester_bg2()
    tester_bg3()
    tester_bg4()