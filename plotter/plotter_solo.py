try:
    from . import plotter_core as pc
    from . import plotter_vprof as pv
    from . import plotter_trisurf as pt
    #from . import plotter_dwprof as pw
except ImportError:
    import plotter_core as pc
    import plotter_vprof as pv
    import plotter_trisurf as pt
    #import plotter_dwprof as pw

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
        :param np.ndarray z: z coordinate of data
        :param dict plotter_options: all the arguments passed to plotter
        """
        self.tstamps = tstamps

        if z is None:
            if array is None:
                self.plotter = pc.PlotterEmpty(array, tstamps, projection=projection,
                                          extent=extent, x=x, y=y, plotter_options=plotter_options)
            elif 'quiver_options' in plotter_options:
                try:
                    from . import plotter_vector as pq
                except ImportError:
                    import plotter_vector as pq
                quiver_options = plotter_options.get('quiver_options', {})
                assert len(array) == 2
                self.plotter = pq.PlotterVector(array[0], array[1], tstamps, projection=projection,
                        extent=extent, x=x, y=y, plotter_options=plotter_options)
            else:
                self.plotter = pc.PlotterCore(array, tstamps, projection=projection,
                                          extent=extent, x=x, y=y, plotter_options=plotter_options)
        else:
            if 'kdx' in plotter_options:
                # plan view plot
                kdx = plotter_options.pop('kdx', None)
                print(array.shape)
                print(array[:, kdx, :, :].shape)
                self.plotter = pc.PlotterCore(array[:, kdx, :, :], tstamps, projection=projection,
                                              extent=extent, x=x, y=y, plotter_options=plotter_options)
            elif 'downwind_options' in plotter_options:
                # delayed import
                try:
                    from . import plotter_dwprof as pw
                except ImportError:
                    import plotter_dwprof as pw
                downwind_options = plotter_options.pop('downwind_options')
                if downwind_options['kind'] == 'planview':
                    self.plotter = pw.PlotterDwprofPlanview(array, tstamps, projection=projection, extent=extent, 
                                               x=x, y=y, z=z, 
                                               origin=downwind_options['origin'], 
                                               distance=downwind_options['distance'], 
                                               kind=downwind_options['kind'], 
                                               plotter_options=plotter_options)
                else:
                    self.plotter = pw.PlotterDwprof(array, tstamps, projection=projection, extent=extent, 
                                               x=x, y=y, z=z, 
                                               origin=downwind_options['origin'], 
                                               distance=downwind_options['distance'], 
                                               kind=downwind_options['kind'], 
                                               plotter_options=plotter_options)

            else:
                idx = plotter_options.pop('idx', None)
                jdx = plotter_options.pop('jdx', None)
                if idx is None and jdx is None:
                    # 3d isosurface plot
                    zlim = plotter_options.pop('zlim', None)
                    self.plotter = pt.PlotterTrisurf(array,
                                               tstamps, projection=projection, extent=extent,
                                               x=x, y=y, z=z, zlim=zlim,
                                               plotter_options=plotter_options)
                else:
                    # vertical profile
                    self.plotter = pv.PlotterVprof(array,
                                               tstamps, projection=projection, extent=extent,
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
