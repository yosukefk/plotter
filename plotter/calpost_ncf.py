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
    else:
        nt, ny, nx = dat['v'].shape
        has_z = False

    print('a')

    domain_axisT = cf.DomainAxis(nt)
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
    dimT = cf.DimensionCoordinate(data=dat['ts'])

    dimT.nc_set_variable('time')
    dimY.nc_set_variable('y')
    dimX.nc_set_variable('x')

    if has_z:
        z = dat['z']
        dimZ = cf.DimensionCoordinate(data=z,
                                  properties={
                                      'standard_name': 'projection_z_coordinate',
                                      'units': 'meters'
                                  })
        dimZ.nc_set_variable('z')
    print('c')

    v.set_construct(dimT)
    v.set_construct(dimY)
    v.set_construct(dimX)
    if has_z:
        v.set_construct(dimZ)

    print('d')

    return v

def tester():

    dat = reader.tester()

    o = create(dat)
    save(o, 'test.nc')


