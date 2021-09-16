import numpy as np
import os
def asc_reader(f, ts=None):



    o = None
    for i in range(len(f)):
        if i % 3600 == 0: print(i)
        if not os.path.exists( f[i] ):
            continue

        if o is None:
            a,x,y,g = asc_reader_one(f[i], xy=True)
            o = np.zeros((len(f), len(y), len(x)))
        else:
            a = asc_reader_one(f[i], xy=False)
        o[i, ...] = a

    return {'x': x, 'y': y,  'v': o, 'grid': g}

def asc_reader_one(fname, xy=False):
    with open(fname) as f:

        ncol = int(next(f)[6:])
        nrow = int(next(f)[6:])
        xll = float(next(f)[10:])
        yll = float(next(f)[10:])
        siz = float(next(f)[9:])
        nd = float(next(f)[13:])

        if xy:
            x = np.arange(ncol) * siz + xll
            y = np.arange(nrow) * siz + yll
            grid  = {'x0': xll, 'y0': yll, 
                     'x1': xll + siz*(ncol-1), 
                     'y1': yll + siz*(nrow-1),
                     'dx': siz,
                     'dy': siz,
                     'nx': ncol,
                     'ny': nrow,
                     }
        arr = np.loadtxt(f)
        #print(arr.shape)
    assert arr.shape == (nrow, ncol)
    # i think i need to flip upside down
    arr = arr[::-1, :]
    if xy:
        return (arr, x, y, grid)
    else:
        return arr

def tester():
    asc_reader_one('../../../from_surfer/00210.asc')
#tester()
