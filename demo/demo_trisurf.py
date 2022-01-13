import sys
sys.path.insert(0, './repo/plotter')

from plotter import calpost_reader as cpr
import plotter.plotter_solo as plotter_solo
from plotter.plotter_util import LambertConformalHRRR
from plotter.plotter_background import BackgroundManager

import matplotlib.colors as colors
import pandas as pd
from io import StringIO
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature

import numpy as np

projHRRR = LambertConformalHRRR()


zlvl = np.array(
        [
            float(_) for _ in  
            '2 5 10 20 30 40 60 80 100 120 180 250 500'.split()]
        )

#if 'dat' in locals():
if True:

    #dat = cpr.calpost_reader('../calpost_3d/tseries/tseries_ch4_1min_conc_pilot_min_emis_3_xto_recp_1_13lvl_fmt_1_dsp_3_tur_3_byweek_20190224_20190303.dat', z=zlvl)
    dat = cpr.calpost_reader('../calpost_3d/tseries/tseries_ch4_1min_conc_pilot_min_emis_3_xto_recp_1_13lvl_fmt_1_dsp_3_tur_3_prf_1_byday_20190224.dat' , z=zlvl)

# grab necessary info
# [60:] to drop first 60min of data (spin-up)
arr = dat['v'][60:]
tstamps = dat['ts'][60:]
grid = dat['grid']


# get horizontal extent 
extent = [
    grid['x0'], grid['x0'] + grid['nx'] * grid['dx'],
    grid['y0'], grid['y0'] + grid['ny'] * grid['dy'],
]

# distance in calpost is in km
extent = [_ * 1000 for _ in extent]
x = dat['x'] * 1000
y = dat['y'] * 1000

z = dat['z']


arr = arr[:, 0:9, ...]
zlvl = zlvl[:9]
z = zlvl[:9]

# convert unit of array from g/m3 tp ppb
# mwt g/mol
# molar volume m3/mol
arr = arr / 16.043 * 0.024465403697038 * 1e9

# array has nan, so mask them
arr = np.ma.masked_invalid(arr)



### create 2d plot to steal stuff


title = 'test'

# Mrinali/Gary's surfer color scale
cmap = colors.ListedColormap([
    '#D6FAFE', '#02FEFF', '#C4FFC4', '#01FE02',
    '#FFEE02', '#FAB979', '#EF6601', '#FC0100', ])
cmap.set_under('#FFFFFF')
cmap.set_over('#000000')
# Define a normalization from values -> colors
bndry = [1, 10, 50, 100, 200, 500, 1000, 2000]
norm = colors.BoundaryNorm(bndry, len(bndry))


# receptor box defined by Shanon
df_corners = pd.read_csv(StringIO(
'''
box,lon,lat
receptor,-102.14119642699995,31.902587319000077
receptor,-102.06890715999998,31.928683642000067
receptor,-102.03957186099996,31.873156213000073
receptor,-102.11577420099997,31.85033867900006
receptor,-102.14119642699995,31.902587319000077
emitter,-102.1346819997111,31.80019199958484
emitter,-102.0045175208385,31.83711037948465
emitter,-102.046423081171,31.94509160994673
emitter,-102.1790300003915,31.90254999960113
emitter,-102.1346819997111,31.80019199958484
'''.strip()))
receptor_corners = df_corners.loc[df_corners['box'] == 'receptor', ['lon','lat']].values

shp_soft = shpreader.Reader('data/SoftLaunch_alt.shp')

plotter_options = {
    'background_manager': BackgroundManager(
        add_image_options=[cimgt.GoogleTiles(style='satellite'), 13],
        ),
    'title': title,
    'contour_options': {
        'levels': bndry,
        'cmap': cmap,
        'norm': norm,
        'alpha': .5,
        'extend': 'max',
    },
    'colorbar_options': {
        'label': r'$CH_4$ (ppbV)',
    },
    'customize_once': [
#        # add recetptor box
#        lambda p: p.ax.add_geometries(
#            [Polygon([_ for _ in receptor_corners])],  # four corners into polygon
#            crs = ccrs.PlateCarree(),  # projection is unprojected ("PlateCarre")
#            facecolor='none', edgecolor='black', lw=.6,  # plot styles
#            ),
        # add softlaunch box
        # ridiculously complicated...
        lambda p: p.ax.add_feature(
            ShapelyFeature(
                shp_soft.geometries(),
                crs=ccrs.PlateCarree(),
            facecolor='none', 
            #edgecolor='black', 
            edgecolor='#BDEDFC',
            lw=.6,  # plot styles
            )),

    ]}

# make a plot template
p = plotter_solo.Plotter(array=arr, tstamps=tstamps, 
                         x=x, y=y, z=z, projection=LambertConformalHRRR(),
                         plotter_options=plotter_options)

# want to load the extra stuff, incl background
# dont know why ipdate dowsnt work....

p.savefig('wish_me_luck.png', tidx=60)
p.savemp4('wish_me_luck.mp4',wdir='./wdir2',nthreads=24)
