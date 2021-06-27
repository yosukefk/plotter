
import plotnine as p9
from plotnine import (
    ggplot, aes, geom_point, stat_smooth, geom_smooth, labs,
    geom_line, geom_ribbon, 
    geom_vline,
    scale_x_continuous, scale_x_date,
    scale_color_brewer,
    scale_alpha_manual,
    scale_y_log10, 
    scale_size_manual, 
)

import matplotlib.pylab as plt
import matplotlib.image as img

import pandas as pd
import numpy as np
import tempfile


class PlotterTseries:
    def __init__(self, array, tstamps, plotter_options=None):
        """

        :rtype: PlotterTseries
        :param dict array: dict of 3-d array of data values
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t)
        :param dict plotter_options: all the arguments passed to plotter
        """

        if plotter_options is None: plotter_options = {}

        # i have to know the axes being used, even user wants default
        # so i grab default axes here and hold onto it
        # TODO this seems to creats open figure and unless i close this
        # somehow it hangs there wasting memory.  what should I do?
        # shouldnt this be get instad of setdefault?
        # self.fig = plotter_options.setdefault('fig', plt.figure())
        self.fig = plotter_options.get('fig', plt.figure())
        pos = plotter_options.get('pos', None)

        # cat all the data into one dataframe
        self.df = self.arr2df(array, tstamps)
        self.tstamps = tstamps

        # create plots
        if pos:
            self.ax = self.fig.add_subplot(*pos)
        else:
            self.ax = self.fig.add_subplot()

        # get quantiles
        # TODO allow user to do whatever somehow
        qpoints = [.9, .99, 1]
        qlabels = [ "{0:.0%}".format(_) for _ in qpoints]
        nq = len(qpoints)
        self.df2 = self.df.groupby(['tag', 't']).quantile(q=qpoints).unstack()

        # massage the dataframe
        self.df2.columns = qlabels
        self.df2 = self.df2.reset_index().melt(id_vars=['tag', 't'],
                                               var_name='q',
                                               value_name='v')
        self.df2['q'] = pd.Categorical(self.df2['q'], categories=qlabels)
        self.df2['g'] = self.df2['tag'] + self.df2['q'].astype(str)

        # base tseries plot
        self.gg = ( 
            ggplot(data=self.df2, mapping=aes('t', 'v' )) + 
            geom_line(aes(color='tag',alpha='q', size='q', group='g')) +
            # TODO nice time axis needed
#            scale_x_continuous(breaks=np.arange(0, hrmax, 24),
#                       minor_breaks = np.arange(0, hrmax, 6),
#            ) +
            scale_color_brewer(name='Model', type='qual', palette='Set1') +
            scale_alpha_manual(values=np.linspace(1, .2, num=nq)) + 
            scale_size_manual(values=np.geomspace(2, .5, num=nq)) +
            scale_y_log10(limits=[1.0, self.df2['v'].max()]) +
            labs(
                #title=title, 
                #x='hour', 
                y='conc (ppb)', 
                alpha='Quantile', 
                 size='Quantile',))
        self.hasdata = False



    def update(self, tidx=None, footnote=None, title=None):
        """
        Update plot to data at tidx

        :param int tidx: time index
        :param str footnote: footnote overwrite
        :param str title:  title overwrite
        """
        if tidx is None: tidx = 0
        t = self.tstamps[tidx]
        #print(self.df2.loc[self.df2['t'] == t, :])
        gg = ( self.gg + 
                 geom_vline(aes(xintercept=t)) + 
                 geom_point(data=self.df2.loc[self.df2['t'] == t, :],
                            mapping=aes('t', 'v', color='tag'),
                            inherit_aes=False) 
                 )
        arr = self.gg2arr(gg)
#        print(arr)
#        print(arr.shape)
#        print(np.quantile(arr[:,:,0], q=np.linspace(0,1)))
#        print(np.quantile(arr[:,:,1], q=np.linspace(0,1)))
#        print(np.quantile(arr[:,:,2], q=np.linspace(0,1)))
#        print(np.quantile(arr[:,:,3], q=np.linspace(0,1)))

        if self.hasdata:
#            print('b')
            self.im.set_data(arr)
        else:
#            print('a')
            self.im = self.ax.imshow(arr)
            self.ax.set_axis_off()
#            print(self.im)
            self.hasdata = True

                                        
    @staticmethod
    def arr2df(arrays, ts):
        """
        take arr, ts from reader, return dataframe for ggplot

        :rtype: pd.DataFrame
        :param dict arrays:
        :param np.ndarray tstamps: 1-d array of datetime, dimensions(t)
        """

        # flatten spatial dimensions
        vs = {k:arr.reshape(arr.shape[0], -1) for k,arr in arrays.items()}

        # drop nans
        vs = {k:v[:, ~np.isnan(v[0, :])] for k,v in vs.items()}



        n = list(vs.values())[0].shape[-1]
        dfs = []
        for k, v in vs.items():
            vv = v.reshape(-1)
            df = pd.DataFrame( 
                dict( 
                    tag = k,
                    t = np.repeat(ts, n), 
                    v = vv,
                ))
            dfs.append(df)

        df = pd.concat(dfs, axis=0)
        return df


    @staticmethod
    def gg2arr(gg):
        """
        ggplot into image, and then read

        :param p9.ggplot, gg:
        """
        fig = plt.figure()#figsize=figsize)
        plt.autoscale(tight=True)
        #gg.save('gg.png')#, height=height, width=width, verbose=False)
        #arr = img.imread('gg.png')
        with tempfile.NamedTemporaryFile() as f:
            gg.save(f.name, format='png')
            arr = img.imread(f.name, format='png')
        return arr


