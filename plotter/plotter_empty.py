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

class PlotterEmpty:
    def __init__(self, array, tstamps, projection=None, extent=None, x=None, y=None,
                 plotter_options=None):
        """
        Manages mpl.Axes without actually making plot

        :rtype: PlotterEmpty
        :param np.ndarray array: has to be None
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t)
        :param ccrs.CRS projection: projection of xy coordinate of data
        :param list extent: xy extent of data, with with coordinate of projection
        :param np.ndarray x: x coordinate of data, with shape matching (...) part of array
        :param np.ndarray y: y coordinate of data, with shape matching (...) part of array
        :param dict plotter_options: all the arguments passed to plotter
        """

        if plotter_options is None: plotter_options = {}

        self.fig = plotter_options.get('fig', plt.figure())
        pos = plotter_options.get('pos', None)

        self.arr = array
        assert array is None
        self.tstamps = tstamps

        self.imshow_options = plotter_options.get('imshow_options', None)
        self.contour_options = plotter_options.get('contour_options', None)

        self.colorbar_options = plotter_options.get('colorbar_options', {})

        self.footnote = plotter_options.get('footnote', None)
        self.footnote_options = plotter_options.get('footnote_options', {})
        self.footnote_manager = None

        self.title = plotter_options.get('title', None)
        self.title_options = plotter_options.get('title_options', None)

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
            plot_projection = plotter_options.get('projection', self.projection)
        else:
            plot_extent = self.background_manager.extent if self.background_manager.extent else self.extent
            plot_projection = self.background_manager.projection if self.background_manager.projection else self.projection

        # create plots (GeoAxes)
        if pos:
            self.ax = self.fig.add_subplot(*pos)
            self.ax.axis('off')
        else:
            # TODO fix this warning
            # MatplotlibDeprecationWarning: Adding an axes using the same arguments as a previous axes currently reuses the earlier instance.
            # In a future version, a new instance will always be created and returned.
            # Meanwhile, this warning can be suppressed, and the future behavior ensured, by passing a unique label to each axes instance.
            self.ax = self.fig.add_subplot()
            self.ax.axis('off')

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

        if self.hasdata:
            pass
        else:
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
