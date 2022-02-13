#!/usr/bin/env python
import sys
sys.path.insert(0, './repo/plotter')

from plotter import calpost_reader as cpr
import plotter.plotter_solo as plotter_solo
import plotter.plotter_multi as plotter_multi
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

import matplotlib as mpl

mpl.rcParams['savefig.dpi'] = 300

projHRRR = LambertConformalHRRR()


zlvl = np.array(
        [
#            float(_) for _ in  
            #'2 5 10 20 30 40 60 80 100 120 180 250 500'.split()
#            '2 5 10 20 30 40 50 65 80 100 120 180 250 500'.split()
2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 100, 120, 150,
            ]
        )

def proc(fname, oname, title=None, workdir=None):
    #if 'dat' in locals():
    if True:

        #dat = cpr.calpost_reader('../calpost_3d/tseries/tseries_ch4_1min_conc_pilot_min_emis_3_xto_recp_1_13lvl_fmt_1_dsp_3_tur_3_byweek_20190224_20190303.dat', z=zlvl)
        #dat = cpr.calpost_reader('../calpost_3d/tseries/tseries_ch4_1min_conc_pilot_min_emis_3_xto_recp_1_13lvl_fmt_1_dsp_3_tur_3_prf_1_byday_20190224.dat' , z=zlvl)
        dat = cpr.calpost_reader(fname, z=zlvl)

    # grab necessary info
    # [60:] to drop first 60min of data (spin-up)
    print(dat['v'].shape)
    if dat['v'].shape[0] > 200:
        maybe_hourly = False
        arr = dat['v'][60:]
        tstamps = dat['ts'][60:]
    else:
        maybe_hourly = True
        arr = dat['v']
        tstamps = dat['ts']
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


    arr = arr[:, 0:14, ...]
    #zlvl = zlvl[:14]
    z = zlvl[:14]

    # convert unit of array from g/m3 tp ppb
    # mwt g/mol
    # molar volume m3/mol
    arr = arr / 16.043 * 0.024465403697038 * 1e9

    # array has nan, so mask them
    arr = np.ma.masked_invalid(arr)


    title = title

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

    figure_options = {
    #    'suptitle': title,
        #'colorbar_options': {
        #    'label': r'$CH_4$ (ppbV)',
        #},
        'footnote_options': {'text': "{tstamp}", 'y':.01},
#        'tight_layout': True,
    }

    # make all the fonts smaller, since tight_layout doesnt work for irregular set of panels
