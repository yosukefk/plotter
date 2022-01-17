import warnings
try:
    import cartopy.crs as ccrs
    has_cartopy = True
except ImportError:
    warnings.warn('no cartopy', ImportWarning)
    ccrs = None
    has_cartopy = False
try:
    import rasterio
    has_rasterio = False
except ImportError:
    warnings.warn('no rasterio', ImportWarning)
    rasterio = None
    has_rasterio = True


import matplotlib as mpl
import numpy as np
from multiprocessing import Pool
import shlex
import subprocess
import socket
import tempfile
from pathlib import Path
import os

from plotter.plotter_multi import Plotter as PlotterMulti


class PlotterWarning(UserWarning):
    pass


def LambertConformalTCEQ():
    """
    TCEQ's Lambert Conformal projection, define in caropy way

    :rtype: ccrs.CRS
    :return: CRS
    """
    return ccrs.LambertConformal(central_longitude=-97, central_latitude=40,
                                 standard_parallels=(33, 45), globe=ccrs.Globe(semimajor_axis=6370000,
                                                                               semiminor_axis=6370000))


def LambertConformalHRRR():
    """
    HRRR's Lambert Conformal projection, define in caropy way

    :rtype: ccrs.CRS
    :return: CRS
    """
    return ccrs.LambertConformal(central_longitude=-97.5, central_latitude=38.5,
                                 standard_parallels=(38.5, 38.5),
                                 globe=ccrs.Globe(semimajor_axis=6370000, semiminor_axis=6370000))


# Deprecated
class background_adder:
    # https://ocefpaf.github.io/python4oceanographers/blog/2015/03/02/geotiff/
    def __init__(self, fname, alpha=.2):
        if not has_rasterio:
            raise RuntimeError('no raster io')
        warnings.warn('use background_manager instead!', DeprecationWarning)
        ds = rasterio.open(str(fname))
        self.data = ds.read()[:3, :, :].transpose((1, 2, 0))
        self.extent = [ds.transform[2], ds.transform[2] + ds.transform[0] * ds.width,
                       ds.transform[5] + ds.transform[4] * ds.height, ds.transform[5]]
        self.alpha = alpha

    def set_background(self, p):
        p.background_bga = p.ax.imshow(self.data, extent=self.extent, origin='upper',
                                       alpha=self.alpha)

    def refresh_background(self, p):
        p.background_bga.set_zorder(1)


# create animation mp4 file
def savemp4(p, wdir=None, nthreads=None, odir='.', oname='animation.mp4'):
    """save mp4

    :param plotter_solo.Plotter or plotter_multi.Plotter p: use savefig() to make MP4
    :param str wdir: dir to save intermediate PNG files
    :param int nthreads: number of threads to use on parallel machine
    :param odir: dir to save output file
    :param str oname: output MP4 file name

    """

    if wdir is None:
        is_tempdir = True
        tempdir = tempfile.TemporaryDirectory()
        wdir = Path(tempdir.name)
    else:
        is_tempdir = False

        if isinstance(wdir, str):
            wdir = Path(wdir)
        if wdir.exists():
            for x in wdir.glob('*.png'):
                x.unlink()
        else:
            wdir.mkdir(exist_ok=False)

    # parallel processing
    # save all frames in parallel
    # 68 for stampede, 24 for ls5

    hn = socket.getfqdn()
    if nthreads is None:
        if 'frontera' in hn:
            nthreads = 56
        elif 'ls5' in hn:
            nthreads = 24
        elif 'stampede2' in hn:
            nthreads = 24
        elif 'ls6' in hn:
            nthreads = 64
        else:
            warnings.warn('unknon hostname: %s' % hn)
            nthreads = 1

    # except that you are on TACC login node
    if hn.startswith('login') and '.tacc.' in hn:
        nthreads = 1

    nframes = len(p.tstamps)

    # '{:04d}.png' for python
    # '%04d.png' for shell
    png_fmt_py = '{:0' + str(int(np.log10(nframes) + 1)) + 'd}.png'
    png_fmt_sh = '%0' + str(int(np.log10(nframes) + 1)) + 'd.png'

    is_multi = isinstance(p, PlotterMulti)

    if is_multi:
        # set width to be linked to matplotlib...
        # default is 6.4x4.8 inch image, dpi=100
        # so 640x480 pixel
        # somehow i got the idea that i want to raise dpi=300
        # whic make 1920x1440.  i think this 1920 default width comes from
        # this value
        # so, instead of hard wire 1920 here, i equate this to number of
        # pixel in the image
        png_w = mpl.pyplot.rcParams['figure.figsize'][0] * mpl.pyplot.rcParams['figure.dpi']
        adjust_width = f'-vf scale={png_w}:-2'
    else:
        adjust_width = ''

    # object that does the p.savefig()
    saveone = _saveone(p, os.path.join(wdir, png_fmt_py), is_multi)

    if nthreads > 1:
        while True:
            try:
                with Pool(nthreads) as pool:
                    pool.map(saveone, range(nframes))
                break
            except (OSError, MemoryError):
                nthreads_new = int(nthreads / 2)
                print('dropping nthreads from {} to {}'.format(nthreads, nthreads_new))
                nthreads = nthreads_new
                if nthreads < 2: 
                    raise 
        opt_threads = f'-threads {min(16, nthreads)}'  # ffmpeg says that dont use more than 16 threads
    else:
        # serial processing
        for i in range(nframes):
            saveone(i)
        opt_threads = ''

    # make mp4 file
    cmd = f'ffmpeg -i "{Path(wdir) / png_fmt_sh }" {adjust_width} -vframes {nframes} -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y {opt_threads} "{Path(odir) / oname}"'
    subprocess.run(shlex.split(cmd), check=True)

    if is_tempdir:
        tempdir.cleanup()


