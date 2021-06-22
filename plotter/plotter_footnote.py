import matplotlib as mpl
import numpy as np


class FootnoteManager:
    """Manages Footnote"""

    def __init__(self, plotter, footnote=None, footnote_options=None):
        """

        :rtype: FootnoteManager
        :param PlotterCore plotter:  PlotterCore to which footnote is added
        :param str,  footnote: default footnote
        :param dict,  footnote_options (optional):
        """
        print('opt footnote:', footnote)
        self.plotter = plotter
        if footnote_options is None:
            footnote_options = {}
        if footnote is None:
            self.footnote_template = footnote_options.get(
                'text',
                "{tstamp}\nMin({imn}, {jmn}) = {vmn:.1f}, Max({imx}, {jmx}) = {vmx:.1f}"
            )
        else:
            self.footnote_template = footnote

        keys_to_extract = (
            'tstamp_format', 'minmax_format',
        )
        self.footnote_options = {k: v for k, v in footnote_options.items() if
                                 k in keys_to_extract}

        if hasattr(self.plotter, 'ax'):
            print('ax')
            # builtin options
            myopts = dict(
                # text=footnote, # matplotlib >= 3.3 renamed to 's' to 'text'
                s=footnote,  # matplotlib < 3.2 needs 's' for annotate
                xy=(0.5, 0),  # bottom center
                xytext=(0, -6),
                # drop 6 ponts below (works if there is no x axis label)
                # xytext=(0,-18), # drop 18 ponts below (works with x-small fontsize axis label)
                xycoords='axes fraction',
                textcoords='offset points',
                ha='center', va='top',
            )
            myopts.update({k: v for k, v in footnote_options.items() if k not in
                           keys_to_extract})

            if mpl.__version__ < '3.3' and 'text' in myopts:
                myopts['s'] = myopts['text']
                del myopts['text']

            self.footnote = self.plotter.ax.annotate(**myopts)
            self()
        elif hasattr(self.plotter, 'fig'):
            print('fig')
            # builtin options
            # no clue why, but y=0.2 puts text nicely below the plots, for pair case...
            print('nplot = ', self.plotter.nplot)
            
            if self.plotter.nplot <= 2:
                my_ypos = .2
            elif self.plotter.nplot >=3:
                my_ypos = .3
            myopts = dict(
                #text=footnote, # matplotlib >= 3.3 renamed to 's' to 'text'
                s=footnote,  # matplotlib < 3.2 needs 's' for annotate
                x=0.5,
                y=my_ypos,  
                ha='center', va='top',
            )
            myopts.update({k: v for k, v in footnote_options.items() if k not in
                           keys_to_extract})
            myopts['s'] = myopts.pop('text', myopts['s'])
            print(myopts)

            self.footnote = self.plotter.fig.text(**myopts)
        else:
            raise RuntimeError(f'not sure what this is: {self.plotter}')

    def __call__(self, footnote=None):
        """
        either rewrite footnote altogether, or update using the template

        :param str footnote: overwrites footnote
        """
#        print('fn call', self.plotter)
        if footnote is None:
            footnote = self._update_text()
        self.footnote.set_text(footnote)

    def _update_text(self):
        """Generate standard footnotes"""

        if hasattr(self.plotter, 'ax'):
            my_plotter = self.plotter
        else:
            my_plotter = self.plotter.plotters[0]

        arr = my_plotter.current_arr
        tstamp = my_plotter.current_tstamp

        if 'tstamp_format' in self.footnote_options:
            tstamp = tstamp.strftime(self.footnote_options['tstamp_format'])

        i0 = my_plotter.i0
        j0 = my_plotter.j0
        # find timestamp and min/max
        jmn, imn = np.unravel_index(arr.argmin(), arr.shape)
        jmx, imx = np.unravel_index(arr.argmax(), arr.shape)
        vmn = arr[jmn, imn]
        vmx = arr[jmx, imx]
        imn += i0
        imx += i0
        jmn = j0 - jmn
        jmx = j0 - jmx
        # vmn,vmx = [fnf.format(_) for _ in (vmn, vmx)]
        current_text = self.footnote_template.format(**locals())
        return current_text



