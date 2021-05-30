try:
    from . import plotter_core as pc
except ImportError:
    import plotter_core as pc

import matplotlib.pyplot as plt
import matplotlib as mpl
from importlib import reload

mpl.use('Agg')
reload(pc)


class Plotter:
    def __init__(self, array, tstamps, projection=None, extent=None, x=None, y=None,
                 plotter_options=None):
        """
        Wrapper for single PlotterCore, allows savefig() and savemp4()

        :param np.ndarray array:
        :param np.ndarray tstamps:
        :param ccrs.CRS projection:
        :param list extent:
        :param np.ndarray x:
        :param np.ndarray y:
        :param dict plotter_options:
        """
        self.tstamps = tstamps
        self.plotter = pc.PlotterCore(array, tstamps, projection=projection,
                                extent=extent, x=x, y=y, plotter_options=plotter_options)
        self.ax = self.plotter.ax

    def savefig(self, oname, tidx=None, footnote=None, *args, **kwargs):
        """
        Saves single image file

        :param str oname: output file name
        :param int tidx: index of tstamps
        :param str footnote: footnote overwrite
        :param list args: extra arguments passed to plt.savefig()
        :param dict kwargs: extra arguments passed to plt.savefig()
        """
        self.plotter.update(tidx, footnote)
        plt.savefig(oname, *args, **kwargs)

    def __call__(self, oname, *args, **kwargs):
        """savefig()"""
        self.savefig(oname, *args, **kwargs)

    def savemp4(self, oname, wdir=None, nthreads=None, odir='.'):
        """
        Saves MP4 animation

        :param str oname: output MP4 file name
        :param str wdir: dir to save intermediate PNG files
        :param nthreads: number of threads to use on parallel machine
        :param odir: dir to save uptut file
        """
        pc.pu.savemp4(self, oname=oname, wdir=wdir, nthreads=nthreads,
                odir=odir)



