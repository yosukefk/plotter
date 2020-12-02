import plotter_core as pc
import matplotlib.pyplot as plt
from importlib import reload
reload(pc)
class plotter:
    def __init__(self, array, tstamps, projection=None, extent=None,
            plotter_options={}):
        self.p = pc.plotter_core(array, tstamps, projection, extent, plotter_options)
        self.ax = self.p.ax
    def __call__(self, oname, tidx=None, footnote=''):
        self.p(tidx, footnote)
        plt.savefig(oname)
    def customize(self, fnc, *args):
        # plotter_core has per axis customization accessed:
        # things like showwin boundaries
        self.p.customize(fnc, *args)

def tester():
    import reader
    dat = reader.tester()
    v = dat['v']
    nt,ny,nx = v.shape