#    mpl.rc('font', **{'size': mpl.rcParams['font.size']*.9})
    if title is not None:
        figure_options['suptitle'] = {'s': title, 'y': .98}
    plotter_options = {
    #    'background_manager': BackgroundManager(
    #        add_image_options=[cimgt.GoogleTiles(style='satellite'), 13],
    #        ),
    #    'title': title,
        'contour_options': {
            'levels': bndry,
            'cmap': cmap,
            'norm': norm,
            'alpha': .5,
            'extend': 'max',
        },
        'colorbar_options': None,
        'footnote': '',
        'customize_once': [
    #        # add recetptor box
    #        lambda p: p.ax.add_geometries(
    #            [Polygon([_ for _ in receptor_corners])],  # four corners into polygon
    #            crs = ccrs.PlateCarree(),  # projection is unprojected ("PlateCarre")
    #            facecolor='none', edgecolor='black', lw=.6,  # plot styles
    #            ),
            # add softlaunch box
            # ridiculously complicated...
    #        lambda p: p.ax.add_feature(
    #            ShapelyFeature(
    #                shp_soft.geometries(),
    #                crs=ccrs.PlateCarree(),
    #            facecolor='none', 
    #            #edgecolor='black', 
    #            edgecolor='#BDEDFC',
    #            lw=.6,  # plot styles
    #            )),

        ],
    }
    downwind_options = {
    'origin' : (-436491, -727712),
    'distance' : (50, 150, 300),
    'distance_for_direction' : 150, 
    #'half_angle': 30,
    'half_angle': 45,
    'half_arclen': 150,
    'kind' : 'cross',
    }


    figure_options.update({'nrow':2, 'ncol': 3})
    plotter_options_multi = [plotter_options.copy() for _ in range(5) ]
    plotter_options_multi[1]['downwind_options'] = (downwind_options | {'kind': 'planview'}) 
    plotter_options_multi[0]['downwind_options'] = (downwind_options | {'kind': 'along', })
    plotter_options_multi[2]['downwind_options'] = (downwind_options | {'kind': 'cross', 'distance':  50})
    plotter_options_multi[3]['downwind_options'] = (downwind_options | {'kind': 'cross', 'distance': 150})
    plotter_options_multi[4]['downwind_options'] = (downwind_options | {'kind': 'cross', 'distance': 300})

    plotter_options_multi[1].update(
    {
        'background_manager': BackgroundManager(
            #add_image_options=[cimgt.GoogleTiles(style='satellite'), 13],
            add_image_options=[cimgt.GoogleTiles(style='satellite'), 20],
            ),
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

        ],
    }
    )

    plotter_options_multi[0].update({
    'customize_once': [
            lambda q: q.ax.text(.05, .95, f'along wind',
                                ha='left', va='top',
                                transform=q.ax.transAxes),
            lambda q: q.ax.set_ylabel('height (m AGL)'), 
            lambda q: q.ax.set_xlabel('from source (m)'),#, fontsize='small'),
            lambda q: q.ax.xaxis.set_tick_params(labelsize='small'),
            lambda q: q.ax.axvline(x= 50, color='gray', alpha=.5, lw=.6),
            lambda q: q.ax.axvline(x=150, color='gray', alpha=.5, lw=.6),
            lambda q: q.ax.axvline(x=300, color='gray', alpha=.5, lw=.6),
    ],
    'pos': (2, 2, 1),

    })
    plotter_options_multi[1].update({
    'pos': (2, 2, 2),
    })


    plotter_options_multi[2].update({
    'customize_once': [
            lambda q: q.ax.text(.05, .95, f'cross wind @ 50m',
                                ha='left', va='top',
                                transform=q.ax.transAxes),
            lambda q: q.ax.set_ylabel('height (m AGL)'), 
            lambda q: q.ax.set_xlabel('from plume center (m)'),
#            lambda q: q.ax.set_xlim(left=-300, right=300), 
            lambda q: q.ax.set_xlim(left=-150, right=150), 
            lambda q: q.ax.xaxis.set_tick_params(labelsize='small'),
            lambda q: q.ax.axvline(x=0, color='gray', alpha=.5, lw=.6),

    ],
    'pos': (2, 3, 4),
    })

    plotter_options_multi[3].update({
    'customize_once': [
            lambda q: q.ax.text(.05, .95, f'cross wind @ 150m',
                                ha='left', va='top',
                                transform=q.ax.transAxes),
            lambda q: q.ax.set_ylabel('height (m AGL)'), 
            lambda q: q.ax.set_xlabel('from plume center (m)'),
#            lambda q: q.ax.set_xlim(left=-300, right=300), 
            lambda q: q.ax.set_xlim(left=-150, right=150), 
            lambda q: q.ax.xaxis.set_tick_params(labelsize='small'),
            lambda q: q.ax.axvline(x=0, color='gray', alpha=.5, lw=.6),

    ],
    'pos': (2, 3, 5),
    })

    plotter_options_multi[4].update({
    'customize_once': [
            lambda q: q.ax.text(.05, .95, f'cross wind @ 300m',
                                ha='left', va='top',
                                transform=q.ax.transAxes),
            lambda q: q.ax.set_ylabel('height (m AGL)'), 
            lambda q: q.ax.set_xlabel('from plume center (m)'),
#            lambda q: q.ax.set_xlim(left=-300, right=300), 
            lambda q: q.ax.set_xlim(left=-150, right=150), 
            lambda q: q.ax.xaxis.set_tick_params(labelsize='small'),
            lambda q: q.ax.axvline(x=0, color='gray', alpha=.5, lw=.6),
    ],
    'pos': (2, 3, 6),
    })

    # since tignt layout doesnt work i change each of texts' font here
    for po in plotter_options_multi:
        po['customize_once'].extend(
                [ 
                    lambda q: q.ax.xaxis.set_tick_params(labelsize='xx-small'),
                    lambda q: q.ax.yaxis.set_tick_params(labelsize='xx-small'),
                    lambda q: q.ax.set_xlabel(q.ax.get_xlabel(), fontsize='small', labelpad=1),
                    lambda q: q.ax.set_ylabel(q.ax.get_ylabel() if q.ax.get_subplotspec().get_rows_columns()[4]==0 else None, fontsize='small', labelpad=1),
                    ]
                )
            



    arrays = [arr]*5
