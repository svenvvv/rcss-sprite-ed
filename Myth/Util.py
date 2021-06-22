import functools

# TODO: there IS a nice way to get this from PIL, but I couldn't get it to work
# (see PIL.features.pilinfo()), so it's all manual work for now..
imgFmts = [
    [ "PNG image (*.apng, *.png)",  "PNG" ],
    [ "BMP image (*.bmp)",          "BMP" ],
    [ "JPEG image (*.jpg *.jpeg)",  "JPG" ],
    [ "GIF image (*.gif)",          "GIF" ],
    [ "JPEG2000 image (*.j2c, *.j2k, *.jp2, *.jpc, *.jpf, *.jpx)", "JP2"],
    [ "TGA image (*.tga)",          "TGA" ]
]

def supportedImageFormatsList():
    return imgFmts

def supportedImageFormatsQt():
    l = functools.reduce(lambda a, v: a + ";;" + v[0], imgFmts, "")[2:]
    # Tack on all files for loading images without ext.
    # Exts are actually unneeded, as pillow detects the format from the header, so the whole
    # file ext code is mostly for convienience for the windows folks ;).
    l += ";;All files (*.*)"
    return l

def supportedImageFormatsQtAllInOne():
    return functools.reduce(lambda a, v: a + f" *.{v[1].lower()}", imgFmts, "Supported images (") + ")"

def supportedImageFormatFromQt(fmt):
    imgFmtEntry = list(filter(lambda v: v[0] == fmt, imgFmts))
    if len(imgFmtEntry) > 0:
        return imgFmtEntry[0][1]
    else:
        return None
