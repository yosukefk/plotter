#!/usr/bin/env python
import sys

#plotterdir = './repo/plotter'
plotterdir = '..'
sys.path.insert(0, plotterdir)

import plotter.plotter_reader as pr
import plotter.hysplit_coords as hsc
import plotter.plotter_util as pu
import plotter.hysplit_reader as hsr

from pathlib import Path

from importlib import reload


reload(pr)
reload(hsc)
reload(hsr)

ddir = Path(plotterdir) / 'data'

#rname_toy = '../../scripts/toy_model_allstations.txt'
rname_toy = ddir / 'toy_model_allstations.txt'
rname_pilot = ddir / 'receptor_200m.all.txt'
grid_toy = {'x0': -464.4,
             'y0': -906.7,
             'nx': 34,
             'ny': 47,
             'dx': 0.1,
             'dy': 0.1}
grid_pilot = {
     'x0': -440.8,
      'y0': -730.0,
      'nx': 48,
      'ny': 44,
      'dx': 0.2,
      'dy': 0.2}

hsc_toy = hsc.HysplitReceptorCoords(rname_toy, grid_toy, pu.LambertConformalTCEQ())
#hsc_pilot = hsc.HysplitReceptorCoords(rname_pilot, grid_pilot,
#                                      pu.LambertConformalHRRR())

#fname_toy2 = f'../../scripts/outconc.S2.const.hrrr.2m75kghr.3d.station_2.txt'
#fname_toy = [
#    f'../../scripts/outconc.S2.const.hrrr.2m75kghr.3d.station_{_+1}.txt' for _ in range(11)]
#fname_pilot = '../outconc.outconc.hrrr.pilot.sep.w0306.200receptor.txt'
fname_toy2 = ddir / f'outconc.S2.const.hrrr.2m75kghr.3d.station_2.txt'
fname_toy = [
    ddir / f'outconc.S2.const.hrrr.2m75kghr.3d.station_{_+1}.txt' for _ in range(11)]
fname_pilot = ddir / 'outconc.outconc.hrrr.pilot.sep.w0306.200receptor.txt'

#dat_pilot = pr.reader(fname_pilot, rdx_map = hsc_pilot)
#dat = pr.reader(fname_toy, rdx_map = hsc_toy)
dat = pr.reader(fname_toy2, rdx_map = hsc_toy)
