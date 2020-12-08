import plotter_core as pc
import cartopy.crs as ccrs
import rasterio
import warnings

# TCEQ's Lambert Conformal projection, define in caropy way
lcc_tceq = ccrs.LambertConformal(central_longitude=-97, central_latitude=40,
                                 standard_parallels=(33, 45), globe=ccrs.Globe(semimajor_axis=6370000,
                                                                               semiminor_axis=6370000))

# TODO maybe make this part of PlotterCore itself?
class background_manager:
    def __init__(self, bgfile=None, extent=None, crs=None):
        """

        :param bgfile: Geotiff file to use as background
        :param extent: extent of background
        :param crs: crs to be used for the plot
        """
        if bgfile is None:
            # TODO i should grab extend of the data, i i konw...
            pass
        else:
            # use bgfile's extent
            self.b = rasterio.open(bgfile)
            if crs is None:
                # TODO make sure i grab crs compatible with ccrs
                self.crs = self.b.crs
                if extent is None:
                    # use raster's extent
                    self.extent = [self.b.transform[2], self.b.transform[2] + self.b.transform[0] * self.b.width,
                                   self.b.transform[5] + self.b.transform[4] * self.b.height, self.b.transform[5]]

                else:
                    # user specified extent but not CRS.  has to trust what they are doing...
                    warnings.warn('are you sure', pc.PlotterWarning)
                    self.extent = extent
            else:
                # TODO warp raster data HERE!!
                self.b = self.b  # warp somehow

                if extent is None:
                    # TODO come up with extent approximates the area covered by warped raster
                    raise NotImplementedError('be more specific!')

                else:
                    # user specified both crs and extent
                    self.extent = extent

    def add_background(self, p: pc.PlotterCore):
        """

        :param p:
        """
        # TODO actually data may need to be warped.  so hold onto array to be used, instead of reading it here
        p.ax.imshow(self.b.read()[:3, :, :].transpose((1, 2, 0)),
                    extent=self.extent, origin='upper')


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
