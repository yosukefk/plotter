from . import plotter_util as pu
from . import plotter_footnote as pf
import warnings

try:
    import cartopy.crs as ccrs

    has_cartopy = True
except ImportError:
    warnings.warn('no cartopy', ImportWarning)
    ccrs = None
    has_cartopy = False
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import warnings

mpl.use('Agg')


class PlotterCore:
    def __init__(self, array, tstamps, projection=None, extent=None, x=None, y=None,
                 plotter_options=None):
        """
        Manages mpl.Axes with a tile plot

        :rtype: PlotterCore
        :param np.ndarray array: 3-d array of data values, dimensions(t, y, x), or 2+ d array of data values, dimensions(t, ...)
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t)
        :param ccrs.CRS projection: projection of xy coordinate of data
        :param list extent: xy extent of data, with with coordinate of projection
        :param np.ndarray x: x coordinate of data, with shape matching (...) part of array
        :param np.ndarray y: y coordinate of data, with shape matching (...) part of array
        :param dict plotter_options: all the arguments passed to plotter
        """

        if plotter_options is None: plotter_options = {}

        # i have to know the axes being used, even user wants default
        # so i grab default axes here and hold onto it
        # TODO this seems to creats open figure and unless i close this
        # somehow it hangs there wasting memory.  what should I do?
        # shouldnt this be get instad of setdefault?
        # self.fig = plotter_options.setdefault('fig', plt.figure())
        self.fig = plotter_options.get('fig', plt.figure())
        pos = plotter_options.get('pos', None)

        self.arr = array
        self.tstamps = tstamps
        self.is_gridded = True

        if len(self.arr.shape) < 3:
            if x is None or y is None:
                raise RuntimeError(
                    'x and y are mandartory arguments for non-gridded data')
            
            if self.arr.shape[-1] != len(x) or self.arr.shape[-1] != len(y):
                raise RuntimeError(
                    f'size dosent mactch, arr.shape[-1], len(x), len(y) = {self.arr.shape}, {len(x)}, {len(y)}'
                )
            self.is_gridded = False
                

        self.subdomain = plotter_options.get('subdomain', None)
        if self.is_gridded:
            if self.subdomain is None:
                self.jslice = slice(None)
                self.islice = slice(None)
                self.i0 = 1
                self.j0 = array.shape[-2]
            else:
                warnings.warn('subdomain need QA')
                ny = self.arr.shape[-2]
                #self.jslice = slice((self.subdomain[1] - 1), self.subdomain[3])
                self.jslice = slice(ny -self.subdomain[3], ny - (self.subdomain[1] - 1), )
                self.islice = slice((self.subdomain[0] - 1), self.subdomain[2])
                self.i0 = self.subdomain[0]
                self.j0 = self.subdomain[3]
        else:
            self.islice = slice(None)

        # if neither imshow or contour are specified, default to use imshow
        # user can inteitionally not plot by making both to None
        if all(_ not in plotter_options.keys() for _ in ('imshow_options', 'contour_options')):
            plotter_options['imshow_options'] = {}
        self.imshow_options = plotter_options.get('imshow_options', None)
        self.contour_options = plotter_options.get('contour_options', None)

        self.colorbar_options = plotter_options.get('colorbar_options', {})

        self.footnote = plotter_options.get('footnote', None)
        self.footnote_options = plotter_options.get('footnote_options', {})
        self.footnote_manager = None

        self.title = plotter_options.get('title', None)
        self.title_options = plotter_options.get('title_options', None)

        if 'custimize_after' in plotter_options:
            warnings.warn('i dont think you need this', DeprecationWarning)
        self.customize_after = plotter_options.get('customize_after', None)
        #self.customize_once = plotter_options.get('customize_once', None)
        #print(self.customize_once)

        # data's extent
        self.extent = extent
        self.x = x
        self.y = y
        if self.extent is None and not (self.x is None or self.y is None):
            self.extent = [self.x[0], self.x[-1], self.y[0], self.y[-1]]

        # data's projection
        # assume TCEQ's lambert for the data array
        if projection is None:
            warnings.warn("Assume TCEQ's Lambert Conformal Proection",
                          pu.PlotterWarning)
            projection = pu.LambertConformalTCEQ()
        self.projection = projection

        # background
        self.background_manager = plotter_options.get('background_manager', None)
        # plot's extent/project grab from background_manager or arguments or from the data
        if self.background_manager is None:

            plot_extent = plotter_options.get('extent', self.extent)

            if not self.subdomain is None:
                if not self.x is None:
                    self.x = self.x[self.islice]
                if not self.y is None:
                    self.y = self.y[self.islice]

                dx = (self.extent[1] - self.extent[0]) / self.arr.shape[-1]
                dy = (self.extent[3] - self.extent[2]) / self.arr.shape[-2]
                #print(self.extent)
                #print(self.islice)
                #print(self.jslice)
                #print(dx, dy)
                self.extent = [
                        self.extent[0] + dx * self.islice.start,
                        self.extent[0] + dx * self.islice.stop ,
                        self.extent[3] - dy * self.jslice.stop ,
                        self.extent[3] - dy * self.jslice.start,
                        ]
                #print(self.extent)
                plot_extent = self.extent

            plot_projection = plotter_options.get('projection', self.projection)

        else:
            plot_extent = self.background_manager.extent if self.background_manager.extent else self.extent
            plot_projection = self.background_manager.projection if self.background_manager.projection else self.projection

        # create plots (GeoAxes)
        if pos:
            self.ax = self.fig.add_subplot(*pos, projection=plot_projection)
        else:
            # TODO fix this warning
            # MatplotlibDeprecationWarning: Adding an axes using the same arguments as a previous axes currently reuses the earlier instance.
            # In a future version, a new instance will always be created and returned.
            # Meanwhile, this warning can be suppressed, and the future behavior ensured, by passing a unique label to each axes instance.
            self.ax = self.fig.add_subplot(projection=plot_projection)

        if not plot_extent is None:
            self.ax.set_extent(plot_extent, crs=plot_projection)

        if not self.background_manager is None:
            self.background_manager.add_background(self)

        # self.title overrides 'label' in self.title_options
        if self.title is None:
            if self.title_options is None:
                pass
            else:
                self.title = self.title_options.get('label')
        else:
            if self.title_options is None:
                self.title_options = {'label': self.title}
            else:
                self.title_options['label'] = self.title

        if self.title is not None:
            ttlopt = {'loc': 'center'}
            ttlopt.update(self.title_options)
            self.ax.set_title(**ttlopt)

        # other customizations
        if 'customize_once' in plotter_options:
            self.customize(plotter_options['customize_once'])

        self.hasdata = False
        self.im = None
        self.cnt = None
        self.mappable = None
        self.current_arr = None
        self.current_tstamp = None

    def update(self, tidx=None, footnote=None, title=None):
        """
        Update plot to data at tidx

        :param int tidx: time index
        :param str footnote: footnote overwrite
        :param str title:  title overwrite
        """
        if tidx is None: tidx = 0
        if self.is_gridded:
            # get 2d array to plot
            idx = [tidx, self.jslice, self.islice]
        else:
            idx = [tidx, self.islice]

        arr = self.arr[tuple(idx)]

        ts = self.tstamps[tidx]
        self.current_arr = arr
        self.current_tstamp = ts
        self.tidx = tidx

        if self.hasdata:
            if self.imshow_options is not None:
                self.im.set_data(arr)

            if self.contour_options is not None:
                # have to remove old one, and make new one...
                # https://stackoverflow.com/questions/23250004/updating-contours-for-matplotlib-animation
                for c in self.cnt.collections:
                    c.remove()
                kwds = self.contour_options
                if self.is_gridded:
                    self.cnt = self.ax.contourf(self.x, self.y, arr,
                                                extent=self.extent, transform=self.projection, **kwds)
                else:
                    self.cnt = self.ax.tricontourf(self.x, self.y, arr,
                                                extent=self.extent, transform=self.projection, **kwds)

            if self.footnote_manager is not None:
                self.footnote_manager(footnote)

        else:
            if self.imshow_options is not None:
                kwds = self.imshow_options
                if 'norm' not in kwds:
                    # if user didnt explicitly specify norm, i use entire range of data to bound color
                    kwds['norm'] = mpl.colors.Normalize(vmin=self.arr.min(), vmax=self.arr.max())
                if self.extent is None:
                    if self.x is None:
                        pass
                    else:
                        # not super accurate, off by half pixel
                        self.extent = [np.min(self.x), np.max(self.x), np.min(self.y), np.max(self.y)]

                if 'origin' not in kwds and self.y is not None and self.y[0] < self.y[-1]:
                    # y is ascending order, not typical gis raster.
                    origin = 'lower'
                else:
                    origin = 'upper'

                self.im = self.ax.imshow(arr, extent=self.extent, origin =
                                         origin, transform=self.projection, **kwds)
                self.mappable = self.im

            if self.contour_options is not None:
                kwds = self.contour_options
                if 'norm' not in kwds:
                    # if user didnt explicitly specify norm, i use entire range of data to bound color
                    kwds['norm'] = mpl.colors.Normalize(vmin=self.arr.min(), vmax=self.arr.max())
                if self.is_gridded:
                    if self.x is None:
                        if self.extent is None:
                            self.x = np.arange(arr.shape[1])
                            self.y = np.arange(arr.shape[0])
                        else:
                            self.x = np.linspace(self.extent[0], self.extent[1], arr.shape[1], endpoint=False)
                            self.y = np.linspace(self.extent[3], self.extent[2], arr.shape[0], endpoint=False)
                            self.x = self.x + .5 * (self.x[1] - self.x[0])
                            self.y = self.y + .5 * (self.y[1] - self.y[0])
                        # print(self.x)
                        # print(self.y)
                    self.cnt = self.ax.contourf(self.x, self.y, arr, extent=self.extent, transform=self.projection, **kwds)
                    self.mappable = self.cnt
                else:
                    self.cnt = self.ax.tricontourf(self.x, self.y, arr, extent=self.extent, transform=self.projection, **kwds)
                    self.mappable = self.cnt

            if self.colorbar_options is not None:
                kwds = self.colorbar_options
                if not self.mappable is None:


                    self.cb = plt.colorbar(mappable=self.mappable, ax=self.ax,
                                           **kwds)
                else:
                    warnings.warn('No data to show, Colorbar turned off',
                                  pu.PlotterWarning)

            # None => default?  or '' => nothing?
            if self.footnote != '':
                self.footnote_manager = pf.FootnoteManager(self, self.footnote,
                                                        self.footnote_options)

#            # other customizations
#            if self.customize_once:
#                self.customize(self.customize_once)

            self.hasdata = True

        if title is not None:
            # update the title
            self.ax.set_title(title)

        # customization needed after updating data
        if self.customize_after:
            warnings.warn('set zorder was what you need?',
                          DeprecationWarning)
            self.customize(self.customize_after)

    def __call__(self, *args, **kwargs):
        """update()"""
        self.update(*args, **kwargs)

    def customize(self, fnc):
        """
        apply function to self.ax

        :param function, list fnc:
        """

        # no arguments
        if callable(fnc):
            fnc(self)
        elif '__len__' in dir(fnc):
            for fn in fnc:
                fn(self)
        else:
            raise ValueError(f'fnc is not callable: {fnc}')
