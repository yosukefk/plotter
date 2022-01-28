try:
    from . import plotter_core as pc
    from . import plotter_vprof as pv
    from . import plotter_trisurf as pt
    #from . import plotter_dwprof as pw
    from . import plotter_util as pu
    from . import plotter_footnote as pf
except ImportError:
    import plotter_core as pc
    import plotter_vprof as pv
    import plotter_trisurf as pt
    #import plotter_dwprof as pw
    import plotter_util as pu
    import plotter_footnote as pf

import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings

from importlib import reload
reload(pc)
mpl.use('Agg')


class Plotter:
    def __init__(self, arrays, tstamps, projection=None, extent=None,
                 x=None, y=None, xs=None, ys=None, z=None, plotter_options=None, figure_options=None):
        """
        Wrappter for multple PlotterCore, allows savefig() and savemp4()

        :param list arrays: list of 3-d arrays for each plot
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t), common across plots
        :param ccrs.CRS projection: projection of xy coordinate of data, common across plots
        :param list extent: xy extent of data, with with coordinate of projection, common across plots
        :param np.ndarray x: x coordinate of data, common across plots
        :param np.ndarray y: y coordinate of data, common across plots
        :param np.ndarray z: z coordinate of data, common across plots
        :param dict or list plotter_options: all the arguments passed to all plot, or list of options one for each plot
        :param figure_options: options passed to "figure", the container for the plots

        assumptions:
          tstamps, projection, extent are shared across plots
          landscape orientation, all plots side by side
        """

        # everython but these are passed to plt.figure()
        self.figure_options_for_plotter = [
            'footnote', 'footnote_options', 'colorbar_options', 'suptitle',
            'nrow', 'ncol', 
        ]

        if figure_options is None:
            figure_options = {}
        self.figure_options = figure_options

        self.nplot = len(arrays)

        self.tstamps = tstamps

        # make sure that plotter_options are unintentionally shared across
        # plots
        if plotter_options is None:
            # if none provided, preapre empty dict for each
            plotter_options = [{} for _ in range(self.nplot)]
        elif isinstance(plotter_options, dict):
            # if one set of options are provided, duplicate them
            warnings.warn('plotter options are duplicated for all plots',
                          category=pu.PlotterWarning)
            # TODO imshow options may needed to be cloned as well
            plotter_options = [plotter_options] + [plotter_options.copy()
                                                   for _ in range(self.nplot - 1)]
        elif '__len__' in dir(plotter_options):
            # if multiple sets of options are provided, make sure that they are
            # pointing to two different object, since i have to manage them
            # independently
            assert len(plotter_options) == self.nplot
            for i in range(1, self.nplot):
                if id(plotter_options[0]) == id(plotter_options[i]):
                    warnings.warn(f'plotter options {i} is unlinked from first one',
                                  category=pu.PlotterWarning)
                    plotter_options[i] = plotter_options[i].copy()
                if 'imshow_options' in plotter_options[0]:
                    if id(plotter_options[0]['imshow_options']) == \
                            id(plotter_options[i].get('imshow_options',
                                                      None)):
                        warnings.warn(f'imshow options {i} is unlinked from first one',
                                      category=pu.PlotterWarning)
                        plotter_options[i]['imshow_options'] = \
                            plotter_options[i]['imshow_options'].copy()

        # one figure to hold all plots
        self.fig = plt.figure(**{k: v for k, v in self.figure_options.items() if k not
                                 in self.figure_options_for_plotter})

        self.footnote = figure_options.get('footnote', None)
        self.footnote_options = figure_options.get('footnote_options', {})
        self.footnote_manager = None
        self.suptitle = figure_options.get('suptitle', None)

        # specify nrow/ncol of subplots
        nrow = figure_options.get('nrow', None)
        ncol = figure_options.get('ncol', None)
        if ncol is None:
            if nrow is None:
                if self.nplot < 4:
                    nrow = 1
                elif self.nplot < 9:
                    nrow = 2
                else:
                    nrow = 3
            ncol = (self.nplot + nrow - 1) // nrow
        else:
            if nrow is None:
                print('np, ncol', self.nplot, ncol)
                nrow=  (self.nplot + ncol  - 1) // ncol  
        self.nrow = nrow
        self.ncol = ncol
        print('ncol', ncol, 'nrow', nrow)

        # specify the subplot positions
        for i in range(self.nplot):
            plotter_options[i]['fig'] = self.fig
            plotter_options[i].setdefault('pos', (nrow, ncol, i + 1))

        if x is None and xs is not None:
            use_xs = True
        else:
            use_xs = False
            xs = [x] * len(arrays)
            ys = [y] * len(arrays)

        # create plots
        if z is None:
            self.plotters = [pc.PlotterCore(arr, tstamps, projection=projection, extent=extent,
                                                x=x, y=y, plotter_options=po) 
                                 for arr, po, x, y in zip(arrays, plotter_options, xs, ys)]
        else:
            self.plotters = []
            for arr, po, x, y  in zip(arrays, plotter_options, xs, ys):
                if arr is None:
                    self.plotters.append(
                        pc.PlotterEmpty(None, tstamps, plotter_options=po)
                    )
                elif 'kdx' in po:
                    kdx = po.pop('kdx', None)
                    self.plotters.append(
                        pc.PlotterCore(arr[:, kdx, :, :], tstamps, projection=projection, 
                                       extent=extent, x=x, y=y, plotter_options=po) 
                    )
                elif 'downwind_options' in po:
                    # delayed import
                    try:
                        from . import plotter_dwprof as pw
                    except ImportError:
                        import plotter_dwprof as pw
                    downwind_options = po.pop('downwind_options')
                    #print(downwind_options)
                    if downwind_options['kind'] == 'planview':
                        self.plotters.append(
                                    pw.PlotterDwprofPlanview(arr, tstamps, projection=projection, extent=extent, 
                                                   x=x, y=y, z=z, 
                                                   origin=downwind_options['origin'], 
                                                   distance=downwind_options.get('distance',None), 
                                                   distance_to_plot=downwind_options.get('distance_to_plot',None), 
                                                   distance_for_direction=downwind_options.get('distance_to_plot',None), 
                                                   kind=downwind_options['kind'], 
                                                   plotter_options=po)
                        )
                    else:
                        self.plotters.append( 
                                    pw.PlotterDwprof(arr, tstamps, projection=projection, extent=extent, 
                                                   x=x, y=y, z=z, 
                                                   origin=downwind_options['origin'], 
                                                   distance=downwind_options.get('distance',None), 
                                                   distance_to_plot=downwind_options.get('distance_to_plot',None), 
                                                   distance_for_direction=downwind_options.get('distance_to_plot',None), 
                                                   kind=downwind_options['kind'], 
                                                   plotter_options=po)
                        )

                else:
                    idx = po.pop('idx', None)
                    jdx = po.pop('jdx', None)
                    if idx is None and jdx is None:
                        # 3d isosurface plot
                        zlim = po.pop('zlim', None)
                        self.plotters.append(   
                                        pt.PlotterTrisurf(arr,
                                                   tstamps, projection=projection, extent=extent,
                                                   x=x, y=y, z=z, zlim=zlim,
                                                   plotter_options=po)
                        )
                    else:
                        # vertical profile
                        self.plotters.append(
                            pv.PlotterVprof(arr, 
                                            tstamps,projection=projection, extent=extent, 
                                            x=x, y=y, # passing x,y coordinate in map unit
                                            z=z, idx=idx, jdx=jdx,
                                                   plotter_options=po)
                        )
        self.axes = [p.ax for p in self.plotters]
        for pp in self.plotters:
            if not isinstance(pp, pc.PlotterEmpty):
                self.first_nonempty_plotter= pp
                break


    def savefig(self, oname, tidx=None, footnote=None, suptitle=None,
                titles=None, footnotes=None, *args, **kwargs):
        """
        Saves single image file

        :param str oname: output file name
        :param int tidx: index of tstamps
        :param str footnote: footnote for the figure (container)
        :param str suptitle: suptitle (title for container)
        :param list titles: title for each plot
        :param list footnotes: footnotes for each plot
        :param args: extra arguments passed to plt.savefig()
        :param kwargs: extra arguments passed to plt.savefig()
        """
        # remember if plots were blank
        haddata = self.plotters[0].hasdata

        if footnotes is None or isinstance(footnotes, str) or \
                 len(footnotes) != len(self.plotters):
            footnotes = [footnotes] * len(self.plotters)

        for p, fn in zip(self.plotters, footnotes):

            p.update(tidx=tidx, footnote=fn)

        # if it was blank, need some initalization
        if not haddata:
            cbopt = self.figure_options.get('colorbar_options', None)
            if cbopt is not None:
                self.fig.subplots_adjust(wspace=.1)

                # ugly hardwired values...
                # tried to use
                if self.nplot <= 2:
                    my_shrink = .7
                elif self.nplot >= 3:
                    my_shrink = .5
                else:
                    my_shrink = .5

                self.fig.colorbar(
                    mappable=self.first_nonempty_plotter.mappable,
                    ax=self.axes,
                    use_gridspec=True,
                    **{'shrink': my_shrink, **cbopt})

            if self.footnote is None:
                # print('mk fnm')
                # print('self.footnote = ', self.footnote)
                # print('self.footnote_options = ', self.footnote_options)
                self.footnote_manager = pf.FootnoteManager(self, self.footnote,
                                                           self.footnote_options)
                self.footnote_manager()

            # if footnote is not None:
            else:
                # no clue why, but y=0.2 puts text nicely below the plots, for pair case...
                if self.nplot <= 2:
                    my_ypos = .2
                elif self.nplot >= 3:
                    my_ypos = .3
                else:
                    my_ypos = .3
                self.footnote = self.fig.text(0.5, my_ypos, footnote,
                                              ha='center', va='top')
        else:
            if self.footnote_manager is not None:
                # print('setting fn {footnote}')

                self.footnote_manager(footnote)

            elif footnote is not None:
                self.footnote.set_text(footnote)

        if suptitle is None:
            suptitle = self.suptitle

        if suptitle is not None:
            # warnings.warn('i dont like suptitle after all', DeprecationWarning)
            # if not isinstance(suptitle, dict):
            #     suptitle = {'t': suptitle,
            #                 }
            # self.fig.suptitle(**suptitle)
            my_suptitle = {'x': .1, 'y': .8, 'fontsize': 'large'}
            if isinstance(suptitle, dict):
                my_suptitle.update(suptitle)
            else:
                my_suptitle['s'] = suptitle 
            self.fig.text(**my_suptitle)

        if titles is not None:
            for ax, ttle in zip(self.axes, titles):
                ax.set_title(ttle)

        self.fig.savefig(oname, bbox_inches='tight', *args, **kwargs)

    def __call__(self, oname, *args, **kwargs):
        """savefig()"""
        self.savefig(oname, *args, **kwargs)

    def savemp4(self, oname, wdir=None, nthreads=None, odir='.'):
        """
        Save MP4 animation

        :param str oname: output MP4 file name
        :param str wdir: dir to save intermediate PNG files (None will use Temporary dir)
        :param int nthreads: number of threads to use on parallel machine
        :param str odir: dir to save output file
        """
        pc.pu.savemp4(self, oname=oname, wdir=wdir, nthreads=nthreads,
                      odir=odir)
