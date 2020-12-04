try:
    import gdal
except ModuleNotFoundError:
    from osgeo import gdal
gdal.UseExceptions()


class background_adder:
    # https://ocefpaf.github.io/python4oceanographers/blog/2015/03/02/geotiff/
    def __init__(self, fname, alpha=.2):
        ds = gdal.Open(str(fname))
        data = ds.ReadAsArray()
        gt = ds.GetGeoTransform()

        self.extent = (gt[0], gt[0] + ds.RasterXSize * gt[1],
                       gt[3] + ds.RasterYSize * gt[5], gt[3])
        self.data = data[:3, :, :].transpose((1, 2, 0))
        self.alpha = alpha

    def set_background(self, p):
        p.background_bga = p.ax.imshow(self.data, extent=self.extent, origin='upper',
                                       alpha=self.alpha)

    def refresh_background(self, p):
        p.background_bga.set_zorder(1)
