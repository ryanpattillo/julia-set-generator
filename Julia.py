"""
Constants:
    n -- n*n pixels in each subimage
    split -- split*split subimages in each frame
    frameCount -- number of frames in final gif
    iters -- number of time function is iterated
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
gifType = inputs[4]

coords = list(itertools.product(range(split), range(split)))


def makeLinearGif():
    global c
    line = inputs[1].split()
    cEnd = complex(float(line[0]), float(line[1]))

    pool = Pool(4)

    # Get suitable starting c
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

    s1 = '+' if c.imag >= 0 else '-'
    s2 = '+' if cEnd.imag >= 0 else '-'
    with open("output.julia","w") as out:
        out.write("""Images generated using constants on a straight path from {:03.2f} {} {:03.2f}i to {:03.2f} {} {:03.2f}i.""".format(c.real, s1, abs(c.imag), cEnd.real, s2, abs(cEnd.imag)))
#        out.write(' '.join(map(repr, [n*split, iters, frameCount, r])) + '\n')
#        out.write('linear\n')
#        out.write(' '.join(map(repr, [c.real, c.imag, cEnd.real, cEnd.imag])))

    stop = timeit.default_timer()
    
    print stop - start


def makeRadialGif():
    line = inputs[2].split()
    rad, angle = float(line[0]), float(line[1])
    args = np.linspace(angle, angle + np.pi, frameCount)

    pool = Pool(4)

    # Get suitable radius
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
#    JuliaTools.makeGif(frameCount=frameCount)

    with open("output.julia","w") as out:
        out.write("""Images generated using constants on a circular arc of radius {:03.2f}.""".format(rad))
#        out.write(' '.join(map(repr, [n*split, iters, frameCount, r])) + '\n')
#        out.write('radial\n')
#        out.write(repr(rad))

    stop = timeit.default_timer()
    
    print stop - start


def makeZoomGif():
    global c
    line = inputs[3].split()
    center = complex(float(line[0]), float(line[1]))
    rStart, rEnd = float(line[2]), float(line[3])
    h = 0.25

    pool = Pool(4)
    
    counter = 0
    while True:
        subIm = JuliaTools.subImage(c=c,
                                    r=rStart,
                                    n=10,
                                    iters=50,
                                    split=split,
                                    save=False)
        isBlackList = pool.map(subIm, coords)
        if not all(isBlackList):
            break
        else:
            counter += 1
            c *= 0.975

    print 'appropriate c found after', counter, 'attempts'
    
    counter = 0
    decreased, increased = False, False
    while True:
        subIm = JuliaTools.subImage(c=c,
                                    r=0.25*rStart,
                                    n=10,
                                    iters=50,
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
            h /= 2.0
            increased, decreased = False, False
        counter += 1

    print 'Center point found after', counter, 'attempts'
    
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
#    JuliaTools.makeGif(frameCount=frameCount, reverse=True)

    s1 = '+' if c.imag >= 0 else '-'
    s2 = '+' if center.imag >= 0 else '-'
    with open("output.julia","w") as out:
        out.write("""Image generated using c = {:03.2f} {} {:03.2f}i centered at the point {:03.2f} {} {:03.2f}i.""".format(c.real, s1, abs(c.imag), center.real, s2, abs(center.imag)))
#        out.write(' '.join(map(repr, [n*split, iters, frameCount, r])) + '\n')
#        out.write('zoom\n')
#        out.write(' '.join(map(repr, 
#                               [c.real, c.imag, center.real, center.imag])))
    
    stop = timeit.default_timer()
    
    print stop - start


if __name__ == "__main__":
    if gifType == 'linear':
        makeLinearGif()
    elif gifType == 'radial':
        makeRadialGif()
    elif gifType == 'zoom':
        makeZoomGif()
