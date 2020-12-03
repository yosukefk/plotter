import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np


class plotter_core:
    def __init__(self, array, tstamps, projection=None, extent=None,
            plotter_options = None):
        # i have to know the axes being used, even user wants default
        # so i grab default axes here and hold onto it
        if plotter_options is None: plotter_options = {}
        self.fig = plotter_options.setdefault('fig', plt.figure())
        pos = plotter_options.get('pos', None)
        self.arr = array
        self.tstamps = tstamps
        self.extent = extent

        self.imshow_options = plotter_options.get('imshow_options', None)
        self.contour_options = plotter_options.get('contour_options', None)
        self.colorbar_options = plotter_options.get('colorbar_options', {})

        self.footnote_options = plotter_options.get('footnote_options', {})

        self.title = plotter_options.get('title', None)
        self.customize_after = plotter_options.get('customize_after', None)

        # assume TCEQ's lambert
        if projection is None:
            projection = ccrs.LambertConformal(central_longitude=-97, central_latitude=40,
                    standard_parallels=(33,45), globe=ccrs.Globe(semimajor_axis=6370000,
                        semiminor_axis=6370000))
            print(projection)



        if pos:
            self.ax = self.fig.add_subplot(*pos, projection = projection)
        else:
            self.ax = self.fig.add_subplot( projection = projection)
        self.ax.set_extent(self.extent, crs=projection)
        if self.title is not None:
            self.ax.set_title(self.title, loc='center')


        # other customizations
        if 'customize_once' in plotter_options:
            self.customize(plotter_options['customize_once'])

        self.hasdata = False
        self.im = None
        self.cnt = None

    def __call__(self, tidx = None, footnote='', title=None):
        if tidx is None: tidx = 0
        arr = self.arr[tidx]
        ts = self.tstamps[tidx]

        if self.imshow_options is None:
            pass
        else:
            if self.im is None:
                kwds = self.imshow_options
                self.im = self.ax.imshow(arr, extent=self.extent, **kwds)

                if self.colorbar_options is not None:
                    kwds = self.colorbar_options
                    self.cb = plt.colorbar(mappable=self.im, ax = self.ax,
                            **kwds)

                if footnote is not None:
                    self.footnote = self.ax.annotate(footnote, 
                            xy=(0.5, 0), # bottom center
                            xytext=(0,-6), # drop 6 ponts below (works if there is no x axis label)
                            #xytext=(0,-18), # drop 18 ponts below (works with x-small fontsize axis label)
                            xycoords = 'axes fraction',
                            textcoords = 'offset points',
                            ha='center',va='top')

            else:
                self.im.set_data(arr)

                if footnote is not None:
                    self.footnote.set_text(footnote)

        if self.contour_options is None:
            pass
        else:
            if self.cnt is None:
                kwds = self.contour_options
                self.cnt = self.ax.contourf(arr, extent=self.extent, **kwds)

                if self.colorbar_options is not None:
                    kwds = self.colorbar_options
                    self.cb = plt.colorbar(mappable=self.cnt, ax = self.ax,
                            **kwds)

                if footnote is not None:
                    self.footnote = self.ax.annotate(footnote, 
                            xy=(0.5, 0), # bottom center
                            xytext=(0,-6), # drop 6 ponts below (works if there is no x axis label)
                            #xytext=(0,-18), # drop 18 ponts below (works with x-small fontsize axis label)
                            xycoords = 'axes fraction',
                            textcoords = 'offset points',
                            ha='center',va='top')
            else:
                if footnote is not None:
                    self.footnote.set_text(footnote)


        # customizeration needed after updating data
        if self.customize_after: 
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

