from . import plotter_util as pu
from . import plotter_footnote as pf
from . import plotter_core as pc

import matplotlib.pyplot as plt
import matplotlib as mpl

import numpy as np
from scipy.interpolate import interp2d

class PlotterDwprofPlanview(pc.PlotterCore):
    def __init__(self, array, tstamps, z, origin=None, distance=None, distance_to_plot=None, distance_for_direction=None, half_angle=None, kind=None,
                 projection=None, extent=None, x=None, y=None, plotter_options=None):

        super().__init__( array[:,0,:,:], tstamps, 
                 projection=projection, extent=extent, x=x, y=y, plotter_options=plotter_options)

        
        self.pdw = PlotterDwprof( array, tstamps, z, origin=origin, distance=distance, distance_to_plot=distance_to_plot, distance_for_direction=distance_for_direction, half_angle=half_angle, kind='skelton',
                 projection=projection, extent=extent, x=x, y=y, plotter_options={k:v for k,v in plotter_options.items() if k != 'customize_once'})

    def update(self, tidx=None, footnote=None, title=None):
        super().update(tidx=tidx, footnote=footnote, title=title)
        self.pdw.update(tidx)
        x0, y0, radius, theta, x1, y1 = self.pdw.update(tidx)
        if hasattr(self, 'footprints'): 
            for x in self.footprints:
                x.remove()
        #self.ax.add_patch(plt.Circle((x0,y0), radius, fill=False, color='black', lw=.6))
        self.footprints = []
        for rad in radius:
            arc = self.ax.add_patch(mpl.patches.Arc((x0,y0), rad*2, rad*2, angle=theta/np.pi*180, theta1=-self.pdw.half_angle, theta2=self.pdw.half_angle,  color='black', lw=.6))
            self.footprints.append(arc)
        ray = self.ax.add_line(mpl.lines.Line2D((x0,x1), (y0, y1), color='black', lw=.6))
        self.footprints.append(ray)

class PlotterDwprof:
    def __init__(self, array, tstamps, z, origin=None, distance=None, distance_to_plot=None, distance_for_direction=None, half_angle=None, kind=None,
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

        if distance_to_plot is None:
            distance_to_plot = distance

        if origin is None or distance_to_plot is None:
            raise ValueError('both origin and distnace requered: distance={}, distance_to_plot={}'.format(distance, distance_to_plot))
           
        self.x0, self.y0 = origin
        self.distance_to_plot = np.atleast_1d( distance_to_plot)
        if distance_for_direction is None:
            self.distance_for_direction = self.distance_to_plot.min()
        else:
            self.distance_for_direction = distance_for_direction

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
        circ = 2 * np.pi * self.distance_to_plot # circumference
        # resolution (half of data' resolution)
        dx = .5 * (self.x[-1] - self.x[0]) / (len(self.x) - 1)
        # count of nodes on circle
        ndiv = np.round( circ / dx ).astype(int)
        #print(ndiv)

        # generate coordinates for circle(s)
        dtheta = - 2*np.pi / ndiv  # lets go reverse, since decrease in theta goes to right in profile
        #print(dtheta)

        self.circles = []

        for dst, nd, dth in zip(self.distance_to_plot, ndiv, dtheta):
            dct = {}

            theta = np.arange(nd) * dth
            dct['theta'] = theta
            dct['x'] = np.cos(theta) * dst + self.x0
            dct['y'] = np.sin(theta) * dst + self.y0
            dct['s'] = - np.pi * theta   # s goes from 0 to positive
            dct['m'] = int(np.ceil(len(theta) * self.half_angle / 360)) # half_angle degree both side of center
            dct['n'] = 2 * dct['m'] + 1
            dct['hor'] = np.linspace(dst * np.pi * dth * dct['n'], - dst * np.pi * dth * dct['n'], 2*dct['n'] + 1)

            self.circles.append(dct)

        circ = 2 * np.pi * self.distance_for_direction # circumference
        ndiv = np.round( circ / dx ).astype(int)
        dtheta = - 2*np.pi / ndiv  # lets go reverse, since decrease in theta goes to right in profile
        theta = np.arange(ndiv) * dtheta

        self.circle_for_direction = {}
        self.circle_for_direction['theta'] = theta
        self.circle_for_direction['x'] = np.cos(theta) * self.distance_for_direction + self.x0
        self.circle_for_direction['y'] = np.sin(theta) * self.distance_for_direction + self.y0

        # for each direction, prepare coordinates for ray
        xr = 1.2 * np.cos(theta) * self.distance_to_plot.max() + self.x0
        yr = 1.2 * np.sin(theta) * self.distance_to_plot.max() + self.y0
        nr = int( np.round( self.distance_to_plot.max() * 1.2 / dx ) )
        self.ray = {}
        self.ray['theta'] = theta
        self.ray['x'] = np.linspace(self.x0, xr, nr).T  # sereis of x for each theta
        self.ray['y'] = np.linspace(self.y0, yr, nr).T
        self.ray['n'] = nr
        self.ray['hor'] = np.linspace(0, self.distance_to_plot.max() * 1.2, self.ray['n'])

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
        c_v = np.array([fnc(_x, _y)[0] for _x, _y in zip(self.circle_for_direction['x'], self.circle_for_direction['y'])])

        hdx = c_v.argmax()

        if self.kind == 'skelton':
            # simply return the ray
            #return self.x0, self.y0, self.distance, self.c_theta[hdx], self.r_x[hdx, -1], self.r_y[hdx, -1]
            return self.x0, self.y0, self.distance_to_plot, self.ray['theta'][hdx], self.ray['x'][hdx, -1], self.ray['y'][hdx, -1]

        if self.kind == 'cross':
            
            c_x = np.roll(self.circles[0]['x'], -(hdx - self.circles[0]['n']))[0:(2*self.circles[0]['n']+1)]
            c_y = np.roll(self.circles[0]['y'], -(hdx - self.circles[0]['n']))[0:(2*self.circles[0]['n']+1)]

            c_v = np.empty([len(self.z), len(c_x), ])
            for k in range(len(self.z)):

                fnc = interp2d(self.x, self.y, arr[k])
                c_v[k,:] = [fnc(_x, _y)[0] for _x, _y in zip(c_x, c_y)]
            

            self.hor = self.circles[0]['hor']

            self.current_arr = c_v
            self.cuttent_tstamp = self.tstamps[tidx]

        elif self.kind == 'along':
            r_x = self.ray['x'][hdx]
            r_y = self.ray['y'][hdx]

            r_v = np.empty([len(self.z), len(r_x)])
            for k in range(len(self.z)):
                fnc = interp2d(self.x, self.y, arr[k])
                r_v[k,:] = [fnc(_x, _y)[0] for _x, _y in zip(r_x, r_y)]

            self.hor = self.ray['hor']
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