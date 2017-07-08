"""Functions to be used in Julia.py to create sequences of images."""

import os

import numpy as np
import numexpr as ne
from PIL import Image
import imageio


def f(arr, c):
    """Return arr with iterative function arr = arr**2 + c applied to it"""
    arr = ne.evaluate("arr**2 + c")
    arr[ne.evaluate("real(abs(arr))>2")] = np.inf
    return arr

    
def toGrayScale(arr):
    """Return an array of grayscale values, 0 to 255, of type np.uint8.

    If an element z of arr is NaN or abs(z) > 2, it is mapped to 0.
    Otherwise, it is mapped to 127.999*abs(z).
    """
    arr = np.nan_to_num(ne.evaluate("real(abs(arr))*127.999"))
    arr[ne.evaluate("arr > 255.999")] = 0
    return arr.astype(np.uint8)

    
def toRGB(arr):
    """Return an array of RGB values, each 0 to 255, of type np.uint8.

    If an element z of arr is NaN or abs(z) > 2, it is mapped to 0,0,0.
    Otherwise, it is mapped to an RGB value based on abs(z) and arg(z).
    """
    pi = np.pi
    n = arr.shape[0]
    rgb = np.zeros((n,n,3))

    # isValid is a boolean filter to determine which elements should be 0
    isFinite = np.isfinite(arr)
    isSmall = np.nan_to_num(ne.evaluate("real(abs(arr))"))<=2
    isValid = np.logical_and(isFinite, isSmall)

    arr = np.nan_to_num(arr)
    arr[ne.evaluate("real(abs(arr))>2")] = 0
    args = np.angle(arr)
    a = ne.evaluate("real(abs(arr))")
    r = ne.evaluate("(a*(0.25*(cos(args)+1)-0.5)+1)*255.999*isValid")
    g = ne.evaluate("(a*(0.25*(cos(args-0.666*pi)+1)-0.5)+1)*255.999*isValid")
    b = ne.evaluate("(a*(0.25*(cos(args-1.333*pi)+1)-0.5)+1)*255.999*isValid")
    rgb[...,0], rgb[...,1], rgb[...,2] = r, g, b
    return rgb.astype(np.uint8)
 

def subImage(c, r, n, iters, split, center=complex(0,0), save=True):
    """Make a subimage of the full frame.

    Arguments:
    center -- center of full image in complex plane (default origin)
    save -- save subimage to disk (if not black) (default True)
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
        
        # apply iterative function
        for k in xrange(iters):
            grid = f(grid, c)
            # check if image is black; break and return True if so
            if k in {5, 10, 25, 50, iters-1}:
                if not np.any(toGrayScale(grid)):
                    return True
        
        if save:
            img = Image.fromarray(toRGB(grid), 'RGB')
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


def makeGif(frameCount, reverse=False, loop=False, 
            blackFrames=False, duration=0.075):
    """.

    """
    with imageio.get_writer("JuliaGif.gif", mode="I", duration=duration) as gif:
        if loop or not reverse:
            for frame in range(frameCount):
                framestr = "images/frame" + str(frame) + ".png"
                try:
                    img = imageio.imread(framestr)
                    gif.append_data(img)
                except IOError:
                    pass
        if loop or reverse:
            for frame in reversed(range(frameCount)):
                framestr = "images/frame" + str(frame) + ".png"
                try:
                    img = imageio.imread(framestr)
                    gif.append_data(img)
                except IOError:
                    pass


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
            for i in range(20):
                flist.write("file 'images/frame0.png'\n")
            for frame in range(frameCount):
                framestr = "images/frame" + str(frame) + ".png"
                if os.path.isfile(framestr):
                    flist.write("file '" + framestr + "'\n")
                    last = framestr
            # pause on middle/last frame
            for i in range(10):
                flist.write("file '" + last + "'\n")
        # writes sequence of frames in reverse order of creation
        if loop or reverse:
            # pause on first/middle frame
            for i in range(10):
                flist.write("file 'images/frame" 
                            + str(frameCount-1) + ".png'\n")
            for frame in reversed(range(frameCount)):
                framestr = "images/frame" + str(frame) + ".png"
                if os.path.isfile(framestr):
                    flist.write("file '" + framestr + "'\n")
            # pause on last frame
            for i in range(20):
                flist.write("file '" + framestr + "'\n")

