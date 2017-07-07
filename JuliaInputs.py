# Writes constants to input.julia for use in JuliaGif.py

import random

import numpy as np

n = 250            # each subimage is n*n pixels
split = 3          # final image is split*split subimages stitched together
iters = 100        # number of function iterations
frameCount = 300   # number of frames in gif
r = 1.5            # image radius
gifType = random.choice(['linear']*3 + ['radial']*2 + ['zoom']*4)

# Get original c constant
c = complex(1,1)
while abs(c) > 1:
    c = complex(random.uniform(-1,1), random.uniform(-1,1))

# Get final c for linear gif type
path = 0.5        # path length
cEnd = complex(1,1)
while abs(cEnd) > 1:
    angle = random.uniform(-np.pi,np.pi)
    cEnd = complex(c.real + path*np.cos(angle), c.imag + path*np.sin(angle))

# Get constants for radial gif type
rad = random.uniform(0.25, 1)
angle = random.uniform(0, np.pi)

# Get constants for zoom gif type
center = random.uniform(0, 1)*np.exp(1j*random.uniform(0, 2*np.pi))
rStart = 0.000001
rEnd = 1.50

with open("input.julia", "w") as out:
    out.write(' '.join(map(repr, [n, split, iters, frameCount, r, c.real, c.imag])) + '\n')
    out.write(' '.join(map(repr, [cEnd.real, cEnd.imag])) + '\n')
    out.write(' '.join(map(repr, [rad, angle])) + '\n')
    out.write(' '.join(map(repr, [center.real, center.imag, rStart, rEnd])) + '\n')
    out.write(gifType)
