from . import plotter_util as pu
from . import plotter_footnote as pf
import warnings

from . import plotter_solo as psolo
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from skimage import measure

import numpy as np
import itertools
from cartopy.mpl.patch import geos_to_path

import matplotlib.collections as mcoll
import mpl_toolkits.mplot3d.art3d as art3d

import matplotlib as mpl

import tempfile

# Resolving issue of zorder, Took idea from here
# https://stackoverflow.com/questions/20781859/drawing-a-line-on-a-3d-plot-in-matplotlib
# also see add_fixzordercollection3d() below
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection

class FixZorderLine3DCollection(Line3DCollection):
    _zorder = 1000

    @property
    def zorder(self):
        return self._zorder

    @zorder.setter
    def zorder(self, value):
        pass

class FixZorderPoly3DCollection(Poly3DCollection):
    _zorder = 1000

    @property
    def zorder(self):
        return self._zorder

    @zorder.setter
    def zorder(self, value):
        pass


# this add_fixordercollection3d() is like variation for Axes3D.add_collection3d()
# this finally worked...
def add_fixzordercollection3d(ax, col, zs=0, zdir='z'):
    def poly_collection_2d_to_fixzorder3d(col, zs=0, zdir='z'):
        segments_3d, codes = art3d._paths_to_3d_segments_with_codes(
                col.get_paths(), zs, zdir)
        col.__class__ = FixZorderPoly3DCollection
        col.set_verts_and_codes(segments_3d, codes)
        col.set_3d_properties()
    def line_collection_2d_to_fixzorder3d(col, zs=0, zdir='z'):
        segments3d = art3d._paths_to_3d_segments(col.get_paths(), zs, zdir)
        col.__class__ = FixZorderLine3DCollection
        col.set_segments(segments3d)
    zvals = np.atleast_1d(zs)
    zsortval = (np.min(zvals) if zvals.size else 0)
    if type(col) is mcoll.PolyCollection:
        poly_collection_2d_to_fixzorder3d(col, zs, zdir=zdir)
        col.set_sort_zpos(zsortval)
    elif type(col) is mcoll.LineCollection:
        line_collection_2d_to_fixzorder3d(col, zs, zdir=zdir)
        col.set_sort_zpos(zsortval)
    collection = super(Axes3D, ax).add_collection(col)
    return collection

# https://stackoverflow.com/questions/48269014/contourf-in-3d-cartopy
def add_feature3d(ax, feature, clip_geom=None, zs=None):
    """
    Add the given feature to the given axes.
    """
    concat = lambda iterable: list(itertools.chain.from_iterable(iterable))

    target_projection = ax.projection

    if hasattr(feature, 'geometries'):
        # cartopy.feature.Feature
        feature_hook = feature
    elif hasattr(feature._feature, 'geometries'):
        # cartopy.feature_artist.FeatureArtist ? 
        feature_hook = feature._feature 
    else: 
        raise RuntimeError('problem with feature: %s' % type(feature))

    geoms = list(feature_hook.geometries())

    if target_projection != feature_hook.crs:
        # Transform the geometries from the feature's CRS into the
        # desired projection.
        geoms = [target_projection.project_geometry(geom, feature_hook.crs)
                 for geom in geoms]

    if clip_geom:
        # Clip the geometries based on the extent of the map (because mpl3d
        # can't do it for us)
        geoms = [geom.intersection(clip_geom) for geom in geoms]

    # Convert the geometries to paths so we can use them in matplotlib.
    paths = concat(geos_to_path(geom) for geom in geoms)

    # Bug: mpl3d can't handle edgecolor='face'
    kwargs = feature_hook.kwargs
    if kwargs.get('edgecolor') == 'face':
        kwargs['edgecolor'] = kwargs['facecolor']

    polys = concat(path.to_polygons(closed_only=False) for path in paths)

    if kwargs.get('facecolor', 'none') == 'none':
        lc = mcoll.LineCollection(polys, **kwargs)
    else:
        lc = mcoll.PolyCollection(polys, closed=False, **kwargs) 
    
    #ax.add_collection3d(lc, zs=zs)
    add_fixzordercollection3d(ax, lc, zs=zs)


