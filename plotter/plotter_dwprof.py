from . import plotter_util as pu
from . import plotter_footnote as pf
from . import plotter_core as pc

import matplotlib.pyplot as plt
import matplotlib as mpl

import numpy as np
from scipy.interpolate import interp2d

class PlotterDwprofPlanview(pc.PlotterCore):
    def __init__(self, array, tstamps, z, origin=None, distance=None, half_angle=None, kind=None,
                 projection=None, extent=None, x=None, y=None, plotter_options=None):

        super().__init__( array[:,0,:,:], tstamps, 
                 projection=projection, extent=extent, x=x, y=y, plotter_options=plotter_options)

        
        self.pdw = PlotterDwprof( array, tstamps, z, origin=origin, distance=distance, half_angle=half_angle, kind='skelton',
                 projection=projection, extent=extent, x=x, y=y, plotter_options={k:v for k,v in plotter_options.items() if k != 'customize_once'})

    def update(self, tidx=None, footnote=None, title=None):
        super().update(tidx=tidx, footnote=footnote, title=title)
        self.pdw.update(tidx)
        x0, y0, radius, theta, x1, y1 = self.pdw.update(tidx)
        if hasattr(self, 'footprints'): 
            for x in self.footprints:
                x.remove()
        #self.ax.add_patch(plt.Circle((x0,y0), radius, fill=False, color='black', lw=.6))
        arc = self.ax.add_patch(mpl.patches.Arc((x0,y0), radius*2, radius*2, angle=theta/np.pi*180, theta1=-self.pdw.half_angle, theta2=self.pdw.half_angle,  color='black', lw=.6))
        ray = self.ax.add_line(mpl.lines.Line2D((x0,x1), (y0, y1), color='black', lw=.6))
        self.footprints = [arc, ray]

