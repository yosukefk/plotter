try:
    from . import plotter_core as pc
    from . import plotter_vprof as pv
except ImportError:
    import plotter_core as pc
    import plotter_vprof as pv

import matplotlib.pyplot as plt
import matplotlib as mpl
from importlib import reload

mpl.use('Agg')
reload(pc)


class Plotter:
    def __init__(self, array, tstamps, projection=None, extent=None, x=None,
                 y=None, z=None, plotter_options=None):
        """
        Wrapper for single PlotterCore, allows savefig() and savemp4()

        :param np.ndarray array:  3-d array of data values, dimensions(t, y, x)
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t)
        :param ccrs.CRS projection: projection of xy coordinate of data
        :param list extent: xy extent of data, with with coordinate of projection
        :param np.ndarray x: x coordinate of data
        :param np.ndarray y: y coordinate of data
        :param dict plotter_options: all the arguments passed to plotter
        """
        self.tstamps = tstamps
        if z is None:
            self.plotter = pc.PlotterCore(array, tstamps, projection=projection,
                                          extent=extent, x=x, y=y, plotter_options=plotter_options)
        else:
            if 'kdx' in plotter_options:
                kdx = plotter_options.pop('kdx', None)
                print(array.shape)
                print(array[:, kdx, :, :].shape)
                self.plotter = pc.PlotterCore(array[:, kdx, :, :], tstamps, projection=projection,
                                              extent=extent, x=x, y=y, plotter_options=plotter_options)
            else:
                idx = plotter_options.pop('idx', None)
                jdx = plotter_options.pop('jdx', None)
                self.plotter = pv.PlotterVprof(array,
                                               tstamps,projection=projection, extent=extent, 
                                               x=x, y=y, z=z, idx=idx, jdx=jdx,
                                               plotter_options=plotter_options)

        self.ax = self.plotter.ax

    def savefig(self, oname, tidx=None, footnote=None, *args, **kwargs):
        """
        Saves single image file

        :param str, Path oname: output file name
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

        :param str, Path oname: output MP4 file name
        :param str, Path wdir: dir to save intermediate PNG files (None will use Temporary dir)
        :param int nthreads: number of threads to use on parallel machine
        :param str, Path odir: dir to save output file
        """
        pc.pu.savemp4(self, oname=oname, wdir=wdir, nthreads=nthreads,
                      odir=odir)
