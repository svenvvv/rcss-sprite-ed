# RCSS Spritesheet Editor

A little editor for spritesheets contained in 
[RmlUi](https://github.com/mikke89/RmlUi) stylesheets.
Requires Python and Qt5.

Features:

* Create new sprites (mouse drawing),
* Delete sprites,
* Modify existing sprites (redraw using mouse or enter values),
* Replace source image (spritesheet `src` attribute),
* Undo/redo.

![Screenshot](./img/rcss-ed-1.png)

If you encounter any bugs then please create an 
[issue](https://github.com/svenvvv/rcss-sprite-ed/issues).

## Documentation

See [the manual](./MANUAL.md)

## Setting up

Install the requirements.

```
pip3 install -r requirements.txt
```

Run the program.

```
./main.py
# or python3 main.py
```

## TODO

* Doesn't support "flipping" sprites (negative coordinates).

Loading stylesheets with flipped sprites is supported and during saving they
will be exported correctly, but as of now there is no way to flip created
sprites in the editor.

* Doesn't support saving into RCSS files.

Presently, when you click save, then the program will present you with text
which you can manually paste into your stylesheet.

* No support for creating new spritesheets.

It's required to provide an existing one from an RCSS file.

* No support for stylesheets containing multiple spritesheets.

The loader code does support multiple, but at the moment it's hardcoded to exit
without prejudice :).
If you wish to extend it then see `loadStylesheet()` in `MainWindow.py`.

* Bugs, probably.

Haven't had a chance to work on my UI, as I was writing this tool instead :).

