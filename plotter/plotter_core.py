import plotter_util as pu
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import warnings





class PlotterCore:
    def __init__(self, array, tstamps, projection=None, extent=None, x=None, y=None,
                 plotter_options=None):
        """

        :rtype: object
        :param array: 3-d array of data values, dimensions(t, y, x), or 2+ d array of data values, dimensions(t, ...)
        :param tstamps: 1-d array of datetime, dimensions(t)
        :param projection: projection of xy coordinate of data
        :param extent: xy extent of data, with with coordinate of projection
        :param x: x coordinate of data, with shape matching (...) part of array
        :param y: y coordinate of data, with shape matching (...) part of array
        :param plotter_options: all the arguments passed to plotter
        """

        if plotter_options is None: plotter_options = {}

        # i have to know the axes being used, even user wants default
        # so i grab default axes here and hold onto it
        self.fig = plotter_options.setdefault('fig', plt.figure())
        pos = plotter_options.get('pos', None)

        self.arr = array
        self.tstamps = tstamps

        # if neither imshow or contour are specified, default to use imshow
        # user can inteitionally not plot by making both to None
        if all(_ not in plotter_options.keys() for _ in ('imshow_options', 'contour_options')):
            plotter_options['imshow_options'] = {}
        self.imshow_options = plotter_options.get('imshow_options', None)
        self.contour_options = plotter_options.get('contour_options', None)

        self.colorbar_options = plotter_options.get('colorbar_options', {})

        self.footnote_options = plotter_options.get('footnote_options', {})

        self.title = plotter_options.get('title', None)
        self.title_options = plotter_options.get('title_options', None)

        if 'custimize_after' in plotter_options:
            warnings.warn('i dont think you need this', DeprecationWarning)
        self.customize_after = plotter_options.get('customize_after', None)

        # data's extent
        self.extent = extent
        self.x = x
        self.y = y

        # data's projection
        # assume TCEQ's lambert for the data array
        if projection is None:
            warnings.warn("Assume TCEQ's Lambert Conformal Proection",
                          pu.PlotterWarning)
            projection = pu.LambertConformalTCEQ()
        self.projection = projection

        # background
        self.background_manager = plotter_options.get('background_manager', None)

        # if self.background_manager is None or self.background_manager.projection is None:
        if self.background_manager is None:
            # plot's extent
            plot_extent = plotter_options.get('extent', self.extent)
            plot_projection = plotter_options.get('projection', self.projection)
        else:
            plot_extent = self.background_manager.extent if self.background_manager.extent else self.extent
            plot_projection = self.background_manager.projection if self.background_manager.projection else self.projection

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

        # self.title overrides
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

    def __call__(self, tidx=None, footnote='', title=None):
        if tidx is None: tidx = 0
        arr = self.arr[tidx]
        ts = self.tstamps[tidx]

        if self.hasdata:
            if self.imshow_options is not None:
                self.im.set_data(arr)

            if self.contour_options is not None:
                # have to remove old one, and make new one...
                # https://stackoverflow.com/questions/23250004/updating-contours-for-matplotlib-animation
                for c in self.cnt.collections:
                    c.remove()
                kwds = self.contour_options
                self.cnt = self.ax.contourf(self.x, self.y, arr,
                                            extent=self.extent, transform=self.projection, **kwds)

            if footnote is not None:
                self.footnote.set_text(footnote)

        else:
            if self.imshow_options is not None:
                kwds = self.imshow_options
                if self.extent is None:
                    if self.x is None:
                        pass
                    else:
                        # not super accurate, off by half pixel
                        self.extent = [np.min(self.x), np.max(self.x), np.min(self.y), np.max(self.y)]

                self.im = self.ax.imshow(arr, extent=self.extent, transform=self.projection, **kwds)
                self.mappable = self.im

            if self.contour_options is not None:
                kwds = self.contour_options
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

            if self.colorbar_options is not None:
                kwds = self.colorbar_options
                if not self.mappable is None:
                    self.cb = plt.colorbar(mappable=self.mappable, ax=self.ax,
                                           **kwds)
                else:
                    warnings.warn('No data to show, Colorbar turned off',
                                  pu.PlotterWarning)

            if footnote is not None:
                self.footnote = self.ax.annotate(footnote,
                                                 xy=(0.5, 0),  # bottom center
                                                 xytext=(0, -6),
                                                 # drop 6 ponts below (works if there is no x axis label)
                                                 # xytext=(0,-18), # drop 18 ponts below (works with x-small fontsize axis label)
                                                 xycoords='axes fraction',
                                                 textcoords='offset points',
                                                 ha='center', va='top')

            self.hasdata = True

        if not title is None:
            # update the title
            self.ax.set_title(title)

        # customizeration needed after updating data
        if self.customize_after:
            warnings.warn('set zorder was what you need?',
                          DeprecationWarning)
            self.customize(self.customize_after)

    def customize(self, fnc):
        # apply fnc to self.ax
        # no arguments

        if callable(fnc):
            fnc(self)
        elif '__len__' in dir(fnc):
            for fn in fnc:
                fn(self)
        else:
            raise ValueError(f'fnc is not callable: {fnc}')
