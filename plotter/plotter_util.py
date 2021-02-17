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


from multiprocessing import Pool
import shlex
import subprocess
import socket
import tempfile
from pathlib import Path

class PlotterWarning(UserWarning): pass


# TCEQ's Lambert Conformal projection, define in caropy way
def LambertConformalTCEQ():
    return ccrs.LambertConformal(central_longitude=-97, central_latitude=40,
                                 standard_parallels=(33, 45), globe=ccrs.Globe(semimajor_axis=6370000,
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

def savemp4(p, saveone=None, nthreads=None, odir='.', oname='animation.mp4'):
    '''save mp4
    :param plotter:
    '''

    with tempfile.TemporaryDirectory() as wdir:

        # you decide if you want to use many cores
        # parallel processing
        # save all frames in parallel
        # 68 for stampede, 24 for ls5
        if nthreads is None:
            nthreads = 24  # ls5

        if saveone is None:
            #saveone = lambda i: p.save(Path(wdir) / f'{i:04}.png', tidx=i)
            def saveone(i):
                p.save(Path(wdir) / f'{i:04}.png', tidx=i)

        # except that you are on TACC login node
        hn = socket.getfqdn()
        if hn.startswith('login') and '.tacc.' in hn:
            nthreads = 1

        if nthreads > 1:
            with Pool(nthreads) as pool:
                pool.map(saveone, range(len(p.tstamps)))
        else:
            # serial processing
            for i in range(len(p.tstamps)):
                saveone(i)





        # make mpeg file
        cmd = f'ffmpeg -i "{Path(wdir) / "%04d.png"}" -vframes 2880 -crf 3 -vcodec libx264 -pix_fmt yuv420p -f mp4 -y "{Path(odir) / oname}"'
        subprocess.run(shlex.split(cmd), check=True)


