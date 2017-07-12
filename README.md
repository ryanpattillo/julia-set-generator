# Julia Set Generator

This code creates sequences of images of 
[Julia sets](http://www.karlsims.com/julia.html) by iterating complex 
numbers through the function *f(z) = z^p + c* for complex constants *c*
and (usually) integer exponents *p*.
Images are RGB `.png` files and can be combined to form animations.

## Requirements

These scripts are run in Python 2.7.9. 
The following third-party packages are used:

* `numpy` - efficient array operations with complex numbers
* [`numexpr`](https://github.com/pydata/numexpr) - optimizes `numpy` array 
operations
* `PIL.Image` - creates images from `numpy` arrays and saves them to disk
* [`pathos`](https://github.com/uqfoundation/pathos) - allows for 
multiprocessing to be used in `Julia.py` with `JuliaTools.py` 
imported as a module

## Running the scripts

First, run `JuliaInputs.py`. This creates the file
`input.json` which contains all of the constants that are read into
`Julia.py`. You can now run `Julia.py`, which imports
`JuliaTools.py` as a module. The sequence of Julia 
fractals will be written to `images/`.

## Output

There are three types of image sequences that `Julia.py` can create.

* Linear - Every frame shows a fixed region of the complex plane 
centered at the origin. Each successive frame is made by moving 
*c* along a straight line in the complex plane.
([Example](https://twitter.com/JuliaFractalBot/status/883609555418087425))
* Radial - Every frame shows a fixed region of the complex plane
centered at the origin. Each successive frame is made by moving 
*c* along a circular arc centered at the origin.
([Example](https://twitter.com/JuliaFractalBot/status/882560744625254401))
* Zoom - Every frame shows the same Julia fractal, i.e. *c* is not changed.
The center of each image is also constant, but it may be centered anywhere
in the plane. Each successive frame shows a slightly smaller or larger 
region of the complex plane to give a zooming effect. 
([Example](https://twitter.com/JuliaFractalBot/status/883642095684210688))
* Power - Every frame shows a fixed region of the complex plane centered 
at the origin, and *c* is fixed. The exponent *p* in *f(z) = z^p + c* is 
changed in each frame, usually taking on fractional values.

## Twitter Bot

This code is being used by the twitter bot 
[@JuliaFractalBot](https://twitter.com/JuliaFractalBot) to generate and
tweet videos of Julia fractals. A sequence of images produced by `Julia.py`
is converted to a `.mp4` video compatible with Twitter using 
[`ffmpeg`](https://github.com/FFmpeg/FFmpeg):
```bash
ffmpeg -r 30 -f concat -i framelist.txt -vcodec libx264 -crf 12 -pix_fmt yuv420p -s 1024:1024 -aspect 1:1 JuliaVid.mp4
```
The video file is then asynchronously uploaded to Twitter using
[large-video-upload-python](https://github.com/twitterdev/large-video-upload-python/).
One can also create an animated `.gif` from the images:
```bash
ffmpeg -r 10 -f concat -i framelist.txt JuliaGif.gif
```
This bot uses `.mp4`s over `.gif`s because Twitter's file size limit for 
videos is 512MB, while it is only 15MB for animated `.gif`s.
