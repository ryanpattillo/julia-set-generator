"""Create sequence of images based on inputs from 'input.julia'.

For descriptions of constants & inputs, see JuliaInputs.py.

Sequence types:
  Linear -- Every frame shows a fixed region of the complex plane
             centered at the origin. Each successive frame is made by moving
             c along a straight line in the complex plane.
  Radial -- Every frame shows a fixed region of the complex plane
             centered at the origin. Each successive frame is made by moving
             c along a circular arc centered at the origin.
  Zoom -- Every frame shows the same Julia fractal, i.e. `c` is not changed.
           The center of each image is also constant, but it may be centered 
           anywhere in the plane. Each successive frame shows a slightly 
           smaller or larger region of the complex plane to give 
           a zooming effect.

Each sequence type adjusts its starting and/or ending c values so
 that they are 'interesting' -  this means that the fractal created 
 by c is not an entirely black image.

String to be tweeted is written to 'output.julia'.
"""

import timeit
import itertools

import numpy as np
from pathos.multiprocessing import ProcessingPool as Pool

import JuliaTools

start = timeit.default_timer()

# Read constants from input.julia
with open('input.julia','r') as inFile:
    inputs = inFile.readlines()

line = inputs[0].split()
n, split, iters, frameCount = map(int, line[0:4])
r, c = float(line[4]), complex(float(line[5]), float(line[6]))
seqType = inputs[4]

# List of coordinates of subimages inside the full image
coords = list(itertools.product(range(split), range(split)))


def makeLinear():
    global c
    line = inputs[1].split()
    cEnd = complex(float(line[0]), float(line[1]))

    pool = Pool(4)

    # Get interesting starting c
    while True:
        subIm = JuliaTools.subImage(c=c,
                                    r=r,
                                    n=10,
                                    iters=iters,
                                    split=split,
                                    save=False)
        isBlackList = pool.map(subIm, coords)
        if not all(isBlackList):
            break
        else:
            c *= 0.975

    # Get interesting cEnd
    while True:
        subIm = JuliaTools.subImage(c=cEnd,
                                    r=r,
                                    n=10,
                                    iters=iters,
                                    split=split,
                                    save=False)
        isBlackList = pool.map(subIm, coords)
        if not all(isBlackList):
            break
        else:
            cEnd *= 0.975

    # Straight line c follows in complex plane
    cPath = np.linspace(c, cEnd, frameCount)

    for frame in range(frameCount):    
        subIm = JuliaTools.subImage(c=cPath[frame],
                                    r=r,
                                    n=n,
                                    iters=iters,
                                    split=split)
        isBlackList = pool.map(subIm, coords)
        allBlack = all(isBlackList)
        
        if not allBlack:
            JuliaTools.makeFrame(frame, n, split, coords)
    
    pool.close()
 
    JuliaTools.prepareForFFmpeg(frameCount=frameCount, loop=True)       

    # Write tweet string
    s1 = '+' if c.imag >= 0 else '-'
    s2 = '+' if cEnd.imag >= 0 else '-'
    with open("output.julia","w") as out:
        out.write("Images generated using constants"
                  " on a straight path from {:03.2f} {} {:03.2f}i"
                  " to {:03.2f} {} {:03.2f}i."
                  .format(c.real, s1, abs(c.imag), 
                          cEnd.real, s2, abs(cEnd.imag)))

    stop = timeit.default_timer()
    
    print stop - start


def makeRadial():
    line = inputs[2].split()
    rad, angle = float(line[0]), float(line[1])
    args = np.linspace(angle, angle + np.pi, frameCount)

    pool = Pool(4)

    while True:
        subIm = JuliaTools.subImage(c=rad*np.exp(1j*angle),
                                    r=r,
                                    n=10,
                                    iters=iters,
                                    split=split,
                                    save=False)
        isBlackList = pool.map(subIm, coords)
        if not all(isBlackList):
            break
        else:
            rad *= 0.975

    # Circular arc c follows in complex plane
    cPath = rad*np.exp(1j*args)

    for frame in range(frameCount):
        subIm = JuliaTools.subImage(c=cPath[frame],
                                    r=r,
                                    n=n,
                                    iters=iters,
                                    split=split)
        isBlackList = pool.map(subIm, coords)
        allBlack = all(isBlackList)
        
        if not allBlack:
            JuliaTools.makeFrame(frame, n, split, coords)
    
    pool.close()
        
    JuliaTools.prepareForFFmpeg(frameCount=frameCount, loop=True)

    with open("output.julia","w") as out:
        out.write("Images generated using constants"
                  " on a circular arc of radius {:03.2f}."
                  .format(rad))

    stop = timeit.default_timer()
    
    print stop - start


def makeZoom():
    global c
    line = inputs[3].split()
    center = complex(float(line[0]), float(line[1]))
    rStart, rEnd = float(line[2]), float(line[3])
    h = 0.25

    pool = Pool(4)
    
    # Get interesting c
    while True:
        subIm = JuliaTools.subImage(c=c,
                                    r=rStart,
                                    n=10,
                                    iters=iters,
                                    split=split,
                                    save=False)
        isBlackList = pool.map(subIm, coords)
        if not all(isBlackList):
            break
        else:
            c *= 0.975
    
    # Get interesting center (not entirely black or color)
    decreased, increased = False, False
    while True:
        subIm = JuliaTools.subImage(c=c,
                                    r=0.25*rStart,
                                    n=10,
                                    iters=iters,
                                    split=split,
                                    center=center,
                                    save=False)
        isBlackList = pool.map(subIm, coords)
        someBlack = any(isBlackList)
        someColor = not all(isBlackList)
        if someBlack and someColor:
            break
        elif not someColor:
            center *= 1 - h
            decreased = True
        else:
            center *= 1 + h
            increased = True
        if increased and decreased:
            h *= 0.5
            increased, decreased = False, False

    # Ensures frame size is changed at consant proportion
    factor = (rEnd/rStart)**(1.0/float(frameCount))
    for frame in range(frameCount):
        subIm = JuliaTools.subImage(c=c,
                                    r=rStart,
                                    n=n,
                                    iters=iters,
                                    split=split,
                                    center=center)
        pool.map(subIm, coords)
        JuliaTools.makeFrame(frame, n, split, coords)
        rStart *= factor
            
    pool.close()

    JuliaTools.prepareForFFmpeg(frameCount=frameCount, loop=True)

    s1 = '+' if c.imag >= 0 else '-'
    s2 = '+' if center.imag >= 0 else '-'
    with open("output.julia","w") as out:
        out.write("Image generated using c = {:03.2f} {} {:03.2f}i"
                  " centered at the point {:03.2f} {} {:03.2f}i."
                  .format(c.real, s1, abs(c.imag), 
                          center.real, s2, abs(center.imag)))
    
    stop = timeit.default_timer()
    
    print stop - start


if __name__ == "__main__":
    if seqType == 'linear':
        makeLinear()
    elif seqType == 'radial':
        makeRadial()
    elif seqType == 'zoom':
        makeZoom()