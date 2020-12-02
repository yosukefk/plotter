import reader

fname = '../calpost/tseries_ch4_1min_conc_co_fl.dat'
with open(fname) as f:
    dat = reader.reader(f, slice(60*12, 60*12+1))


g = dat['grid']
ext = (g['x0'], g['x0'] + g['dx']*g['nx'],
g['y0'], g['y0'] + g['dy']*g['ny'])
ext = [_*1000 for _ in ext]

arr = dat['v'][:,::-1,:]
