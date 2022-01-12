from setuptools import setup

setup(
        name='plotter',
        version='1.1.0',
        description='make tile plot from camx/calpuff etc',
        url='https://github.com/yosukefk/plotter',
        license='MIT',
        packages=['plotter'], 
        install_requires=[
            'cartopy>=0.18', 
            'pandas>=1.1.4',
            ],
        )
