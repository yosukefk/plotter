import reader
import gdal
import osr


dat = reader.tester()





arr = dat['v'][:,::-1,:]
#arr = dat['v']
g = dat['grid']
ext = (g['x0'], g['x0'] + g['dx']*g['nx'],
g['y0'], g['y0'] + g['dy']*g['ny'])

print(type(g['nx']))
print(type(g['ny']))


drv = gdal.GetDriverByName('GTiff')
ds = drv.Create('test.tif', xsize = int(g['nx']), ysize=int(g['ny']), bands=1,
        eType=gdal.GDT_Float32)
ds.SetGeoTransform([g['x0']*1000, g['dx']*1000, 0, (g['y0']+g['ny']*g['dy'])*1000, 0,
    -g['dy']*1000])
srs = osr.SpatialReference()
srs.ImportFromProj4('''+proj=lcc +lat_1=33 +lat_2=45 +lat_0=40 +lon_0=-97
+x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m +no_defs''')
ds.SetProjection(srs.ExportToWkt())

ds.GetRasterBand(1).WriteArray(arr[60*12])
del ds
