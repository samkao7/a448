# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.2.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---
# %% [markdown]
# # Use pyresample to make a projected image
#
# In the cartopy_mapping_pyproj notebook we stored projection
# coords in a json file called corners.json.  This notebook
# reads that information back in to plot lats/lons on a map
# %%
import context
import json
import pprint


import cartopy
from pyhdf.SD import SD
from pyhdf.SD import SDC
from pyresample import kd_tree
modis_image = context.modis_sat
print(modis_image)

from satcode.data_read import download
download(modis_image.name, dest_folder = context.data_dir)

# %%
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

#

# %% [markdown]
# # Read the lons/lats from the MYD03 file
#
# **substitute your filename**

# %%
# Read the lats and lons from the MYD03 file
m3_path = context.modis_sat
print(f"reading {m3_path}")
m3_file = SD(str(m3_path), SDC.READ)
lats = m3_file.select("Latitude").get()
lons = m3_file.select("Longitude").get()

# %% [markdown]
# # get the map projection from corners.json
#
# Get the map  projection and extent from corners.json

# %%
json_file = context.data_dir / Path("corners.json")
with open(json_file, "r") as f:
    map_dict = json.load(f)
pprint.pprint(map_dict)

# %% [markdown]
# # Use pyresample to define a new grid in this projection

# %%
from pyresample import SwathDefinition

proj_params = map_dict["proj4_params"]
swath_def = SwathDefinition(lons, lats)
area_def = swath_def.compute_optimal_bb_area(proj_dict=proj_params)

# %%
dir(area_def)

# %% [markdown]
# # resample the longitudes on this grid

# %%
fill_value = -9999.0
area_name = "modis swath 5min granule"
image_lons = kd_tree.resample_nearest(
    swath_def,
    lons.ravel(),
    area_def,
    radius_of_influence=5000,
    nprocs=2,
    fill_value=fill_value,
)
print(f"\ndump area definition:\n{area_def}\n")
print(
    (
        f"\nx and y pixel dimensions in meters:"
        f"\n{area_def.pixel_size_x}\n{area_def.pixel_size_y}\n"
    )
)

# %% [markdown]
# # replace missing values with floating point nan

# %%
nan_value = np.array([np.nan], dtype=np.float32)[0]
image_lons[image_lons < -9000] = nan_value

# %% [markdown]
# # Plot the image using cartopy

# %%
crs = area_def.to_cartopy_crs()
ax = plt.axes(projection=crs)
ax.coastlines()
ax.set_global()
plt.imshow(image_lons, transform=crs, extent=crs.bounds, origin="upper")
plt.colorbar()

# %%
crs.globe.to_proj4_params()

# %%

# %%
