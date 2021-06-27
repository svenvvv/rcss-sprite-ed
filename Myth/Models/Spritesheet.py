from Myth.Models.Property import Property


class SpritesheetError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class Spritesheet:
    def __init__(self, basepath, linerange, name, sprites, src="none", resolution=None):
        self._name = name
        self._sprites = sprites
        self._basepath = basepath
        self._linerange = linerange

        self._src = src
        self._resolution = resolution

        self._properties = [
            Property("Name", self.name, self.setName, str),
            Property("Source image", self.source, self.setSource, str),
            Property("Resolution", self.resolution, self.setResolution, float),
        ]

    def basepath(self):
        return self._basepath

    def setBasepath(self, path):
        self._basepath = path

    def linerange(self):
        return self._linerange

    def setLinerange(self, range):
        self._linerange = range

    def resolution(self):
        return self._resolution

    def setResolution(self, res):
        self._resolution = res

    def source(self):
        return self._src

    def sourceLongPath(self):
        return f"{self.basepath()}/{self.source()}"

    def setSource(self, source):
        self._src = source

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def sprites(self):
        return self._sprites

    def serialize(self):
        ret = f"@spritesheet {self._name}\n"
        ret += "{\n"

        ret += f"\t/* Path: {self.sourceLongPath()} */\n"
        ret += f"\tsrc: {self._src};\n"

        if self._resolution:
            ret += f"\tresolution: {self._resolution}x;\n"

        ret += "\n"

        for s in self._sprites:
            ret += f"\t{s.toRCSS()}\n"

        ret += "}\n"

        return ret
