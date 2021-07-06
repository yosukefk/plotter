from . import plotter_util as pu
from . import plotter_footnote as pf

import matplotlib.pyplot as plt
import numpy as np

import warnings


class PlotterVprof:
    def __init__(self, array, tstamps, z, idx=None, jdx=None,
                 projection=None, extent=None, x=None, y=None, plotter_options=None):
        """
        Manages mpl.Axes with a vertical profile plot

        :rtype: PlotterVprof
        :param np.ndarray array: 4-d array of data values, dimensions(t, z, y, x), or 2+ d array of data values, dimensions(t, ...)
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t)
        :param ccrs.CRS projection: projection of xy coordinate of data
        :param list extent: xy extent of data, with with coordinate of projection
        :param np.ndarray x: x coordinate of data, with shape matching (...) part of array
        :param np.ndarray y: y coordinate of data, with shape matching (...) part of array
        :param dict plotter_options: all the arguments passed to plotter
        """

        if plotter_options is None:
            plotter_options = {}

        # i have to know the axes being used, even user wants default
        # so i grab default axes here and hold onto it
        self.fig = plotter_options.get('fig', plt.figure())
        pos = plotter_options.get('pos', None)

        self.arr = array
        self.tstamps = tstamps

        if idx is None:
            if jdx is None:
                raise ValueError('none of idx/jdx provided')
            else:
                islice = slice(None, None)
                jslice = jdx
        else:
            if jdx is None:
                islice = idx
                jslice = slice(None, None)
            else:
                raise ValueError('both idx/jdx provided')
        self.idx = idx
        self.jdx = jdx
        self.islice = islice
        self.jslice = jslice
        self.kslice = slice(None, None)

        if 'imshow_option' in plotter_options:
            warnings.warn('imshow not supported', pu.PlotterWarning)
        self.contour_options = plotter_options.get('contour_options', {})

        self.colorbar_options = plotter_options.get('colorbar_options', {})

        self.footnote = plotter_options.get('footnote', "{tstamp}")  # default just time stamp
        footnote_options = {'xytext': (0, -18)}  # default, need to push lower
        footnote_options.update(
            plotter_options.get('footnote_options', {}))
        self.footnote_options = footnote_options
        self.footnote_manager = None

        self.title = plotter_options.get('title', None)
        self.title_options = plotter_options.get('title_options', None)

        # data's extent
        self.extent = extent
        self.x = x
        self.y = y
        if self.extent is None and not (self.x is None or self.y is None):
            self.extent = [self.x[0], self.x[-1], self.y[0], self.y[-1]]

        # vertical coordinates
        self.z = z

        # create plots 
        if pos:
            self.ax = self.fig.add_subplot(*pos)
        else:
            self.ax = self.fig.add_subplot()

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

        # default settings...


        if self.idx is None:
            hor = self.x
            xlab = 'easting'
        elif self.jdx is None:
            hor = self.y
            xlab = 'northing'
        else:
            raise RuntimeError('???')

        print('hor',hor)
        if hor is not None:

            self.ax.set_xticks([hor.min(), hor.max()])
            self.ax.set_xticklabels([0, hor[-1]-hor[0]])
            self.ax.set_xlabel(xlab)
            self.ax.set_ylabel('height')


        # other customizations
        if 'customize_once' in plotter_options:
            self.customize(plotter_options['customize_once'])
        # self.customize_once = plotter_options.get('customize_once', None)

        self.hasdata = False
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
        if tidx is None:
            tidx = 0
        # get 2d array to plot
        idx = [tidx, self.kslice, self.jslice, self.islice]

        arr = self.arr[tuple(idx)]

        ts = self.tstamps[tidx]
        self.current_arr = arr
        self.current_tstamp = ts

        if self.hasdata:

            if self.contour_options is not None:
                # have to remove old one, and make new one...
                # https://stackoverflow.com/questions/23250004/updating-contours-for-matplotlib-animation
                for c in self.cnt.collections:
                    c.remove()
                kwds = self.contour_options
                self.cnt = self.ax.contourf(self.hor, self.z, arr,**kwds)

            if self.footnote_manager is not None:
                self.footnote_manager(footnote)

        else:

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
                #print('idx', self.idx)
                #print('jdx', self.jdx)
                if self.idx is None:
                    self.hor = self.x
                elif self.jdx is None:
                    self.hor = self.y
                else:
                    raise RuntimeError('???')

                print('self.hor', self.hor)
                print('self.z', self.z)
                self.cnt = self.ax.contourf(self.hor, self.z, arr,  **kwds)
                self.mappable = self.cnt

            if self.colorbar_options is not None:
                kwds = self.colorbar_options
                if self.mappable is not None:
                    self.cb = plt.colorbar(mappable=self.mappable, ax=self.ax,
                                           **kwds)
                else:
                    warnings.warn('No data to show, Colorbar turned off',
                                  pu.PlotterWarning)

            # None => default?  or '' => nothing?
            if self.footnote != '':
                print('here')
                print(self.footnote)
                print(self.footnote_options)
                self.footnote_manager = pf.FootnoteManager(self, self.footnote,
                                                        footnote_options=self.footnote_options)

            #if self.customize_once:
            #    self.customize(self.customize_once)

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
