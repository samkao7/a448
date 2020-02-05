import context
from pathlib import Path
from satpy import Scene
print(context.before_dir)
before_files = [str(item) for item in Path(context.before_dir).glob("*B6*.TIF")]
print(before_files)
scn = Scene(reader="generic_image", filenames=before_files)
scn.load(['image'])
print(help(scn))
scn.save_datasets(writer='simple_image',filename='b6.png',datasets=['image'])










