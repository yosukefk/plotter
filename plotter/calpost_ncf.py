# this still doens read by IDV correctly, something wrong following CF convention
# https://gist.github.com/julienchastang/2129368a26ce0d85cff13cf0bc05cbf4
import netCDF4
import pyproj
import numpy as np

import plotter.calpost_reader as cpr

def create(dat, fname, grid_mapping=False):
    """creates cf-python Field object

    :param dict dat: calpost_reader generated dict of data

    :return: cf.Field
    """
    ds = netCDF4.Dataset(fname, mode='w')

    if len(dat['v'].shape) == 4:
        nt, nz, ny, nx = dat['v'].shape
        has_z = True
        print(nt, nz, ny, nx)
    else:
        nt, ny, nx = dat['v'].shape
        has_z = False

    dim_t = ds.createDimension('time', nt)
    if has_z:
        dim_z = ds.createDimension('z', nz)
    dim_y = ds.createDimension('y', ny)
    dim_x = ds.createDimension('x', nx)

    time = ds.createVariable('time', np.float64, ('time',))
    time.standard_name = 'time'
    time.units = 'days since ' + dat['ts'][0].date().strftime('%Y-%m-%d 00:00:00    ')
    time.long_name = 'time'
    time.calendar = 'gregorian'
    ts = dat['ts']
    time[:] = [_.days + _.seconds / 86400 for _ in (ts - ts[0])]

    if has_z:
        z = ds.createVariable('z', np.float32, ('z',))
        z.standard_name = 'height'
        z.units = 'meters'
        z.long_name = 'height'
        z[:] = dat['z']

    y = ds.createVariable('y', np.float64, ('y',))
    y.standard_name = 'projection_y_coordinate'
    y.units = 'meters'
    y.long_name = 'projection_y_coordinate'
    y[:] = dat['y'] * 1000

    x = ds.createVariable('x', np.float64, ('x',))
    x.standard_name = 'projection_x_coordinate'
    x.units = 'meters'
    x.long_name = 'projection_x_coordinate'
    x[:] = dat['x'] * 1000

    ys, xs = np.meshgrid(dat['y'], dat['x'])
    p = pyproj.Proj('+proj=lcc +lon_0=-97.5 +lat_0=38.5 +lat_1=38.5 +lat_2=38.5 +R=6370000')
    lats, lons = p(ys, xs, inverse=True)

    latitude = ds.createVariable('latitude', np.float64, ('y', 'x'))
    latitude.standard_name = 'latitude'
    latitude.units = 'degrees_north'
    latitude.long_name = 'latitude'
    latitude.coordinates = "latitude longitude"
    latitude[:] = lats

    longitude = ds.createVariable('longitude', np.float64, ('y', 'x'))
    longitude.standard_name = 'longitude'
    longitude.units = 'degrees_east'
    longitude.long_name = 'longitude'
    longitude.coordinates = "latitude longitude"
    longitude[:] = lons

    #lambert_conformal_conic = ds.createVariable('lambert_conformal_conic', np.byte, ())
    lambert_conformal_conic = ds.createVariable('lambert_conformal_conic', np.int32, ())
    lambert_conformal_conic.earth_radius = 637000.
    lambert_conformal_conic.grid_mapping_name = "lambert_conformal_conic"
    lambert_conformal_conic.standard_parallel = (38.5, 38.5 )
    lambert_conformal_conic.longitude_of_central_meridian = -97.5
    lambert_conformal_conic.latitude_of_projection_origin = 38.5

#    longitude = ds.createVariable(


    if has_z:
        data_dim = ('time', 'z', 'y', 'x')
    else:
        data_dim = ('time', 'y', 'x')
    methane = ds.createVariable('methane', np.float32, data_dim, zlib=True, complevel=5)
    methane.standard_name = 'mass_concentration_of_methane_in_air'
    methane.units = 'kg m-3'
    methane.long_name = 'mass_concentration_of_methane_in_air'
    if grid_mapping:
        # cf compilent, 
        # https://cfconventions.org/cf-conventions/cf-conventions.html#grid-mappings-and-projections
        #but
        # i still dont get idv to understand this, and
        # paraveiw maybe taking degree for horizontal, meters for vertical, lookig very weirdo
        # for until i find correct way i stick with above
        #methane.coordinates = "time z latitude longitude"
        methane.coordinates = "latitude longitude"
        methane.grid_mapping = "lambert_conformal_conic"
    else:
        # primitive
        # time axis is still CF compient.  But giving up geolocation
        # for paraview probably this is all we need
        methane.coordinates = "time z y x"
    methane[...] = dat['v']
    

    ds.Conventions = 'CF-1.6'


def tester():
    dat = cpr.calpost_reader('tseries/tseries_ch4_1min_conc_pilot_min_emis_f0003_recep_25_xto_f0003_14lvl_fmt_1_dsp_3_tur_3_prf_1_byday_20190224.dat', 
    z = 

'2 5 10 20 30 40 50 65 80 100 120 180 250 500'.split()
)
    create(dat, 'xxx.nc')
if __name__ == '__main__':
    tester()
