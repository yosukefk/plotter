import warnings
from . import plotter_core as pc
from . import plotter_util as pu
try:
    import cartopy.crs as ccrs
    has_cartopy = True
    from cartopy.io.img_tiles import GoogleWTS
except ImportError:
    warnings.warn('no cartopy', ImportWarning)
    ccrs = None
    has_cartopy = False

try:
    import rasterio
    from rasterio.warp import reproject, calculate_default_transform, Resampling
    has_rasterio = True
except ImportError:
    warnings.warn('no rasterio', ImportWarning)
    rasterio = None
    reproject = None
    calculate_default_transform = None
    Resampling = None
    has_rasterio = False

import numpy as np
import tempfile


# TODO maybe make this part of PlotterCore itself?
class BackgroundManager:
    def __init__(self, bgfile=None, source_projection=None, extent=None,
                 projection=None, wms_options=None, add_image_options=None):
        """Manage plot's projection/extent/background

        :param str, Path bgfile: name of Geotiff file to use as background
        :param ccrs.CRS source_projection: projection of bgfile, in case cartopy don't understand it
        :param list extent: extent of background (x0, x1, y0, y1)
        :param ccrs.CRS projection: projection to be used for the plot
        :param dict wms_options: arguments to GeoAxes.add_wms()
        :param dict add_image_options: arguments to GeoAxes.add_image()
        """

        if bgfile is None:
            self.projection = projection
            self.extent = extent
            self.img = None
            self.wms_options = wms_options
            self.add_image_options = add_image_options
        else:

            if not has_rasterio:
                raise RuntimeError('no raster io')

            # use bgfile's extent
            self.b = rasterio.open(bgfile)

            if source_projection is None:
                self.source_projection = self.read_projection(self.b.crs.data)
            else:
                self.source_projection = source_projection

            if projection is None:
                self.projection = self.source_projection
                self.img = self.b.read()[:3, :, :].transpose((1, 2, 0))
                if extent is None:
                    # use raster's extent
                    self.extent = [self.b.transform[2], self.b.transform[2] + self.b.transform[0] * self.b.width,
                                   self.b.transform[5] + self.b.transform[4] * self.b.height, self.b.transform[5]]

                else:
                    # user specified extent but not projection.  has to trust what they are doing...
                    warnings.warn('are you sure', pu.PlotterWarning)
                    self.extent = extent
            else:
                self.warp(projection)
                if extent is None:
                    pass

                else:
                    # user specified both projection and extent
                    self.extent = extent

    @staticmethod
    def read_projection(crs_data):
        """
        reead rasterio's crs data (Proj.4) and return equivalent ccrs.CRS

        :rtype: ccrs.CRS
        :param dict crs_data: Proj.4 projection specification
        :return: projection
        """
        # try interpret projection of raster...  this should be supported by cartopy,
        # something like this https://github.com/SciTools/cartopy/pull/1023, which kind of superceded by
        # https://github.com/SciTools/cartopy/issues/1477 which is still taking time...  So for now i do
        # quick-and-dirty job here
        # this is good source too https://github.com/djhoese/cartopy/blob/feature-from-proj/lib/cartopy/_proj4.py
        # but he manually edited crs.py to interpret from proj4 components, and
        # i dont think i can import his work easily.

        if 'init' in crs_data and crs_data['init'].lower().startswith('epsg:'):
            # if epsg is specified, assume it is going to work.
            epsg = int(crs_data['init'][5:])
            if epsg == 3857:
                source_projection = ccrs.Mercator.GOOGLE
            else:
                # this goes to internet to get info, so avoid it if possible
                source_projection = ccrs.epsg(epsg)

        elif 'proj' in crs_data:

            _GLOBE_PARAMS = {'datum': 'datum',
                             'ellps': 'ellipse',
                             'a': 'semimajor_axis',
                             'b': 'semiminor_axis',
                             'f': 'flattening',
                             'rf': 'inverse_flattening',
                             'towgs84': 'towgs84',
                             'nadgrids': 'nadgrids',
                             'R': 'semimajor_axis',
                             }
            projection_terms = {}
            globe_terms = {}
            for name, value in crs_data.items():
                if name in _GLOBE_PARAMS:
                    globe_terms[name] = value
                else:
                    projection_terms[name] = value

            # yk, without this, it defaults to wgs84...
            globe_terms.setdefault('ellps', None)
            globe = ccrs.Globe(**{_GLOBE_PARAMS[name]: value for name, value in
                                  globe_terms.items()})

            if crs_data['proj'] == 'lcc':
                # there seems to be more subtleteis , but this should suffice
                # https://github.com/djhoese/cartopy/blob/feature-from-proj/lib/cartopy/crs.py#L1144-L1172
                source_projection = ccrs.LambertConformal(
                    central_longitude=crs_data['lon_0'],
                    central_latitude=crs_data['lat_0'],
                    false_easting=crs_data['x_0'],
                    false_northing=crs_data['y_0'],
                    standard_parallels=[crs_data['lat_1'], crs_data['lat_2']],
                    globe=globe)
            elif False:
                # define more projection as needed
                pass
            else:
                raise NotImplementedError(f"proj4 projection '{crs_data['proj']}'")
        else:

            raise RuntimeError("can't tell projection of raster, use 'source_projection' to specify")

        return source_projection

    def warp(self, projection: ccrs.CRS):
        """reproject bacground raster

        :param projection: ccrs.Projection
        """
        transform, width, height = calculate_default_transform(
            self.b.crs.data, projection.proj4_params, self.b.width, self.b.height, *self.b.bounds
        )
        kwds = self.b.meta
        kwds['transform'] = transform
        kwds['width'] = width
        kwds['heigh'] = height
        # with rasterio.open(tempfile.TemporaryFile(siffix='.tif')) as dst:

        with tempfile.TemporaryFile('w+b') as fil,\
                rasterio.open(fil, 'w+', **kwds) as dst:
            data = self.b.read()

            for i, band in enumerate(data, 1):
                dest = np.zeros((height, width), band.dtype)
                reproject(
                    band,
                    dest,
                    src_transform=self.b.transform,
                    src_crs=self.b.crs.data,
                    dst_transform=transform,
                    dst_crs=projection.proj4_params,
                    resampling=Resampling.nearest
                )
                dst.write(dest, indexes=i)

            self.img = dst.read()[:3, :, :].transpose((1, 2, 0))
            self.projection = projection
            self.extent = dst.bounds

    def add_background(self, p: pc.PlotterCore):
        """
        Add background image, either by GeoAxes.imshow, GeoAxes.add_wms or GeoAxes.add_image()

        :param p: PlotterCore
        """
        if self.img is not None:
            p.ax.imshow(self.img, extent=self.extent, origin='upper')
        elif self.wms_options:
            p.ax.add_wms(**self.wms_options)
        elif self.add_image_options:
            if len(self.add_image_options) < 2 and isinstance(self.add_image_options[0], GoogleWTS):
                # set zoom level automatically
                # https://gis.stackexchange.com/questions/7430/what-ratio-scales-do-google-maps-zoom-levels-correspond-to
                
                lv0 = 591657550.500000
                siz = max(p.extent[1] - p.extent[0], p.extent[3]-p.extent[2])
                z = int(np.floor(np.log2(lv0 / (siz*2))))
                
                self.add_image_options.append(z)
            p.ax.add_image(*self.add_image_options)

    def purge_bgfile_hook(self):
        """
        drop bgfile attribute, which is rasterio

        rasterio cannot be picked, so it needs to be purged for multiprocessing
        """
        try:
            del self.b
        except AttributeError:
            pass
