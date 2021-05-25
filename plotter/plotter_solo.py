try:
    from . import plotter_core as pc
except ImportError:
    import plotter_core as pc

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')

from importlib import reload
reload(pc)


class Plotter:
    def __init__(self, array, tstamps, projection=None, extent=None, x=None, y=None,
                 plotter_options=None):
        self.tstamps = tstamps
        self.p = pc.PlotterCore(array, tstamps, projection=projection,
                                extent=extent, x=x, y=y, plotter_options=plotter_options)
        self.ax = self.p.ax

    def savefig(self, oname, tidx=None, footnote=None, *args, **kwargs):
        self.p.update(tidx, footnote)
        plt.savefig(oname, *args, **kwargs)

    #def __call__(self, oname, tidx=None, footnote=''):
    def __call__(self, oname, *args, **kwargs):
        self.savefig(oname, *args, **kwargs)

    def savemp4(self, oname):
        pc.pu.savemp4(self, oname=oname)



