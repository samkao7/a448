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

# %%
import context
from pathlib import Path
from satpy import Scene


# %%
print(context.before_dir)
before_files = [str(item) for item in Path(context.before_dir).glob("*B6*.TIF")]
print(before_files)
scn = Scene(reader="generic_image", filenames=before_files)
scn.load(['image'])
scn.save_datasets(writer='simple_image',filename='b6.png',datasets=['image'])

# %%
from PIL import Image               # to load images
from IPython.display import display # to display images

pil_im = Image.open('b6.png')
thumbnail=pil_im.resize([400,400])
display(thumbnail)

# %%
#display(pil_im)

# %%
