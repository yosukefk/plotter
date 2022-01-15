# this cf was tedious to work with, so i wrote capost_ncf2, which uses plan netCDF4 package.
# it is still not following CF convention, seems like, it doesnt read by IDV correctly
import cf
import numpy as np

from plotter import calpost_reader as reader


def save(v, fname, compress=5, **kwds):
    """save to file

    :param cf.Field v: cf.Field to save
    :param str fname: filename
    :param int compress: 0-9
    """

    cf.write(v, fname, compress=compress, **kwds)

def create(dat):
    """creates cf-python Field object

    :param dict dat: calpost_reader generated dict of data

    :return: cf.Field
    """

    v = cf.Field(
        properties={
            'standard_name': 'mass_concentration_of_methane_in_air',
            'units': 'kg m-3',
        })

    v.set_data(dat['v'] / 1000)
    v.nc_set_variable('methane')

    if len(dat['v'].shape) == 4:
        nt, nz, ny, nx = dat['v'].shape
        has_z = True
        print(nt, nz, ny, nx)
    else:
        nt, ny, nx = dat['v'].shape
        has_z = False

    print('a')

    domain_axisT = cf.DomainAxis(nt)
    domain_axisT.nc_set_unlimited(True)
    domain_axisY = cf.DomainAxis(ny)
    domain_axisX = cf.DomainAxis(nx)


    domain_axisT.nc_set_dimension('time')
    domain_axisY.nc_set_dimension('y')
    domain_axisX.nc_set_dimension('x')

    axisT = v.set_construct(domain_axisT)
    axisY = v.set_construct(domain_axisY)
    axisX = v.set_construct(domain_axisX)

    if has_z:
        domain_axisZ = cf.DomainAxis(nz)
        domain_axisZ.nc_set_dimension('z')
        axisZ = v.set_construct(domain_axisZ)
    print(type(domain_axisY))
    print(dir(domain_axisY))
    print(domain_axisY.identity())

    print('b')

    x = dat['x']
    y = dat['y']

    dimX = cf.DimensionCoordinate(data=x * 1000,
                                  properties={
                                      'standard_name': 'projection_x_coordinate',
                                      'units': 'meters'})
    dimY = cf.DimensionCoordinate(data=y * 1000,
                                  properties={
                                      'standard_name': 'projection_y_coordinate',
                                      'units': 'meters'
                                  })
    dimT = cf.DimensionCoordinate(data=dat['ts'],
)

    dimT.nc_set_variable('time')
    dimY.nc_set_variable('y')
    dimX.nc_set_variable('x')

    if has_z:
        z = dat['z']
        dimZ = cf.DimensionCoordinate(data=z,
                                  properties={
                                      'standard_name': 'height',
                                      'units': 'meters'
                                  })
        dimZ.nc_set_variable('z')
    print('c')

    dim_t = v.set_construct(dimT, axes=domain_axisT.identity())
    dim_y = v.set_construct(dimY, axes=domain_axisY.identity())
    dim_x = v.set_construct(dimX, axes=domain_axisX.identity())
    if has_z:
        v.set_construct(dimZ, axes=domain_axisZ.identity())

    print('d')

    if has_z:
        v.set_data_axes([axisT, axisZ, axisY, axisX])
    else:
        v.set_data_axes([axisT, axisY, axisX])


    datum = cf.Datum(parameters={'earth_radius': 637000.0})

    coordinate_conversion_h = cf.CoordinateConversion(
        parameters={'grid_mapping_name': 'lambert_conformal_conic',
        'standard_parallel': (38.5, 38.5),
        'longitude_of_central_meridian': -97.5,
        'latitude_of_projection_origin': 38.5,
        })


    horizontal_crs = cf.CoordinateReference(
        datum=datum,
        coordinate_conversion=coordinate_conversion_h,
        coordinates=[dim_x, dim_y])

    v.set_construct(horizontal_crs)

    

    return v

def tester():

    dat = reader.tester()

    o = create(dat)
    save(o, 'test.nc')


