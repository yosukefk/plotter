import cf
import numpy as np

import calpost_reader as reader
dat = reader.tester()

v = cf.Field(
        properties={
            'standard_name': 'mass_concentration_of_methane_in_air', 
            'units': 'kg m-3',
            })

v.set_data(dat['v'] / 1000)
v.nc_set_variable('methane')

nt,ny,nx = dat['v'].shape

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

print('b')

x = dat['x'][:nx]
y = dat['y'][np.arange(ny)*nx]

dimX= cf.DimensionCoordinate(data=x*1000, 
        properties = {
            'standard_name': 'projection_x_coordinate',
            'units': 'meters'})
dimY= cf.DimensionCoordinate(data=y*1000,
        properties = {
            'standard_name': 'projection_y_coordinate',
            'units': 'meters'
            })
dimT= cf.DimensionCoordinate(data=dat['ts'])
dimT.nc_set_variable('time')
dimY.nc_set_variable('y')
dimX.nc_set_variable('x')
print('c')

v.set_construct(dimT)
v.set_construct(dimY)
v.set_construct(dimX)

print('d')


