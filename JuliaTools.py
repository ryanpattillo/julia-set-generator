"""Functions to be used in Julia.py to create sequences of images."""

import os

import numpy as np
import numexpr as ne
from PIL import Image


def f(arr, c, p):
    """Return arr with iterative function arr = arr**2 + c applied to it"""
#    arr = ne.evaluate("arr**p + c")
#    arr[ne.evaluate("real(abs(arr))>2")] = np.inf
#    return arr
    return ne.evaluate("arr**p + c")

    
def toGrayScale(arr):
    """Return an array of grayscale values, 0 to 255, of type np.uint8.

    If an element z of arr is NaN or abs(z) > 2, it is mapped to 0.
    Otherwise, it is mapped to 127.999*abs(z).
    """
    arr = np.nan_to_num(ne.evaluate("real(abs(arr))*127.999"))
    arr[ne.evaluate("arr > 255.999")] = 0
    return arr.astype(np.uint8)

    
def toRGB(arr, escape, iters):
    """Return an array of RGB values, each 0 to 255, of type np.uint8.

    If an element z of arr is NaN or abs(z) > 2, it is mapped to 0,0,0.
    Otherwise, it is mapped to an RGB value based on abs(z) and arg(z).
    """
    pi = np.pi
    n = arr.shape[0]
    rgb = np.zeros((n,n,3))

    # isValid is a boolean filter to determine which entries
    #   are not in the interior of the fractal
    isFinite = np.isfinite(arr)
    isSmall = np.nan_to_num(ne.evaluate("real(abs(arr))"))<=2
    isValid = np.logical_and(isFinite, isSmall)
    
    arr = np.nan_to_num(arr)
    arr[ne.evaluate("real(abs(arr))>2")] = 0
    args = np.angle(arr)
    a = ne.evaluate("real(abs(arr))")
    iters = float(iters)

    r = ne.evaluate("(1 - a*(0.5 - 0.25*(1 + cos(args))))"
                    " *255.999*isValid"
                    " + 175*escape/iters*(escape>0)")
    g = ne.evaluate("(1 - a*(0.5 - 0.25*(1 + cos(args - 0.666*pi))))"
                    " *255.999*isValid"
                    " + 175*escape/iters*(escape>0)")
    b = ne.evaluate("(1 - a*(0.5 - 0.25*(1 + cos(args - 1.333*pi))))"
                    " *255.999*isValid"
                    " + 175*escape/iters*(escape>0)")

    rgb[...,0], rgb[...,1], rgb[...,2] = r, g, b

    return rgb.astype(np.uint8)

def subImage(c, r, n, iters, split, p, 
             center=complex(0,0), save=True, aura=True):
    """Make a subimage of the full frame.

    Arguments:
    center -- center of full image in complex plane (default origin)
    save -- save subimage to disk (if not black) (default True)
    aura -- shading of outside points on escape time (default True)
    """
    def nested(coords):
        """Return True if image is black, False otherwise."""
        i, j = coords[0], coords[1]

        # real & imag subimage bounds in complex plane
        reMin, reMax = center.real - r, center.real + r
        imMin, imMax = center.imag - r, center.imag + r
        reL = reMin + i*(reMax-reMin)/float(split)
        reR = reMin + (i+1)*(reMax-reMin)/float(split)
        imL = imMin + j*(imMax-imMin)/float(split)
        imR = imMin + (j+1)*(imMax-imMin)/float(split)
        
        # create grid of complex numbers to be iterated on
        re = np.linspace(reL, reR, n, dtype=np.complex_)
        im = 1j*np.flip(np.vstack(
                        np.linspace(imL, imR, n, dtype=np.complex_)), 0)
        grid = re + im

        testCounts = set([int(0.1*k*iters) for k in range(1,10)])
        escape = np.zeros((n,n))
        # apply iterative function
        for k in xrange(iters):
            grid = f(grid, c, p)
            #grid = ne.evaluate("grid**p + c")
            grid[ne.evaluate("real(abs(grid))>2")] = np.inf
            if aura:
                escape = ne.evaluate("escape + (k+1)"
                                     "*(real(abs(grid))>2)*(escape==0)")
                if k in testCounts and np.all(escape):
                    break
            elif k in testCounts and not np.any(toGrayScale(grid)):
                    return True

        if save:
            img = Image.fromarray(toRGB(grid, escape, iters), 'RGB')
            img.save("images/image_" + str(i) + "_" + str(split-j-1) + ".png")
        return False
    return nested


def makeFrame(num, n, split, coordList):
    """Create full frame from subimages and write to disk.

    Arguments:
    num -- index of frame
    coordList -- list of tuples specifying positions of subimages
    """
    frame = Image.new('RGB', (n*split, n*split))
    for tup in coordList:
        x, y = tup[0], tup[1]
        imstr = "images/image_" + str(x) + "_" + str(y) + ".png"
        # if imstr exists, paste it in proper position in frame
        try:
            img = Image.open(imstr)
            frame.paste(img, (x*n, y*n))
            os.remove(imstr)
        # if imstr does not exist, do nothing; region in frame will be black
        except IOError:
            pass
    frame.save("images/frame" + str(num) + ".png")


def prepareForFFmpeg(frameCount, reverse=False, loop=False):
    """Make framelist.txt, a file which specifies order of frames for FFmpeg.

    Arguments:
    reverse -- frames are ordered from last to first (default False)
    loop -- frames are ordered first to last to first (default False)
    """
    with open('framelist.txt', 'w') as flist:
        # writes sequence of frames in order of creation
        if loop or not reverse:
            # pause on first frame
            for _ in xrange(20):
                flist.write("file 'images/frame0.png'\n")
            for frame in xrange(frameCount):
                framestr = "images/frame" + str(frame) + ".png"
                if os.path.isfile(framestr):
                    flist.write("file '" + framestr + "'\n")
                    last = framestr
            # pause on middle/last frame
            for _ in xrange(10):
                flist.write("file '" + last + "'\n")
        # writes sequence of frames in reverse order of creation
        if loop or reverse:
            # pause on first/middle frame
            for _ in xrange(10):
                flist.write("file 'images/frame" 
                            + str(frameCount-1) + ".png'\n")
            for frame in reversed(range(frameCount)):
                framestr = "images/frame" + str(frame) + ".png"
                if os.path.isfile(framestr):
                    flist.write("file '" + framestr + "'\n")
            # pause on last frame
            for _ in xrange(20):
                flist.write("file '" + framestr + "'\n")

