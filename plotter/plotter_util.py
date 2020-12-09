import plotter_core as pc
import cartopy.crs as ccrs
import rasterio
import warnings

class PlotterWarning(UserWarning): pass

# TCEQ's Lambert Conformal projection, define in caropy way
def LambertConformalTCEQ():
    return ccrs.LambertConformal(central_longitude=-97, central_latitude=40,
                                 standard_parallels=(33, 45), globe=ccrs.Globe(semimajor_axis=6370000,
                                                                               semiminor_axis=6370000))

# TODO maybe make this part of PlotterCore itself?
class BackgroundManager:
    def __init__(self, bgfile=None, source_projection=None, extent=None, projection=None):
        """

        :param bgfile: Geotiff file to use as background
        :param extent: extent of background
        :param projection: projection to be used for the plot
        """
        if bgfile is None:
            if any((projection is None, extent is None)):
                # NULL background!!!
                raise RuntimeError('Null background!!')
                self.projection = None
                self.extent = None
                self.img = None
            else:
                self.projection = projection
                self.extent = extent
                self.img = None
        else:
            # use bgfile's extent
            self.b = rasterio.open(bgfile)
            self.img = self.b.read()[:3, :, :].transpose((1, 2, 0))

            # try interpret projection of raster...  this should be supported by cartopy,
            # something like this https://github.com/SciTools/cartopy/pull/1023, which kind of superceded by
            # https://github.com/SciTools/cartopy/issues/1477 which is still taking time...  So for now i do
            # quick-and-dirty job here
            # this is good source too https://github.com/djhoese/cartopy/blob/feature-from-proj/lib/cartopy/_proj4.py
            if source_projection is None:
                crs_data = self.b.crs.data
                if 'init' in crs_data and crs_data['init'].lower().startswith('epsg:'):
                    # if epsg is specified, assume it is going to work.
                    epsg = int(crs_data['init'][5:])
                    self.source_projection = ccrs.epsg(epsg)
                elif 'proj' in crs_data:
                    _GLOBE_PARAMS = {'datum': 'datum',
                                     'ellps': 'ellipse',
                                     'a': 'semimajor_axis',
                                     'b': 'semiminor_axis',
                                     'f': 'flattening',
                                     'rf': 'inverse_flattening',
                                     'towgs84': 'towgs84',
                                     'nadgrids': 'nadgrids'}
                    projection_terms = {}
                    globe_terms = {}
                    for name, value in crs_data.items():
                        if name in _GLOBE_PARAMS:
                            globe_terms[name] = value
                        else:
                            projection_terms[name] = value
                    globe = ccrs.Globe(**{_GLOBE_PARAMS[name]: value for name, value in
                                          globe_terms.items()})
                    if crs_data['proj'] == 'lcc':

                        self.source_projection = ccrs.LambertConformal(
                            central_longitude=crs_data['lon_0'],
                            central_latitude=crs_data['lat_0'],
                            false_easting=crs_data['x_0'],
                            false_northing=crs_data['y_0'],
                            standard_parallels=[crs_data['lat_1'], crs_data['lat_2']],
                            globe=globe)
                    else:
                        raise NotImplementedError(f"proj4 projection '{crs_data['proj']}'")
                else:
                    raise RuntimeError("cant tell projection of raster, use 'source_projection' to specify")
            else:
                self.source_projection = source_projection
            if projection is None:
                self.projection = self.source_projection
                if extent is None:
                    # use raster's extent
                    self.extent = [self.b.transform[2], self.b.transform[2] + self.b.transform[0] * self.b.width,
                                   self.b.transform[5] + self.b.transform[4] * self.b.height, self.b.transform[5]]

                else:
                    # user specified extent but not projection.  has to trust what they are doing...
                    warnings.warn('are you sure', pc.PlotterWarning)
                    self.extent = extent
            else:
                # TODO warp raster data HERE!!
                self.b = self.b  # warp somehow

                if extent is None:
                    # TODO come up with extent approximates the area covered by warped raster
                    raise NotImplementedError('be more specific!')

                else:
                    # user specified both projection and extent
                    self.extent = extent

    def add_background(self, p: pc.PlotterCore):
        """

        :param p:
        """
        if self.img is None:
            pass
        else:
            p.ax.imshow(self.img, extent=self.extent, origin='upper')

        # # or use wms server like below (i may want to cache img if that's not done by itself
        # img = p.ax.add_wms(
        #         'https://services.nationalmap.gov/arcgis/services/USGSNAIPImagery/ImageServer/WMSServer',
        #         layers='0'
        #     )


# Deprecated
class background_adder:
    # https://ocefpaf.github.io/python4oceanographers/blog/2015/03/02/geotiff/
    def __init__(self, fname, alpha=.2):
        warnings.warn('use background_manager', DeprecationWarning)
        ds = rasterio.open(str(fname))
        self.data = ds.read()[:3, :, :].transpose((1, 2, 0))
        self.extent = [ds.transform[2], ds.transform[2] + ds.transform[0] * ds.width,
                       ds.transform[5] + ds.transform[4] * ds.height, ds.transform[5]]
        self.alpha = alpha

    def set_background(self, p):
        p.background_bga = p.ax.imshow(self.data, extent=self.extent, origin='upper',
                                       alpha=self.alpha)

    def refresh_background(self, p):
        p.background_bga.set_zorder(1)
