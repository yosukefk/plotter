"""facilitates passing pseudoNetCDF data"""


try:
    import cartopy.crs as ccrs
    has_cartopy = True
except ImportError:
    warnings.warn('no cartopy', ImportWarning)
    has_cartopy = False
try:
    import PseudoNetCDF as pnc
except ImportError:
    warnings.warn('no PseudoNetCDF', ImportWarning)
    has_pnc = False

import numpy as np
import pytz
import datetime
from pathlib import Path



def iotf2dt(iotf,itzon=0):
    if itzon in (5,6,7,8):
        tz = pytz.timezone(f'Etc/GMT+{itzon}')
    elif itzon == 0:
        tz = pytz.utc
    else:
        raise ValueError(f'itzon: {itzon}')

    dt =  datetime.datetime(int(iotf[0] / 1000), 1, 1,tzinfo=tz)
    dt += datetime.timedelta(days=int(iotf[0] % 1000) - 1)
    dt += datetime.timedelta(seconds = 
            int(iotf[1] / 10000) * 3600 + 
            int(iotf[1] / 100) % 100 * 60 + 
            int(iotf[1]) % 100 )
    return dt

def Reader(f, vname=None, tslice=slice(None, None)):

    if isinstance(f, str) or isinstance(f, Path):
        print(f'opening: {f}')
        f = pnc.pncopen(f)

    if vname is None:
        for vn in iter(f.variables.keys()):
            if vn in ('O3', 'MDA8O3', 'MDA1O3', 'PM25', 'A24PM25'):
                vname = vn
                break


    o = {}
    o['name'] = vname
    v= f.variables[vname]

    v = v.squeeze()
    v = v[..., -1::-1, :]
    #v = np.flipud(v.squeeze())

    # time stamps
    o['tstamps'] = [iotf2dt(_) for _ in f.variables['TFLAG'][:, 0, :]]

    # projection
    if f.GDTYP != 2:
        raise NotImplementedError('only LCC (gtype==1) supported')
    # assume 6370 km sphere (EMEP)
    proj = ccrs.LambertConformal(
            central_longitude= f.XCENT, central_latitude=f.YCENT,
            standard_parallels=(f.P_ALP, f.P_BET),
            globe=ccrs.Globe(semimajor_axis=6370000,
                semiminor_axis=6370000))

    # extent
    ext = [f.XORIG, f.XORIG + f.NCOLS * f.XCELL,
            f.YORIG, f.YORIG + f.NROWS * f.YCELL, ]


    o['projection'] = proj
    o['extent'] = ext
    o['v'] = np.ma.masked_invalid(v)
    return o


