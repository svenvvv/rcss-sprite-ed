import os
import PIL
from PIL.ImageQt import ImageQt

from Myth.Models.Sprite import Sprite

from PyTexturePacker import Packer
from PyTexturePacker.ImageRect import ImageRect


class PackerException(ValueError):
    def __init__(self, message):
        super().__init__(message)


class SpritePacker:
    """
    I couldn't find a maintained Python texture packer that would give
    it's output as anything but a file on disk.
    So we're marionetting the guts of PyTexturePacker in this class :)

    This is a bit of a hack and could be broken by updates to PyTexturePacker,
    as we're using "private" APIs here, but I don't feel like writing a new
    texture packer for no particular gain.
    """
    def __init__(self, spritePath, enterSubdirs=True):
        print(f"Loading sprites from {spritePath}")
        self._path = spritePath
        self._images, self._errors = self.loadFromDir(spritePath, enterSubdirs)

        if not len(self._images):
            raise PackerException("Could not read any images from the path")

    def images(self):
        return self._images

    def errors(self):
        return self._errors

    def loadFromDir(self, spritePath, enterSubdirs):
        images = []
        errors = []
        for root, dirs, files in os.walk(spritePath):
            for f in files:
                fullpath = os.path.join(root, f)

                print(f"Reading {fullpath}")

                try:
                    images.append(ImageRect(fullpath))
                except Exception as e:
                    errors.append(str(e))

                if not enterSubdirs:
                    break
        return images, errors

    def pathToId(self, path):
        return path.replace(os.sep, "-")

    def pack(self, bg_color=0, **kwargs):
        try:
            packer = Packer.create(**kwargs)
            # TODO: why is this an array??
            atlas = packer._pack(self._images)[0]
            packed = atlas.dump_image(bg_color)
            rmlSprites = []
            error = None

            for r in atlas.image_rect_list:
                # Slice off root folder and path separator
                p = r.image_path[len(self._path)+1:]
                p = os.path.splitext(p)[0]
                id = self.pathToId(p)
                print(f"Packed sprite {id} ({r.x}, {r.y}, {r.width}, {r.height})")
                rmlSprites.append(Sprite(id, r.x, r.y, r.width, r.height))

            if len(rmlSprites) != len(self._images):
                error = "Could not fit all sprites into the specified dimensions!"

            return ImageQt(packed), rmlSprites, error
        except ValueError as e:
            print(e)
            return None, None, str(e)
