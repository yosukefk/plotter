from . import plotter_util as pu
from . import plotter_footnote as pf
from . import plotter_core as pc

import matplotlib.pyplot as plt
import matplotlib as mpl

import numpy as np
from scipy.interpolate import interp2d

class PlotterDwprofPlanview(pc.PlotterCore):
    def __init__(self, array, tstamps, z, origin=None, distance=None, distance_to_plot=None, distance_for_direction=None, half_angle=None, half_arclen=None, kind=None,
                 projection=None, extent=None, x=None, y=None, plotter_options=None):

        #print('plan', half_angle, half_arclen)

        super().__init__( array[:,0,:,:], tstamps, 
                 projection=projection, extent=extent, x=x, y=y, plotter_options=plotter_options)

        
        self.pdw = PlotterDwprof( array, tstamps, z, origin=origin, distance=distance, distance_to_plot=distance_to_plot, distance_for_direction=distance_for_direction, 
                half_angle=half_angle, half_arclen=half_arclen, kind='skelton',
                 projection=projection, extent=extent, x=x, y=y, plotter_options={k:v for k,v in plotter_options.items() if k != 'customize_once'})

    def update(self, tidx=None, footnote=None, title=None):
        super().update(tidx=tidx, footnote=footnote, title=title)
        self.pdw.update(tidx)
            #return self.x0, self.y0, self.ray['x'][hdx, -1], self.ray['y'][hdx, -1], self.distance_to_plot, self.half_angle, self.ray['theta'][hdx]
        x0, y0, x1, y1, radius, half_angle, theta, half_stretch = self.pdw.update(tidx)
        if hasattr(self, 'footprints'): 
            for x in self.footprints:
                x.remove()
        #self.ax.add_patch(plt.Circle((x0,y0), radius, fill=False, color='black', lw=.6))
        self.footprints = []
        #for rad in radius:
        for rad, ha, hs in zip(radius, half_angle, half_stretch):
            #print('r,h=', rad, ha)
            #arc = self.ax.add_patch(mpl.patches.Arc((x0,y0), rad*2, rad*2, angle=theta/np.pi*180, theta1=-self.pdw.half_angle, theta2=self.pdw.half_angle,  color='black', lw=.6))
            arc = self.ax.add_patch(mpl.patches.Arc((x0,y0), rad*2, rad*2, angle=theta/np.pi*180, theta1=-ha, theta2=ha,  color='black', lw=.6))
            self.footprints.append(arc)
            if hs > 0:
                xx0 = x0 + rad * np.cos(theta-ha*np.pi/180)
                yy0 = y0 + rad * np.sin(theta-ha*np.pi/180)
                xx1 = xx0 + hs * np.cos(theta-ha*np.pi/180-.5*np.pi)
                yy1 = yy0 + hs * np.sin(theta-ha*np.pi/180-.5*np.pi)
                stretch1 = self.ax.add_line(mpl.lines.Line2D((xx0, xx1), (yy0,yy1), color='black', lw=.6))
                xx0 = x0 + rad * np.cos(theta+ha*np.pi/180)
                yy0 = y0 + rad * np.sin(theta+ha*np.pi/180)
                xx1 = xx0 + hs * np.cos(theta+ha*np.pi/180+.5*np.pi)
                yy1 = yy0 + hs * np.sin(theta+ha*np.pi/180+.5*np.pi)
                stretch2 = self.ax.add_line(mpl.lines.Line2D((xx0, xx1), (yy0,yy1), color='black', lw=.6))
                self.footprints.append(stretch1)
                self.footprints.append(stretch2)
        ray = self.ax.add_line(mpl.lines.Line2D((x0,x1), (y0, y1), color='black', lw=.6))
        self.footprints.append(ray)

