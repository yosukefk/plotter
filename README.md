# Plotter

Plots raster data with time (dimensions of time, x, y) using Cartopy/Matplotlib, and saves annimation

## Install

Instead of official python, it is highly recommended to use Anaconda Python + conda-forge, as GIS related packages is a lot harder to install with regular python. 

If you are completely new to Anaconda/Python, I recommend install "Miniconda".  That should provide you either (1) dedicated way to start command line terminal with conda enabled, or (2) your default setting is changed to use with conda or (3) you have to always type `conda activate` before using conda based tools.  In either way, command line prompt will be change to have `(base) PS C:\Users\Yosuke> ` or `(base) ~ $ ` something like that, having "(base)" included in the prompt.  You are ready to install.

Grab code from git repo

`git clone https://github.com/yosukefk/plotter.git`

Go into main directory

`cd plotter`

Grab required pacages

`conda install -c conda-forge --file requirements.txt`

Install to your python path

`pip install .`

Now you should be able to `import plotter` to use the tool, from python environment (either python script, or python interactive session).

## Usage

Working example, can take it as a starting point for your work

`cd demo`

`python work_pretty_solo.py`

`python work_pretty_trio.py`

~~Unittest, when things broke run this test if part of tool is broken.~~ (i think it has been broken)

~~`cd unittest`~~

~~`python tests.py`~~
