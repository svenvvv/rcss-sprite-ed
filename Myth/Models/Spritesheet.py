
class SpritesheetError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class Spritesheet:
    requiredProps = [ "src" ]
    _sprites = []
    _props = []
    _basepath = None

    def __init__(self, css):
        self._name = css.name
        self._sprites = css.declarations
        self._props = css.props

        for p in self.requiredProps:
            if not p in self._props:
                raise SpritesheetError(f"Missing required property: {p}")

    def setBasepath(self, path):
        self._basepath = path

    def basepath(self):
        return self._basepath

    def resolution(self):
        return self._props["resolution"]

    def setResolution(self, res):
        self._props["resolution"] = res

    def source(self):
        return self._props["src"]

    def sourceLongPath(self):
        return f"{self.basepath()}/{self.source()}"

    def setSource(self, source):
        self._props["src"] = source

    def name(self):
        return self._name

    def sprites(self):
        return self._sprites

    def props(self):
        return self._props

    def serialize(self):
        ret = f"@spritesheet {self._name}\n"
        ret += "{\n"

        ret += f"\t/* Path: {self.sourceLongPath()} */\n"
        ret += f"\tsrc: {self._props['src']};\n"

        if self._props["resolution"]:
            ret += f"\tresolution: {self._props['resolution']}x;\n"

        ret += "\n"

        for s in self._sprites:
            ret += f"\t{s.toRCSS()}\n"

        ret += "}\n"

        return ret
