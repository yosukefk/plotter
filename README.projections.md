## how to deal with projections

### projections (or coordinate reference system CRS)

a lot of stuff on a plot comes from data which projection (more precisely CRS coordinate reference system).

1. gridded data:  for our application it is rectangular grid cells
2. overlaid vector data (polygons, points etc): for example some kind of boundaries, emission sources
3. background image: sometimes you have image file to use as background.  Othertimes, you want to use web map (e.g. Google Earth) for background.  
4. plot you are making:  Often time you would stick to original data grid.  sometime you want the plot to use particular projection (eg. want to paste image from this tool to GoogleMap based application)

This note discuss if plotter can handle each of them, and if it does how to do it.

#### 1. model gridded data 

In plotter, gridded data needs to be decomposed by user than fed to the tool.  User will provide

* array of data to plot (3-d array with shaped (time, y, x) )
* time stamps (1-d array, length has to match the first dimesio of the 3-d array)
* y coordinates (1-d array, length must match the second dimsion of the 3-d data array)
* x coordinates (1-d array, length must match the third dimsion of the 3-d data array)
* projection (horizontal CRS) being used


#### 2. overlaid vector data

It can come with (1) table of x,y coordinates and some attributes, (2) series of poitns to definie polygons (3) GIS vector layer such as shapefile.  

In either way, what you have to do is to use lambda expression to is GeoAxes object https://scitools.org.uk/cartopy/docs/v0.13/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes  `plotter_options['customize_once': [ lambda p: p.ax.do_something_here() ] ]`

```
from shapely.geometry import Polygon

geom = Polygon([(x1,y1), (x2,y2), ... ])

plotter_options = {
    'customize_once': [
        lambda p: p.ax.add_geometry(
            ____
        ), 
        ....
    ],
    ....
}

p = plotter_solo.Plotter( ..., plotter_options=plotter )

```



#### 3. background raster data


#### 4. output plot


