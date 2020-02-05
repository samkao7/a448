import sys
from pathlib import Path

path = Path(__file__).resolve()  # this file
this_dir = path.parent  # this folder
lib_dir = this_dir / 'satcode'
root_dir = this_dir.parent
data_dir = root_dir / 'data'

before_dir = data_dir / 'before_image'
modis_sat = data_dir / 'MYD021KM.A2013222.2105.061.2018047235850.hdf'

sys.path.insert(0, str(lib_dir))
sep = "*" * 30
print(f"{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n"
      f"back of path: {sys.path[-1]}\n{sep}\n")
