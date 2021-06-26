# RCSS Spritesheet Editor

A little editor for spritesheets contained in 
[RmlUi](https://github.com/mikke89/RmlUi) stylesheets.
Requires Python and Qt5.

Features:

* Create new sprites (mouse drawing),
* Pack images from folders into RCSS spritesheets,
* Delete sprites,
* Modify existing sprites (redraw using mouse or enter values),
* Replace source image (spritesheet `src` attribute),
* Save into RCSS files,
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

