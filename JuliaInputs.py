"""Create file 'input.julia' of inputs to be used in Julia.py

Constants (all sequences):
  n -- each subimage is n*n pixels
  split -- full image is split*split subimages stitched together
  iters -- number of times iterative function is applied
  frameCount -- number of frames in sequence of images
  c** -- initial complex constant used in iterative function (except Radial)
  r -- half of width of full image in complex plane (except Zoom)

Inputs (Linear):
  path -- length of straight path c follows in complex plane
  cEnd** -- final c value of path

Inputs (Radial):
  rad** -- radius of circular arc along which c values are taken
  angle -- starting angle of circular arc

Inputs (Zoom):
  center** -- center point of images in complex plane
  rStart -- half of width of smallest image in complex plane
  rEnd -- half of width of largest image in complex plane

**These constants may be altered as needed in Julia.py

"""

import random

import numpy as np

n = 256
split = 4
iters = 100
frameCount = 300
r = 1.5

# Favors picking Zoom over Linear over Radial
seqType = random.choice(['linear']*3 + ['radial']*2 + ['zoom']*4)

# Get c such that abs(c) <= 1
c = complex(1,1)
while abs(c) > 1:
    c = complex(random.uniform(-1,1), random.uniform(-1,1))

# Linear type inputs
path = 0.5
cEnd = complex(1,1)
while abs(cEnd) > 1:
    angle = random.uniform(-np.pi,np.pi)
    cEnd = complex(c.real + path*np.cos(angle), c.imag + path*np.sin(angle))

# Radial type inputs
rad = random.uniform(0.25, 1)
angle = random.uniform(0, np.pi)

# Zoom type inputs
center = random.uniform(0, 1)*np.exp(1j*random.uniform(0, 2*np.pi))
rStart = 0.000001
rEnd = 1.50

with open("input.julia", "w") as out:
    out.write(' '.join(map(repr, [n, split, iters, frameCount,
                                  r, c.real, c.imag])) + '\n')
    out.write(' '.join(map(repr, [cEnd.real, cEnd.imag])) + '\n')
    out.write(' '.join(map(repr, [rad, angle])) + '\n')
    out.write(' '.join(map(repr, [center.real, center.imag,
                                  rStart, rEnd])) + '\n')
    out.write(seqType)
