from glob import glob

import h5py
import matplotlib.pyplot as plt
import numpy as np

files = glob('/home/raul/WY_SOUNDINGS/*_ptomnt_*.h5')
files.sort()

matrix = np.empty((366 * 2, 12))
for c, file in enumerate(files):
    print(file)
    f = h5py.File(file, 'r')
    for r, k in enumerate(f.keys()):
        shape = f[k + '/table'].value[0][1].shape[0]
        if shape == 1:
            matrix[r][c] = 0
        else:
            matrix[r][c] = 1

fig, ax = plt.subplots()
ax.pcolormesh(matrix, vmin=0, vmax=1)

# Set the major ticks at the centers and minor 
# tick at the edges
labels = [str(l).zfill(2) for l in range(0, 12)]
locs = np.arange(len(labels))
ax.xaxis.set(ticks=locs + 0.5, ticklabels=labels)
ax.xaxis.set_ticks(locs, minor=True)
ax.grid(True, which='minor')

plt.show(block=False)
