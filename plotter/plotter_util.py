import warnings
try:
    import cartopy.crs as ccrs
    has_cartopy = True
except ImportError:
    warnings.warn('no cartopy', ImportWarning)
    has_cartopy = False
try:
    import rasterio
    has_rasterio = False
except ImportError:
    warnings.warn('no rasterio', ImportWarning)
    has_rasterio = True


import numpy as np
from multiprocessing import Pool
import shlex
import subprocess
import socket
import tempfile
from pathlib import Path
import os

class PlotterWarning(UserWarning): pass


# TCEQ's Lambert Conformal projection, define in caropy way
def LambertConformalTCEQ():
    return ccrs.LambertConformal(central_longitude=-97, central_latitude=40,
                                 standard_parallels=(33, 45), globe=ccrs.Globe(semimajor_axis=6370000,
                                                                               semiminor_axis=6370000))
# HRRR's Lambert Conformal projection, define in caropy way
def LambertConformalHRRR():
    return ccrs.LambertConformal(central_longitude=-97.5, central_latitude=38.5,
                                 standard_parallels=(38.5, 38.5), globe=ccrs.Globe(semimajor_axis=6370000,
                                                                               semiminor_axis=6370000))


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

def savemp4(p, wdir=None, nthreads=None, odir='.', oname='animation.mp4'):
    '''save mp4
    :param plotter:
    '''

    # TODO allow passing wdir, in case user wants to hold onto them

    if wdir is None:
        is_tempdir = True
        tempdir = tempfile.TemporaryDirectory()
        wdir = Path(tempdir.name)
    else:
        is_tempdir = False

        if isinstance(wdir , str):
            wdir = Path(wdir)
        if wdir.exists():
            for x in wdir.glob('*.png'): x.unlink()
        else:
            wdir.mkdir(exist_ok=False)

    # parallel processing
    # save all frames in parallel
    # 68 for stampede, 24 for ls5

    hn = socket.getfqdn()
    if nthreads is None:
        #nthreads = 24  # ls5, stampede2 skx node
        if 'frontera' in hn:
            nthreads = 56  # frontera
        elif 'ls5' in hn:
            nthreads = 24
        elif 'stampede2' in hn:
            nthreads = 24
        else:
            nthreads = 1

    # except that you are on TACC login node
    if hn.startswith('login') and '.tacc.' in hn:
        nthreads = 1

    nframes = len(p.tstamps)

    # '{:04d}.png' for python
    # '%04d.png' for shell
    png_fmt_py = '{:0' + str(int(np.log10(nframes) + 1)) + 'd}.png'
    png_fmt_sh = '%0' + str(int(np.log10(nframes) + 1)) + 'd.png'

    # object that does the p.savefig()
    saveone = _saveone(p, os.path.join(wdir, png_fmt_py))




    if nthreads > 1:
        with Pool(nthreads) as pool:
            pool.map(saveone, range(nframes))
        opt_threads = f'-threads {min(16, nthreads)}'  # ffmpeg says that dont use more than 16 threads
    else:
        # serial processing
        for i in range(nframes):
            saveone(i)
        opt_threads = ''


    # make mpeg file
    cmd = f'ffmpeg -i "{Path(wdir) / png_fmt_sh }" -vframes {nframes} -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y {opt_threads} "{Path(odir) / oname}"'
    subprocess.run(shlex.split(cmd), check=True)

    if is_tempdir:
        tempdir.cleanup()

class _saveone:
    # save one image from plotter
    # made into class in global level in order to use from mutiprocessing
    # https://stackoverflow.com/questions/62186218/python-multiprocessing-attributeerror-cant-pickle-local-object
    def __init__(self, p, png_fmt):
        # do i have to make p globa variable...?
        self.p = p
        self.png_fmt = png_fmt
    def __call__(self, i):
        self.p.savefig(self.png_fmt.format(i), tidx=i)

