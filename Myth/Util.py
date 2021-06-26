import functools
from PySide2.QtGui import QImageReader, QImageWriter

VERSION = "1.0"

def supportedImageFormats(fmts, aggregate):
    ret = None
    print(fmts)
    if aggregate:
        ret = functools.reduce(lambda a, v: a + f" *.{str(v, 'utf8').lower()}",
                               fmts, "All supported formats (") + ")"
    else:
        def fn(agg, raw):
            v = str(raw, "utf8")
            return agg + f"{v.upper()} image (*.{v.lower()});;"

        ret = functools.reduce(fn, fmts, "")
        # NOTE: semicolons left over from reduce()
        # NOTE: if changing this string then change supportedImageFormatToExt()
        ret += "All files (*.*)"

    return ret

@functools.cache
def supportedImageReadFormats(aggregate=False):
    fmts = QImageReader.supportedImageFormats()
    return supportedImageFormats(fmts, aggregate)

@functools.cache
def supportedImageWriteFormats(aggregate=False):
    fmts = QImageWriter.supportedImageFormats()
    return supportedImageFormats(fmts, aggregate)

def supportedImageFormatToExt(longFmt):
    space = longFmt.index(" ")
    fmt = longFmt[:space].lower()

    if fmt == "all":
        return None
    return fmt.lower()
