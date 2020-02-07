# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info,-toc,-latex_envs
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Using pyproj with cartopy
#
# The cells below show how to do coordinate transformations with either pyproj or cartopy.
# Since cartopy uses pyproj under the hood, we expect the same results.
# %%
import context
import json
import pprint
modis_image = context.modis_sat
print(modis_image)

from satcode.data_read import download
download(modis_image.name, dest_folder = context.data_dir)


# %%
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy
from pathlib import Path
import pprint
import numpy as np

#

# %%
# Datum: radius of the earth in meters
#
radius = 6_371_228
#
# vancouver longitude, latitude indegrees
#
van_lon, van_lat = [-123.1207, 49.2827]
#
# use a simple sphere as the datum
#
globe = ccrs.Globe(ellipse=None, semimajor_axis=radius, semiminor_axis=radius)

# %% [markdown]
# # Put the corners of a modis granule on the map.  Use this 2013.220.2105 granule
#
# <img src="images/myd2105.jpg" width=400>
#
#

# %% [markdown]
# ## Find the image corners using parseMeta

# %%
from satcode.modismeta_read import parseMeta
modis_dict = parseMeta(modis_image)

# %% [markdown]
# ## Make an LAEA projection using the spherical globe

# %%
pprint.pprint(modis_dict)
projection = ccrs.LambertAzimuthalEqualArea(
    central_latitude=modis_dict["lat_0"],
    central_longitude=modis_dict["lon_0"],
    globe=globe,
)

# %% [markdown]
# ## Here are the parameters cartopy is using to call pyproj

# %%
projection.proj4_params

# %%
projection.proj4_init

# %% [markdown]
# ## Make a pyproj projection using the cartopy parameters
#
# Show that we can "roundtrip" the coordinates -- i.e. go from lon,lat to x,y to lon, lat
# and get the starting values back

# %%
import pyproj

prj = pyproj.Proj(projection.proj4_init)
print("here are the lon,lat corners")
pprint.pprint(list(zip(modis_dict["lon_list"], modis_dict["lat_list"])))
x, y = prj(modis_dict["lon_list"], modis_dict["lat_list"])
print("here are the x,y corner coords")
pprint.pprint(list(zip(x, y)))
llcrnrlon, llcrnrlat = prj(x, y, inverse=True)
print("here are the lon,lat corners after roundtrip")
pprint.pprint(list(zip(llcrnrlon, llcrnrlat)))

# %% [markdown]
# ## Now repeat this using the modern WGS84 non-spherical earth datum
#
# **Note that changing to this datum makes a difference of about 3 km, (i.e. 1558 km becomes 1561 km below)**

# %%
globe_w = ccrs.Globe(datum="WGS84", ellipse="WGS84")

# %%
projection_w = ccrs.LambertAzimuthalEqualArea(
    central_latitude=modis_dict["lat_0"],
    central_longitude=modis_dict["lon_0"],
    globe=globe_w,
)
print(projection_w.proj4_init)
prj_w = pyproj.Proj(projection_w.proj4_init)
print("here are the lon,lat corners")
pprint.pprint(list(zip(modis_dict["lon_list"], modis_dict["lat_list"])))
x_w84, y_w84 = prj_w(modis_dict["lon_list"], modis_dict["lat_list"])
print("here are the x_w84,y_84 corner coords")
pprint.pprint(list(zip(x_w84, y_w84)))
print("here are the old x,y corner coords")
pprint.pprint(list(zip(x, y)))
llcrnrlon, llcrnrlat = prj_w(x_w84, y_w84, inverse=True)
print("here are the new lon,lat corners after roundtrip")
pprint.pprint(list(zip(llcrnrlon, llcrnrlat)))

# %% [markdown]
# ## now get the Vancouver location in transformed coords
#
# **First do it with cartopy:**

# %%
geodetic = ccrs.Geodetic()
van_point = projection_w.transform_point(van_lon, van_lat, geodetic)
print(van_point)

# %% [markdown]
# **now do it with pyproj to show result doesn't change:**

# %%
geodetic_prj = pyproj.Proj(geodetic.proj4_init)
van_point_prj = pyproj.transform(geodetic_prj, prj_w, van_lon, van_lat)
print(van_point_prj)
van_x, van_y = van_point_prj

# %% [markdown]
# ## Note that the scene center is 0,0 in the transformed coordinates

# %%
center_point = projection_w.transform_point(
    modis_dict["lon_0"], modis_dict["lat_0"], geodetic
)
print(center_point)

# %% [markdown]
# ## To set the extent for the plot, find the x,y mins and maxes

# %%
minx, maxx = np.min(x_w84), np.max(x_w84)
miny, maxy = np.min(y_w84), np.max(y_w84)
# left x, right x, left y, right y
extent = [minx, maxx, miny, maxy]