def add_image(ax3d, im, zbase):
    # get image
    im0 = im.get_array() / 255

    xx, yy = np.meshgrid(
            np.linspace(ax3d.get_xlim()[0], ax3d.get_xlim()[1], num = im0.shape[1]),
            np.linspace(ax3d.get_ylim()[0], ax3d.get_ylim()[1], num = im0.shape[0]),
            )

    zz = np.ones_like(xx) * zbase

    # https://stackoverflow.com/questions/37478460/add-background-image-to-3d-plot
    srf = ax3d.plot_surface(xx, yy, zz, rstride=1, cstride=1, facecolors=im0)
    srf.__class__ = FixZorderPoly3DCollection
    srf._zorder = -1000


def add_trisurf(ax, arr, x, y, z, iso_val, **kwds):

    verts, faces, normals, values = measure.marching_cubes(arr, iso_val)
    verts_p = verts.copy()
    verts_p[:, 2] = np.interp(verts_p[:, 2], np.arange(len(x)), x)
    verts_p[:, 1] = np.interp(verts_p[:, 1], np.arange(len(y)), y)
    verts_p[:, 0] = np.interp(verts_p[:, 0], np.arange(len(z)), z)
    psurf = ax.plot_trisurf(verts_p[:, 2], verts_p[:,1], faces, verts_p[:, 0],
            **kwds)

    return psurf

def add_trisurfs(ax, arr, x, y, z, contour_options):
    surfs = []
    amax = arr.max()
    bdry = contour_options['levels']
    cmap = contour_options['cmap']
    for i in range(len(bdry)):
        b = bdry[-1-i]
        if i == 0:
            c = cmap.get_over()
        else:
            c = cmap.colors[len(bdry)-1-i]
        if i == 0:
            a = .5
        elif i == 1:
            a = .2
        elif i == 2:
            a = .1
        else:
            a = .05
        if amax > b:
            psurf = add_trisurf(ax, arr, x, y, z, b, color=c, alpha=a)
            surfs.append(psurf)
    return surfs
    