#    arrays[1] = None

#    plotter_options_multi.insert(0, {'footnote':''})
#    arrays.insert(0, None)


    #print(plotter_options_multi)
    #for po in plotter_options_multi:
    #    print(po['downwind_options'])
    #raise

#    my_po = plotter_options.copy()
#    my_po['downwind_options'] = {
#    'origin' : (-436491, -727712),
##    'distance' : (50, 150, 300),
#    'distance_for_direction' : 150, 
#    'distance' : 50,
##    'half_angle': 30,
#    'half_arclen': 150,
##    'kind' : 'planview',
#    'kind' : 'cross',
##    'kind' : 'along',
#    }
#    p = plotter_solo.Plotter(array = arr, tstamps=tstamps,
#            x=x, y=y, z=z, projection=LambertConformalHRRR(),
#            plotter_options=my_po)
#    p.savefig('xxx.png', tidx=0)


    # make a plot template
    p = plotter_multi.Plotter(arrays=arrays, tstamps=tstamps, 
                             x=x, y=y, z=z, projection=LambertConformalHRRR(),
                             plotter_options=plotter_options_multi,
                            figure_options = figure_options)

    #p.savefig('dwprof_all.png', tidx=60)
    if maybe_hourly:
        ti = 0
    else:
        ti = 60
    p.savefig(oname.with_suffix('.png'), tidx=ti)

    nthreads = 24
    p.savemp4(oname, wdir=workdir, nthreads=nthreads)

if __name__ == '__main__':
    import sys
    import argparse
    from pathlib import Path

    p = argparse.ArgumentParser()
    p.add_argument('-o', '--outfile', type=str, default=None,
                   help='output mp4 filename',
                   )
    p.add_argument('-d', '--outdir', type=str, default=None,
                   help='output directory',
                   )
    p.add_argument('-t', '--title', type=str, default=None, help='title')
    p.add_argument('-w', '--workdir', type=str, default=None, help='workdir')
    p.add_argument('file', type=str, nargs='+', help='tseries files to process')
    args = p.parse_args()

    fname = args.file
    nfiles = len(fname)
    if nfiles == 1:
        fname = fname[0]

    if args.outfile is None:
        if nfiles > 1:
            raise ValueError('specify --outfile for multple input file')
            
        fn = Path(fname)
        oname = fn.name
        if oname.startswith('tseries'):
            oname = 'dwprof' + oname[6:]
        if args.outdir is None:
            odir = fn.parent
        else:
            odir = Path(args.outdir)
            if not odir.is_dir():
                odir.mkdir(parents=True, exist_ok=True)
       
        ofile = odir / oname

    else:
        outdir = args.outdir
        if outdir is None:
            ofile = Path(args.outfile)
        else:
            file = Path(ourdir) / ofile

    ofile = ofile.with_suffix('.mp4')

    try:
        workdir = args.workdir
    except AttributeError:
        workdir = None





    proc(fname, ofile, title=args.title, workdir=workdir)