# %% [markdown]
# ## show that we get a "perfect fit"  with this extent
#
# First, plot vancover, then add to the plot by calling:
#
#     display(fig)
#
# to redisplay the figure.

# %%
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw={"projection": projection_w})
ax.set_extent(extent, projection_w)
ax.plot(van_x, van_y, "ro", markersize=10)

# %% [markdown]
# **Next add coastlines**

# %%
ax.gridlines(linewidth=2)
ax.add_feature(cartopy.feature.GSHHSFeature(scale="coarse", levels=[1, 2, 3]))
display(fig)

# %% [markdown]
# **now get the corner points of the image and plot the box with center point**

# %%
out = projection_w.transform_points(
    geodetic, np.array(modis_dict["lon_list"]), np.array(modis_dict["lat_list"])
)
xcoords = np.append(out[:, 0], out[0, 0])
ycoords = np.append(out[:, 1], out[0, 1])
ax.plot(xcoords, ycoords)
ax.plot(0, 0, "go", markersize=10)
display(fig)

# %% [markdown]
# ## Write the corner points out as a json file for future use
#
# [What is json?](https://www.w3schools.com/Js/js_json_intro.asp)
#
# (note that json doesn't understand numpy arrays, so need to convert them to python lists)

# %%
xcoords = list(xcoords)
ycoords = list(ycoords)
corner_dict = dict(xcoords=xcoords, ycoords=ycoords)
llcrnrlon, llcrnrlat = prj_w(xcoords, ycoords, inverse=True)
lons = list(llcrnrlon)
lats = list(llcrnrlat)
corner_dict["filename"] = modis_dict["filename"]
corner_dict["lons"] = lons
corner_dict["lats"] = lats
corner_dict["proj4_string"] = projection_w.proj4_init
corner_dict["proj4_params"] = projection_w.proj4_params
corner_dict["extent"] = extent
pprint.pprint(corner_dict)

# %%
corner_output = context.data_dir / Path("corners.json")
with open(corner_output, "w") as f:
    json.dump(corner_dict, f, indent=4)

# %% [markdown]
# ```python
# %load ../data/corners.json
# {
#     "xcoords": [
#         1561347.9917805532,
#         -744961.1366254934,
#         -1285873.5967137816,
#         1019738.9399581843,
#         1561347.9917805532
#     ],
#     "ycoords": [
#         -688348.6658615287,
#         -1179100.5032042824,
#         804312.7470663546,
#         1297248.5261361937,
#         -688348.6658615287
#     ],
#     "lons": [
#         -104.77089390290801,
#         -129.005397891393,
#         -138.038848796623,
#         -107.001718605882,
#         -104.77089390290801
#     ],
#     "lats": [
#         32.13645206898284,
#         28.687374622563773,
#         45.73346985640787,
#         50.510827489422674,
#         32.13645206898284
#     ],
#     "proj4_string": "+datum=WGS84 +ellps=WGS84 +proj=laea +lon_0=-121.4048713497655 +lat_0=39.59910106367865 +x_0=0.0 +y_0=0.0 +no_defs",
#     "proj4_params": {
#         "datum": "WGS84",
#         "ellps": "WGS84",
#         "proj": "laea",
#         "lon_0": -121.4048713497655,
#         "lat_0": 39.59910106367865,
#         "x_0": 0.0,
#         "y_0": 0.0
#     },
#     "extent": [
#         -1285873.5967137816,
#         1561347.9917805532,
#         -1179100.5032042824,
#         1297248.5261361937
#     ]
# }
# ```

# %% [markdown]
# ## Use [pyproj.geoid](https://jswhit.github.io/pyproj/pyproj.Geod-class.html) to get distance between points

# %%
from pyproj import Geod

g = Geod(ellps="WGS84")
bottom_right = [lons[0], lats[0]]
bottom_left = [lons[1], lats[1]]
top_left = [lons[2], lats[2]]
top_right = [lons[3], lats[3]]
az1, az2, ew_dist = g.inv(
    bottom_left[0], bottom_left[1], bottom_right[0], bottom_right[1]
)
az3, az4, ns_dist = g.inv(bottom_left[0], bottom_left[1], top_left[0], top_left[1])

# %%
print(
    (
        f"east-west distance is {ew_dist*1.e-3:8.3f} km,"
        f"\nnorth-south distance is {ns_dist*1.e-3:8.3f} km"
    )
)

# %%
points_xy = list(zip(xcoords, ycoords))
bottom_right_x, bottom_right_y = points_xy[0]
bottom_left_x, bottom_left_y = points_xy[1]
top_left_x, top_left_y = points_xy[2]

# %%
ew_dist = bottom_right_x - bottom_left_x
ns_dist = top_left_y - bottom_left_y
print(
    (
        f"east-west distance is {ew_dist*1.e-3:8.3f} km,"
        f"\nnorth-south distance is {ns_dist*1.e-3:8.3f} km"
    )
)

# %%