class PlotterTrisurf:
    def __init__(self, array, tstamps, z, zlim=None,
                 projection=None, extent=None, x=None, y=None, plotter_options=None):
        """
        Manages mpl.mpl_toolkits.mplot3.axes3d.Axes3D with a trisurf representation of plume

        :rtype: PlotterTrisurf
        :param np.ndarray array: 4-d array of data values, dimensions(t, z, y, x), or 2+ d array of data values, dimensions(t, ...)
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t)
        :param np.ndarry z: 1-d array of z, dimensions(z)
        :param ccrs.CRS projection: projection of xy coordinate of data
        :param list extent: xy extent of data, with with coordinate of projection
        :param np.ndarray x: x coordinate of data, with shape matching (...) part of array
        :param np.ndarray y: y coordinate of data, with shape matching (...) part of array
        :param dict plotter_options: all the arguments passed to plotter
        """ 

        if plotter_options is None:
            plotter_options = {}

        # i have to know the axes being used, even user wants default
        # so i grab default axes here and hold onto it
        self.fig = plotter_options.get('fig', plt.figure())
        pos = plotter_options.get('pos', None)

        self.arr = array
        self.tstamps = tstamps

        if 'imshow_option' in plotter_options:
            warnings.warn('imshow not supported', pu.PlotterWarning)
        self.contour_options = plotter_options.get('contour_options', {})

        self.colorbar_options = plotter_options.get('colorbar_options', {})

        self.footnote = plotter_options.get('footnote', "{tstamp}")  # default just time stamp
        footnote_options = {'xytext': (0, -18)}  # default, need to push lower
        footnote_options.update(
            plotter_options.get('footnote_options', {}))
        self.footnote_options = footnote_options
        self.footnote_manager = None

        self.title = plotter_options.get('title', None)
        self.title_options = plotter_options.get('title_options', None)

        # data's extent
        self.extent = extent
        self.x = x
        self.y = y
        if self.extent is None and not (self.x is None or self.y is None):
            self.extent = [self.x[0], self.x[-1], self.y[0], self.y[-1]]

        # vertical coordinates
        self.z = z

        # create plots 
        if pos:
            self.ax = self.fig.add_subplot(*pos, projection='3d')
        else:
            self.ax = self.fig.add_subplot(projection='3d')

        self.x1d = np.linspace(x.min(), x.max(), num=self.arr.shape[-1])
        self.y1d = np.linspace(y.min(), y.max(), num=self.arr.shape[-2])
        print(self.x1d)
        print(self.y1d)


        self.ax.set_xlim(self.x1d[0], self.x1d[-1])
        self.ax.set_ylim(self.y1d[0], self.y1d[-1])

        self.ax.set_xticks([])
        self.ax.set_yticks([])


        if zlim is None: 
            self.ax.set_zlim(0, z[-1])
        else:
            self.ax.set_zlim(*zlim)

        zbase = self.ax.get_zlim()[0]
        zbase1 = zbase + .1

        # create dummy contour plot
        p = psolo.Plotter(array[:,0,:,:], tstamps,
                 projection=projection, extent=extent, x=x, y=y, plotter_options=plotter_options)
        # want to load the extra stuff, incl background
        # dont know why ipdate dowsnt work....
        p.savefig(tempfile.TemporaryFile(suffix='.png'))
        #p.plotter.update()

        # image
        for im in p.ax.get_images():
            add_image(self.ax, im, zbase)

        # feature
        clip_geom = p.ax._get_extent_geom().buffer(0)
        self.ax.projection = p.ax.projection
        for a in p.ax.artists:
            add_feature3d(self.ax, a, clip_geom, zs=zbase1)

        # done with the dummy
        plt.close(p.plotter.fig)

        # self.title overrides 'label' in self.title_options
        if self.title is None:
            if self.title_options is None:
                pass
            else:
                self.title = self.title_options.get('label')
        else:
            if self.title_options is None:
                self.title_options = {'label': self.title}
            else:
                self.title_options['label'] = self.title

        if self.title is not None:
            ttlopt = {'loc': 'center'}
            ttlopt.update(self.title_options)
            self.ax.set_title(**ttlopt)

        self.hasdata = False
        self.srf = []
        self.mappable = None
        self.current_arr = None
        self.current_tstamp = None


    def update(self, tidx=None, footnote=None, title=None):
        if tidx is None: tidx = 0
        arr = self.arr[tidx]
        ts = self.tstamps[tidx]
        self.current_arr = arr
        self.current_tstamp = ts

        if self.hasdata:

            for s in self.srf: s.remove()
            self.srf = add_trisurfs(self.ax, arr, self.x1d, self.y1d, self.z, self.contour_options)

            if self.footnote_manager is not None:
                self.footnote_manager(footnote)
        else:

            self.srf = add_trisurfs(self.ax, arr, self.x1d, self.y1d, self.z, self.contour_options)
            #self.mappable = self.srf
            self.mappable = mpl.cm.ScalarMappable(norm=self.contour_options['norm'], cmap=self.contour_options['cmap'])

            if self.colorbar_options is not None:
                kwds = self.colorbar_options
                if not self.mappable is None:
                    self.cb = plt.colorbar(mappable=self.mappable, ax=self.ax,
                                           **kwds)
                else:
                    warnings.warn('No data to show, Colorbar turned off',
                                  pu.PlotterWarning)

            if self.footnote != '':
                self.footnote_manager = pf.FootnoteManager(self, self.footnote,
                                                        self.footnote_options)
            self.hasdata = True

        if title is not None:
            # update the title
            self.ax.set_title(title)
    def customize(self, fnc):
        """
        apply function to self.ax

        :param function, list fnc:
        """ 
        raise NotImplementedError('do i need this?')

