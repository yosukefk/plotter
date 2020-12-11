# Plotter

Plots raster data with time (dimensions of time, x, y) using Cartopy/Matplotlib, and saves annimation

## Install

Instead of official python, it is highly recommended to use Anaconda Python + conda-forge, as GIS related packages is a lot harder to install with regular python. 

`conda create --name plotter`  
`conda activate plotter`

Grab code from git repo

`git clone https://github.com/yosukefk/plotter.git`

Grab required pacages

`conda install -c conda-forge --file requirements.txt`

## Usage

Working example, can take it as a starting point for your work

`cd demo`

`python work_pretty_solo.py`

`python work_pretty_trio.py`

Unittest, when things broke run this test if part of tool is broken.

`cd unittest`

`python tests.py`