class _saveone:
    """save one image from plotter, so that multiprocessing.Pool can be used"""

    # made into class in global level in order to use from mutiprocessing
    # https://stackoverflow.com/questions/62186218/python-multiprocessing-attributeerror-cant-pickle-local-object
    def __init__(self, p, png_fmt, is_multi):
        self.p = p
        self.is_multi = is_multi
        # rasterio cannot be pickled, so drop it
        # also, tricontouf has TriContourGenerator that cannot be pickled,
        # and we dont need them anyway, i think
        if is_multi:
            for plotter in self.p.plotters:
                if hasattr(plotter, 'background_manager'):
                    plotter.background_manager.purge_bgfile_hook()
                if hasattr(plotter, 'cnt'):
                    if hasattr(plotter.cnt, 'cppContourGenerator'):
                        del plotter.cnt.cppContourGenerator
        else:
            if hasattr(self.p.plotter, 'background_manager'):
                self.p.plotter.background_manager.purge_bgfile_hook()
            if hasattr(self.p.plotter, 'cnt'):
                if hasattr(self.p.plotter.cnt, 'cppContourGenerator'):
                    del self.p.plotter.cnt.cppContourGenerator

        self.png_fmt = png_fmt

    def __call__(self, i):
        self.p.savefig(self.png_fmt.format(i), tidx=i)


def calc_plot_extent( x=None, y=None, extent=None, data_proj=None,
                     plot_proj=None):
    """calculate plot_extent"""


    if data_proj is None or not isinstance(data_proj, ccrs.Projection):
        raise ValueError(
            f'data_proj has to be carotpy Projection: {repr(data_proj)}')

    if plot_proj is None or not isinstance(plot_proj, ccrs.Projection):
        raise ValueError(
            f'plot_proj has to be carotpy Projection: {repr(plot_proj)}')



    if extent is None:

        # corner coords of data grid
        #data_corners = np.array( [(x[p], y[q]) for (p,q) in
        #                [(0,0),(0,-1),(-1,-1),(-1,0),(0,0)]] )
        #data_corners = np.array( [(x[p], y[q]) for (p,q) in
        #                [(0,0),(0,-1),(-1,-1),(-1,0),(0,0)]] )
        # be robust!
        xrng = [x.min(), x.max()]
        yrng = [y.min(), y.max()]
    else:
        xrng = extent[0:2]
        yrng = extent[2:4]

    data_corners = np.array( [(xrng[p], yrng[q]) for (p,q) in
                    [(0,0),(0,-1),(-1,-1),(-1,0),(0,0)]] )


    print('data_corners:', data_corners)


    # reproject the corners into plot's projection
    plot_corners = plot_proj.transform_points(data_proj, 
                                   data_corners[:, 0], 
                                   data_corners[:, 1],
                                   )[:, :2] 
    print('plot_corners:', plot_corners)


    # add buffer and take floor/ceil
    decfloor = lambda a, decimals: np.floor(a * (10 ** decimals)) / (10**decimals)
    decceil = lambda a, decimals: np.ceil(a * (10 ** decimals)) / (10**decimals)

    #nx, ny = len(x), len(y)
    #bufx = (plot_corners[2][0] - plot_corners[0][0]) / len(x) 
    #bufy = (plot_corners[2][1] - plot_corners[0][1]) / len(y) 
    bufx = (plot_corners[2][0] - plot_corners[0][0]) / 100
    bufy = (plot_corners[2][1] - plot_corners[0][1]) / 100

    #print(nx, ny, bufx, bufy)

    buf = min(bufx, bufy)
    scl =  - int(np.round(np.log10(buf), 0))
    print('buf, scl:', buf, scl)

    plot_extent = [
        decfloor(plot_corners[0][0] - bufx, scl),
        decceil(plot_corners[2][0] + bufx, scl),
        decfloor( plot_corners[0][1] - bufy, scl),
        decceil( plot_corners[2][1] + bufy, scl),
    ]
    print('plot_extent:', plot_extent)

    return plot_extent