class PlotterDwprof:
    def __init__(self, array, tstamps, z, origin=None, distance=None, half_angle=None, kind=None,
                 projection=None, extent=None, x=None, y=None, plotter_options=None):
        """
        Manages mpl.Axes with a vertical profile plot

        :rtype: PlotterVprof
        :param np.ndarray array: 4-d array of data values, dimensions(t, z, y, x), or 2+ d array of data values, dimensions(t, ...)
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t)
        :param np.ndarray z: 1-d array of z coordinate of data
        :param tuple origin: x,y coorinate of origin of profile
        :param float distance: distance from origin at which direction of profile is determined
        :pram str kind: 'cross', 'along', 'skelton'
        :param ccrs.CRS projection: projection of xy coordinate of data
        :param list extent: xy extent of data, with with coordinate of projection
        :param np.ndarray x: x coordinate of data, with shape matching (...) part of array
        :param np.ndarray y: y coordinate of data, with shape matching (...) part of array
        :param dict plotter_options: all the arguments passed to plotter
        """

        if plotter_options is None:
            plotter_options = {}


        self.arr = array
        self.tstamps = tstamps

        if origin is None or distance is None:
            raise ValueError('both origin and distnace requered')
           
        self.x0, self.y0 = origin
        self.distance = distance 
        if half_angle is None: half_angle = 30
        self.half_angle = half_angle
        self.kind = kind
        if self.kind != 'skelton':
            # i have to know the axes being used, even user wants default
            # so i grab default axes here and hold onto it
            self.fig = plotter_options.get('fig', plt.figure())
            pos = plotter_options.get('pos', None)


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
        if self.kind != 'skelton':
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

        # prepare circle and ray
        # circumference 
        circ = 2 * np.pi * self.distance # circumference
        # resolution (half of data' resolution)
        dx = .5 * (self.x[-1] - self.x[0]) / (len(self.x) - 1)
        # count of nodes on circle
        ndiv = int(np.round( circ / dx ))

        # generate coordinates for circle
        dtheta = - 2*np.pi / ndiv  # lets go reverse, since decrease in theta goes to right in profile
        theta = np.arange(ndiv) * dtheta

        self.c_theta = theta
        self.c_x = np.cos(theta) * self.distance + self.x0
        self.c_y = np.sin(theta) * self.distance + self.y0
        self.c_s = - np.pi * theta   # s goes from 0 to positive
        #self.c_mm = int(np.ceil(len(self.c_theta) / 6)) # 60 degree both side of center
        #self.c_mm = int(np.ceil(len(self.c_theta) / 8)) # 45 degree both side of center
        #self.c_mm = int(np.ceil(len(self.c_theta) / 12)) # 30 degree both side of center
        self.c_mm = int(np.ceil(len(self.c_theta) * self.half_angle / 360)) # half_angle degree both side of center
        self.c_nn = 2*self.c_mm + 1
        self.c_hor = np.linspace(self.distance * np.pi * dtheta * self.c_nn, - self.distance * np.pi * dtheta * self.c_nn, 2*self.c_nn + 1)

        # for each direction, prepare coordinates for ray
        xr = 1.5 * np.cos(theta) * self.distance + self.x0
        yr = 1.5 * np.sin(theta) * self.distance + self.y0
        nr = int( np.round( self.distance * 1.5 / dx ) )
        self.r_x = np.linspace(self.x0, xr, nr).T  # sereis of x for each theta
        self.r_y = np.linspace(self.y0, yr, nr).T
        self.r_nn = nr
        self.r_hor = np.linspace(0, self.distance * 1.5, self.r_nn)

        # column sum of array
        self.arr2d = self.arr.transpose(0, 2, 3, 1).dot(z)

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

        # get array for tidx
        arr = self.arr[tidx]
        arr2d = self.arr2d[tidx]

        self.current_arr = arr
        self.current_tstamp = self.tstamps[tidx]

        # find direction of maximum on the circle
        fnc = interp2d(self.x, self.y, arr2d)
        c_v = np.array([fnc(_x, _y)[0] for _x, _y in zip(self.c_x, self.c_y)])

        hdx = c_v.argmax()

        if self.kind == 'skelton':
            # simply return the ray
            return self.x0, self.y0, self.distance, self.c_theta[hdx], self.r_x[hdx, -1], self.r_y[hdx, -1]

        if self.kind == 'cross':
            c_x = np.roll(self.c_x, -(hdx - self.c_nn))[0:(2*self.c_nn+1)]
            c_y = np.roll(self.c_y, -(hdx - self.c_nn))[0:(2*self.c_nn+1)]

            c_v = np.empty([len(self.z), len(c_x), ])
            for k in range(len(self.z)):

                fnc = interp2d(self.x, self.y, arr[k])
                c_v[k,:] = [fnc(_x, _y)[0] for _x, _y in zip(c_x, c_y)]
            

            self.hor = self.c_hor

            self.current_arr = c_v
            self.cuttent_tstamp = self.tstamps[tidx]

        elif self.kind == 'along':
            r_x = self.r_x[hdx]
            r_y = self.r_y[hdx]

            r_v = np.empty([len(self.z), len(r_x)])
            for k in range(len(self.z)):
                fnc = interp2d(self.x, self.y, arr[k])
                r_v[k,:] = [fnc(_x, _y)[0] for _x, _y in zip(r_x, r_y)]

            self.hor = self.r_hor
            self.current_arr = r_v
            self.cuttent_tstamp = self.tstamps[tidx]


        if self.hasdata:

            if self.contour_options is not None:
                # have to remove old one, and make new one...
                # https://stackoverflow.com/questions/23250004/updating-contours-for-matplotlib-animation
                for c in self.cnt.collections:
                    c.remove()
                kwds = self.contour_options
                self.cnt = self.ax.contourf(self.hor, self.z, self.current_arr,**kwds)
        
            if self.footnote_manager is not None:
                self.footnote_manager(footnote)

        else:

            if self.contour_options is not None:
                kwds = self.contour_options

                self.cnt = self.ax.contourf(self.hor, self.z, self.current_arr,  **kwds)
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
                #print('here')
                #print(self.footnote)
                #print(self.footnote_options)
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
