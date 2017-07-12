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

**May be altered as needed in Julia.py

"""

import random
import json

import numpy as np

n = 256
split = 4
iters = 150
frameCount = 300
r = 1.5
p = random.choice([2]*10 + [3]*5 + [4]*3 + [5]*2)

# Favors picking Zoom over Linear over Radial
seqType = random.choice(['linear']*3 
                      + ['radial']*2 
                      + ['zoom']*4
                      + ['power']*1)

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

# Power type inputs
pMin = 2
pMax = 3


data = {"n": n,
        "split": split,
        "iters": iters,
        "frameCount": frameCount,
        "r": r,
        "p": p,
        "seqType": seqType,
        "c": (c.real, c.imag),
        "linear": {"cEnd": (cEnd.real, cEnd.imag)},
        "radial": {"rad": rad, "angle": angle},
        "zoom": {"center": (center.real, center.imag),
                 "rStart": rStart, "rEnd": rEnd},
        "power": {"pMin": pMin, "pMax": pMax}
       }

with open("input.json", "w") as out:
    json.dump(data, out, indent=1)
