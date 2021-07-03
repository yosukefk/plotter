

from pyproj import CRS, Transformer
import pandas as pd
import numpy as np

class HysplitReceptorCoords:
    def __init__(self, fname, grid, crs):

        self.grid = grid
        self.crs = crs

        # grid centroilds
        xc = (np.arange(grid['nx']) + .5) * grid['dx'] + grid['x0']
        yc = (np.arange(grid['ny']) + .5) * grid['dy'] + grid['y0']
        self.x = xc
        self.y = yc

        # crs
        crs_wgs = CRS.from_epsg(4326)
        crs_model = CRS.from_proj4(crs.proj4_init)

        self.trns= Transformer.from_crs(crs_wgs, crs_model)


        # read the receptor file
        df = pd.read_csv(fname, delimiter=' ', names=['rdx', 'lat', 'lon'])

        # get x,y coords
        x, y =  [_ * .001 for _ in self.trns.transform(df.lat, df.lon)]
        df['x'], df['y'] = x, y

        # get i,j
        idx = np.array([np.arange(len(xc))[np.isclose(_, xc)][0] for _ in x])
        jdx = np.array([np.arange(len(yc))[np.isclose(_, yc)][0] for _ in y])
        df['idx0'], df['jdx0'] = idx, jdx
        df['idx1'], df['jdx1'] = idx+1, jdx+1

        # see if grid is fully covered, and if it does order
        nx, ny = len(self.x), len(self.y)
        self.nx, self.ny = nx, ny
        cnt_g = nx  * ny
        cnt_d = len(df.index)
        self.nsta = cnt_d
        if cnt_g == cnt_d:
            # full
            if np.all(idx == np.tile(np.arange(nx), ny)) \
                    and np.all(jdx == np.repeat(np.arange(ny), nx)):
                self.coverage = 'full, c-order'
            elif np.all(idx == np.repeat(np.arange(nx), ny)) \
                and np.all(jdx == np.tile(np.arange(ny), nx)):
                self.coverage = 'full, f-order'
            else:
                self.coverage = 'full, random'
        elif cnt_g > cnt_d:
            self.coverage = 'partial, random'
        else:
            raise ValueError('more data than grid def')

        print(self.coverage)


        #df = df.set_index('rdx', drop=False)
        self.df = df

    def __str__(self):
        return f'HysplitReceptorCoords(grid={self.grid}, coverage="{self.coverage}")'

    def get_index(self, rdx, base=0):
        if base == 0:
            cols = ['idx0', 'jdx0']
        elif base == 1:
            cols = ['idx1', 'jdx1']
        else:
            raise ValueError(f'base: {base}')

        if not isinstance(rdx, (pd.Series, pd.DataFrame)):
            rdx = pd.Series(rdx, name='rdx')
            print(rdx)
        #return self.df.join( pd.Series(rdx, name='rdx'), on = 'rdx')
        return self.df.merge( rdx, how='right' ).loc[:, cols]



if __name__== '__main__':
    from plotter.plotter_util import LambertConformalTCEQ, LambertConformalHRRR

    fname_pilot = 'receptor_200m.all.txt'
    fname_toy = 'toy_model_allstations.txt'


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

    hrc_toy = HysplitReceptorCoords(fname_toy, grid_toy, LambertConformalTCEQ())
    hrc_pilot = HysplitReceptorCoords(fname_pilot, grid_pilot, LambertConformalHRRR())

    print(hrc_pilot.get_index(pd.DataFrame(
                                           {'rdx':[1,2,3,11]},
        index=[1,2,3,11],
                                           )))
