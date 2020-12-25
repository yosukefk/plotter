try:
    from . import plotter_core as pc
    from . import plotter_util as pu
except ImportError:
    import plotter_core as pc
    import plotter_util as pu

import matplotlib.pyplot as plt
from importlib import reload
import warnings

reload(pc)


class Plotter:
    def __init__(self, arrays, tstamps, projection=None, extent=None, x=None, y=None,
                 plotter_options=None, figure_options=None):

        # assumptions:  
        #   tstamps, projection, extent are shared across plots
        #   landscape orientation, all plots side by side

        if figure_options is None:
            figure_options = {}
        self.figure_options = figure_options

        self.nplot = len(arrays)

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
        self.fig = plt.figure()

        # specify the subplot positions
        for i in range(self.nplot):
            plotter_options[i]['fig'] = self.fig
            plotter_options[i]['pos'] = (1, self.nplot, i + 1)

        # create plots
        self.plotters = [pc.PlotterCore(arr, tstamps, projection=projection, extent=extent,
                                        x=x, y=y, plotter_options=po) for arr, po in zip(arrays, plotter_options)]
        self.axes = [p.ax for p in self.plotters]

        figure_customizers = figure_options.pop('figure_customizers', None)

        if figure_customizers:
            for fc in figure_customizers:
                fc(self.fig)

    # TODO rename footnotes to subplot_footnote or something like that...
    def __call__(self, oname, tidx=None, footnote='', suptitle=None,
            titles=None):#, footnotes=''):

        # remember if plots were blank
        haddata = self.plotters[0].hasdata

        #if isinstance(footnotes, str) or len(footnotes) != len(self.plotters):
        #    footnotes = [footnotes] * len(self.plotters)

        #print(footnotes)
        #    if footnotes:
        #for p,fn in zip(self.plotters, footnotes):

        #    p(tidx, footnote=fn)
        for p in self.plotters:

            p(tidx, footnote=None)

        # if it was blank, need some initalization
        if not haddata:
            cbopt = self.figure_options.get('colorbar_options', None)
            fnopt = self.figure_options.get('footnote_options', None)
            if cbopt is not None:
                self.fig.subplots_adjust(wspace=.1)

                # ugly hardwired values...
                # tried to use
                if self.nplot <= 2:
                    my_shrink = .7
                elif self.nplot >= 3:
                    my_shrink = .5

                # TODO do this on plotter_core too
                cb_customizers = cbopt.pop('colorbar_customizers', None)

                cb = self.fig.colorbar(
                    mappable=self.plotters[0].mappable,
                    ax=self.axes,
                    use_gridspec=True,
                    **{'shrink': my_shrink, **cbopt})
                for cbc in cb_customizers:
                    cbc(cb)


            if footnote is not None or fnopt is not None:
                # no clue why, but y=0.2 puts text nicely below the plots, for pair case...
                if self.nplot <= 2:
                    my_ypos = .2
                elif self.nplot >=3:
                    my_ypos = .3


                # default options
                my_footnote_options = {
                        'x': 0.5, 
                        'y': my_ypos,
                        's': '',
                        'ha': 'center',
                        'va': 'top',
                        }
                if footnote is not None:
                    my_footnote_options['s'] = footnote
                if fnopt is not None:
                    my_footnote_options.update(fnopt)
                self.footnote = self.fig.text(**my_footnote_options)
        else:
            if footnote is not None:
                self.footnote.set_text(footnote)




        if not suptitle is None:
            warnings.warn('i dont like suptitle after all', DeprecationWarning)
            if not isinstance(suptitle, dict):
                suptitle = {'t': suptitle}
            self.fig.suptitle(**suptitle)

        if not titles is None:
            for ax, ttle in zip(self.axes, titles):
                ax.set_title(ttle)

        self.fig.savefig(oname, bbox_inches='tight')

