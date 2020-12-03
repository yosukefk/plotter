from . import plotter_core as pc
import matplotlib as mpl
import matplotlib.pyplot as plt
from importlib import reload
import warnings
reload(pc)
class Plotter:
    def __init__(self, arrays, tstamps, projection=None, extent=None,
            plotter_options=None, figure_options={}):

        # assumptions:  
        #   tstamps, projection, extent are shared across plots
        #   landscape orientation, all plots side by side

        self.figure_options = figure_options

        np = len(arrays)

        # make sure that plotter_options are unintentionally shared across
        # plots
        if plotter_options is None:
            # if none provided, preapre empty dict for each
            plotter_options = [{} for _ in range(np)]
        elif isinstance(plotter_options, dict):
            # if one set of options are provided, duplicate them
            warnings.warn('plotter options are duplicated for all plots')
            # TODO imshow options may needed to be cloned as well
            plotter_options = [plotter_options] + [ plotter_options.copy()
                    for _ in range(np-1)]
        elif '__len__' in dir(plotter_options):
            # if multiple sets of options are provided, make sure that they are
            # pointing to two different object, since i have to manage them
            # independently
            assert len(plotter_options) == np
            for i in range(1, np):
                if id(plotter_options[0]) == id(plotter_options[i]):
                    warnings.warn(f'plotter options {i} is unlinked from first one')
                    plotter_options[i] = plotter_options[i].copy()
                if 'imshow_options' in plotter_options[0]:
                    if id(plotter_options[0]['imshow_options']) == \
                            id(plotter_options[i].get('imshow_options',
                                None)):
                        warnings.warn(f'imshow options {i} is unlinked from first one')
                        plotter_options[i]['imshow_options'] = \
                                plotter_options[i]['imshow_options'].copy()
                        

        # one figure to hold all plots
        self.fig = plt.figure()

        # specifiy the subplot positions
        for i in range(np):
            plotter_options[i]['fig'] = self.fig
            plotter_options[i]['pos'] = (1,np,i+1)
        
        # create plots
        self.plotters = [pc.plotter_core(arr, tstamps, projection, extent,
            po) for arr,po in zip(arrays, plotter_options)]
        self.axes = [p.ax for p in self.plotters]
            

    def __call__(self, oname, tidx=None, footnote='', suptitle=None, titles=None):

        # remember if plots were blank
        haddata = self.plotters[0].im is not None

        for p in self.plotters:
            p(tidx, footnote)

        # if it was blank, need some initalization
        if not haddata:
            cbopt =  self.figure_options.get('colorbar_options', None)
            if cbopt is not None:
                self.fig.subplots_adjust(wspace=.1)
                self.fig.colorbar(
                        mappable=self.plotters[0].im,
                        ax=self.axes,
                        shrink=.6,
                        **cbopt)
        if not suptitle is None:
            self.fig.suptitle( suptitle )
        if not titles is None:
            for ax,ttle in zip(self.axes, titles):
                ax.set_title(ttle)

        self.fig.savefig(oname, bbox_inches='tight')

    def customize(self, fnc, *args):
        # plotter_core has per axis customization accessed:
        # things like showwin boundaries
        self.p.customize(fnc, *args)

def tester():
    import reader
    dat = reader.tester()
    v = dat['v']
    nt,ny,nx = v.shape
