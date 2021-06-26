from . import plotter_util as pu
import warnings

class PlotterVprof:
    def __init__(self, array, tstamps, z, idx=None, jdx=None, plotter_options=None):
        if plotter_options is None: plotter_options = {}
        self.fig = plotter_options.get('fig', plt.figure())
        pos = plotter_options.get('pos', None)

        self.arr = array
        self.tstamps = tstamps
        self.z = z

        if idx is None:
            if jdx is None:
                raise ValueError('ijdx')
            else:
                islice = slice(None,None)
                jslice = jdx
        else:
            if jdx is None:
                islice = idx
                jslice = slice(None,None)
            else:
                raise ValueError('ijslice')
        self.idx = idx
        self.jdx = jdx
        self.islice = islice
        self.jslice = jslice

        if 'imshow_option' in plotter_options:
            warnings.warn('imshow not supported', pu.PlotterWarning )
        self.contour_options = plotter_options.get('contour_options', {})

        self.colorbar_options = plotter_options.get('colorbar_options', {})

        self.footnote = plotter_options.get('footnote', None)
        self.footnote_options = plotter_options.get('footnote_options', {})
        self.footnote_manager = None

        self.title = plotter_options.get('title', None)
        self.title_options = plotter_options.get('title_options', None)

        # create plots 
        if pos:
            self.ax = self.fig.add_subprot(*pos)
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

        # other customizations
        if 'customize_once' in plotter_options:
            self.customize(plotter_options['customize_once'])

        self.hasdata = False
        self.cnt = None
        self.mappable = None
        self.current_arr = None
        self.current_tstamp = None

    def update(self, tidx=None, footnote=None, title=None):
        if tidx is None: tidx = 0
        idx = [tidx, :, self.jslice, self.islice]
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
                self.cnt = self.ax.contourf(self.x, self.y, arr,
                                            extent=self.extent, transform=self.projection, **kwds)

            if self.footnote_manager is not None:
                self.footnote_manager(footnote)

        else:

            if self.contour_options is not None:
                kwds = self.contour_options
                if self.x is None:
                    self.x = np.arrange(arr.shape[-1])
                self.cnt = self.ax.contourf(self.x, self.z, arr,  **kwds)
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