class PlotterDwprof:
    def __init__(self, array, tstamps, z, origin=None, distance=None, distance_to_plot=None, distance_for_direction=None, half_angle=None, half_arclen=None, kind=None,
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

        #print('dwp', half_angle, half_arclen)

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

        half_stretch = None
        if half_angle is None: 
            if half_arclen is None:
                #half_angle = 30
                half_angle = 30 * np.ones_like(self.distance_to_plot)
                half_arclen =  circ * half_angle / 360.
            else:
                circ = 2 * np.pi * self.distance_to_plot # circumference
                half_angle = 360 * half_arclen / circ
        else:
            half_angle = np.atleast_1d(half_angle)

            if len(self.distance_to_plot) != len(half_angle):
                if len(half_angle) == 1:
                    half_angle = np.repeat(half_angle, len(self.distance_to_plot))
                else:
                    raise ValueError("# of 'distance_to_plot' and 'half_angle' incosistent: {}, {}".format(self.distance_to_plot, half_angle))

            if half_arclen is None:
                half_arclen =  circ * half_angle / 360.
            else:
                half_arclen = np.atleast_1d(half_arclen)
                if len(half_angle) != len(half_arclen):
                    if len(half_arclen) == 1:
                        half_arclen = np.repeat(half_arclen, len(half_angle))
                    else:
                        raise ValueError("# of 'half_angle' and 'half_arclen' incosistent: {}, {}".format(half_angle, half_arclen))

                half_angle1 = half_angle
                half_arclen2 = half_arclen
                circ = 2 * np.pi * self.distance_to_plot # circumference
                half_angle2 = 360 * half_arclen / circ
                half_arclen1 =  circ * half_angle / 360.

                half_angle = np.minimum(half_angle1, half_angle2)
                half_stretch = np.maximum(half_arclen2 - half_arclen1, 0)

        if half_stretch is None:
            half_stretch = np.zeros_like(half_angle)

        self.half_angle = half_angle
        self.half_stretch = half_stretch
        self.half_arclen = half_arclen

#        print('kn', kind)
#        print('dp', self.distance_to_plot)
#        print('ha', self.half_angle)
#        print('hl', self.half_arclen)



        self.kind = kind
        if self.kind != 'skelton':
            # i have to know the axes being used, even user wants default
            # so i grab default axes here and hold onto it
            self.fig = plotter_options.get('fig', plt.figure())
            pos = plotter_options.get('pos', None)

        if self.kind == 'cross':
            if len(self.distance_to_plot) != 1:
                raise ValueError("For 'cross' plot, one and only one value for distance_to_plot: {}".format(self.distance_to_plot))


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

        # *** prepare circles and ray ***

        # circumference 
        circ = 2 * np.pi * self.distance_to_plot # circumference
        # resolution (half of data' resolution)
        dx = .5 * (self.x[-1] - self.x[0]) / (len(self.x) - 1)
        # count of nodes on circle
        ndiv = np.round( circ / dx ).astype(int)
        # incremental angle
        dtheta = - 2*np.pi / ndiv  # lets go reverse, since decrease in theta goes to right in profile

        # generate coordinates for circle(s)
        self.circles = []

        for dst, nd, dth, ha in zip(self.distance_to_plot, ndiv, dtheta, self.half_angle):
            dct = {}
            theta = np.arange(nd) * dth
            dct['theta'] = theta
            dct['x'] = np.cos(theta) * dst + self.x0
            dct['y'] = np.sin(theta) * dst + self.y0
            dct['s'] = - np.pi * theta   # s = coordinate on the arc, it goes from 0 to positive
            dct['m'] = int(np.ceil(len(theta) * ha / 360)) # count of points on arc to cover half_angle (e.g. 30 degree)
            dct['n'] = 2 * dct['m'] + 1 # count of points on arc to cover full_angle (e.g 60 degree)
            #dct['hor'] = np.linspace(dst * np.pi * dth * dct['n'], - dst * np.pi * dth * dct['n'], 2*dct['n'] + 1) # horizontal coord in plot, centered 0   TODO why n, not m???
            dct['hor'] = np.linspace(dst * dth * dct['m'], - dst * dth * dct['m'], 2*dct['m'] + 1) # horizontal coord in plot, centered 0   TODO why n, not m???

            self.circles.append(dct)

        # prepare circle needed for picking direction
        circ = 2 * np.pi * self.distance_for_direction # circumference
        ndiv = np.round( circ / dx ).astype(int)
        dtheta = - 2*np.pi / ndiv  # lets go reverse, since decrease in theta goes to right in profile
        theta = np.arange(ndiv) * dtheta
        self.circle_for_direction = {}
        self.circle_for_direction['theta'] = theta
        self.circle_for_direction['x'] = np.cos(theta) * self.distance_for_direction + self.x0
        self.circle_for_direction['y'] = np.sin(theta) * self.distance_for_direction + self.y0

        # prepare lays
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
        depth = z[1:] - z[:-1]
        depth = np.insert(depth, 0, z[0])
        self.arr2d = self.arr.transpose(0, 2, 3, 1).dot(depth)


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
            # return info related ary at the time:
            # origin
            # ray endpoint
            # array of distance to plot
            # half angle at each distance
            # direction theta at the time
#            print('s dtp', self.distance_to_plot)
#            print('s ha', self.half_angle)
            return self.x0, self.y0, self.ray['x'][hdx, -1], self.ray['y'][hdx, -1], self.distance_to_plot, self.half_angle, self.ray['theta'][hdx], self.half_stretch

        if self.kind == 'cross':
            assert len(self.circles) == 1

            # xy coordinates on the map
            c_x = np.roll(self.circles[0]['x'], -(hdx - self.circles[0]['m']))[0:(2*self.circles[0]['m']+1)]
            c_y = np.roll(self.circles[0]['y'], -(hdx - self.circles[0]['m']))[0:(2*self.circles[0]['m']+1)]

            # conc at the points above
            c_v = np.empty([len(self.z), len(c_x), ])
            for k in range(len(self.z)):
                fnc = interp2d(self.x, self.y, arr[k])
                c_v[k,:] = [fnc(_x, _y)[0] for _x, _y in zip(c_x, c_y)]

            self.hor = self.circles[0]['hor']
            self.current_arr = c_v
            self.cuttent_tstamp = self.tstamps[tidx]
            #print('ccc ca shp', self.current_arr.shape)
            #print('ccc hor shp', self.hor.shape)

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

                #print(self.kind, self.hor.shape, self.z.shape, self.current_arr.shape)
                self.cnt = self.ax.contourf(self.hor, self.z, self.current_arr,  **kwds)
                self.mappable = self.cnt
#                print(self.kind)
#                print(self.half_arclen)
                if self.kind == 'cross':
                    self.ax.set_xlim(left=-self.half_arclen, right=+self.half_arclen)

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
