try:
    from . import plotter_core as pc
except ImportError:
    import plotter_core as pc

import matplotlib.pyplot as plt
from importlib import reload

reload(pc)


class Plotter:
    def __init__(self, array, tstamps, projection=None, extent=None, x=None, y=None,
                 plotter_options=None):
        self.p = pc.PlotterCore(array, tstamps, projection=projection,
                                extent=extent, x=x, y=y, plotter_options=plotter_options)
        self.ax = self.p.ax

    def save(self, oname, tidx=None, footnote=None):
        self.p.update(tidx, footnote)
        plt.savefig(oname)

    #def __call__(self, oname, tidx=None, footnote=''):
    def __call__(self, oname, *args, **kwargs):
        self.save(oname, *args, **kwargs)
