#!/usr/bin/env python
import sys

plotterdir = './repo/plotter'
sys.path.insert(0, plotterdir)

from plotter.reader import reader, get_format

from plotnine import (
    ggplot, aes, geom_point, stat_smooth, geom_smooth, labs,
    geom_line, geom_ribbon, 
    scale_x_continuous, scale_x_date,
    scale_color_brewer,
    scale_alpha_manual,
    scale_y_log10, 
    scale_size_manual, 
)
import plotnine as p9
p9.options.dpi = 300

import pandas as pd
import numpy as np
# from pathlib import Path

import argparse

import get_receptor_coords


def read_what_to_do():

    # i am going to get file names from command lines, does this work?
    p = argparse.ArgumentParser(
            description='tell me what tsereis file to process, you get ts plot')

#    # this would be way to use multiple files in series for one scenario
#    p.add_argument('-i', '--input', help='(series of) input tseries files',
#                   type=str, nargs='+', action='append')

#    # list of tseries file, each file is treated as one time series
#    p.add_argument('input', help='input tseries files',
#                   type=str, nargs='+')

    # list of tseries file, each file is treated as one time series
    p.add_argument('input', help='input tseries files',
                   type=str, nargs=2)

    # output file name (mp4)
    p.add_argument('-o', '--output', 
                   help='output png file name', 
                   default='ts.png', 
                   type=str,
                   )

    # embedded title to use
    p.add_argument('-t', '--title', 
                   help='title to use', 
                   default=None, 
                   type=str,
                   )

    args = p.parse_args()
    return args


# read command line options
args = read_what_to_do()

fnames = args.input
oname = args.output
title = args.title

if title is None:
    title = ''

fmts = [get_format(fn) for fn in fnames]

titles = [{'calpost': 'Calpuff', 'hysplit': 'Hysplit'}[_] for _ in fmts]

# calpost knows location but hysplit needt to be told
xs = [{'calpost': None, 'hysplit': get_receptor_coords.df.x}[_] for _ in
      fmts]
ys = [{'calpost': None, 'hysplit': get_receptor_coords.df.y}[_] for _ in
      fmts]

dats = [reader(fn, x=x, y=y,)
        for fn, x, y in zip(fnames, xs, ys)]

# find common time period
tstamps = [_['ts'] for _ in dats]

if tstamps[0][0] < tstamps[1][0]:
    s0 = np.where(tstamps[1][0] == tstamps[0])
    s1 = 0
    print('s0', s0)
    assert len(s0) == 1
    s0 = int(s0[0])
else:
    s1 = np.where(tstamps[0][0] == tstamps[1])
    s0 = 0
    print('s1', s1)
    assert len(s1) == 1
    s1 = int(s1[0])

if tstamps[0][-1] < tstamps[1][-1]:
    e1 = np.where(tstamps[0][-1] == tstamps[1])
    e0 = None
    print('e1', e1)
    assert len(e1) == 1
    e1 = int(e1[0]) + 1
else:
    e0 = np.where(tstamps[1][-1] == tstamps[0])
    e1 = None
    print('e0', e0)
    assert len(e0) == 1
    e0 = int(e0[0]) + 1

assert np.all(tstamps[0][s0:e0] == tstamps[1][s1:e1])


def arr2df(arrays, ts, tags, n=None):
    # take arr, ts from reader, return dataframe for ggplot

    vs = [arr.reshape(arr.shape[0], -1) for arr in arrays]

    v = vs[0]

    # drop nans
    vs = [v[:, ~np.isnan(v[0, :])] for v in vs]

    v = vs[0]
    nn = v.shape[-1]
    if n is None:
        n = nn
    sel = sorted(np.random.choice(np.arange(nn), n, replace=False))
    # print(sel)

    dfs = []
    for v, tag in zip(vs, tags):
        df = pd.DataFrame( 
            dict( 
                tag=tag,
                t=np.repeat(ts, n),
                v=v[:, sel].reshape(-1),
            ))
        df['hr'] = (df['t'] - df['t'][0]).dt.total_seconds() / 3600
        dfs.append(df)

    df = pd.concat(dfs, axis=0)
    return df


# extract necessary data
print(dats[0]['v'].shape, dats[0]['ts'].shape, dats[0]['ts'][0], dats[0]['ts'][-1], s0, e0)
print(dats[1]['v'].shape, dats[1]['ts'].shape, dats[1]['ts'][0], dats[1]['ts'][-1], s1, e1)
arrays = [dat['v'][s:e] for dat, s, e in zip(dats, (s0, s1), (e0, e1))]
tss = [ts[s:e] for ts, s, e in zip(tstamps, (s0, s1), (e0, e1))]
ts = tstamps[0][s0:e0]

# conversion factors
convfacs = [{'calpost': 1. / 16.043 * 0.024465403697038 * 1e9, 
             'hysplit': 1., }[_] for _ in fmts]

arrays = [arr*cf for arr, cf in zip(arrays, convfacs)]

# array has nan, so mask them
arrays = [np.ma.masked_invalid(arr) for arr in arrays]

print('xxx')
print([_.shape for _ in arrays])
print([_.shape for _ in tss])
print(ts.shape)

# convert data into dataframe
df = arr2df(arrays, ts, titles)  # , n=50)

df2 = df.loc[:, ['tag', 'hr', 'v']].groupby(['tag', 'hr']).quantile(
    q=[.9, .99, 1]).unstack()
df2.columns = ['q090', 'q099', 'q100']

df2 = df2.reset_index().melt(id_vars=['tag', 'hr'], var_name='q',
                             value_name='v')

df2['g'] = df2['tag'] + df2['q'].astype(str)

hrmax = df['hr'].max()
p = (
    ggplot(df2) + 
    geom_line(aes('hr', 'v', color='tag', alpha='q', size='q', group='g')) +
    scale_x_continuous(breaks=np.arange(0, hrmax, 24),
                       minor_breaks=np.arange(0, hrmax, 6),
                       ) +
    scale_color_brewer(type='qual', palette='Set1') +
    scale_alpha_manual(np.linspace(1, 0.2, num=3)) + 
    scale_size_manual([2, 1, .5]) +
    labs(title=title, y='conc (ppb)')
)
p.save(oname)

print(df2['v'].max())
pp = p + scale_y_log10(limits=[1.0, df2['v'].max()])
pp.save(oname[:-4] + '_log.png')
