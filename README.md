# copyartifacts plugin for beets

A plugin that moves non-music files during the import process.

This is a plugin for [beets](http://beets.radbox.org/): a music library manager and much more.

## Warning

This code is very experimental - USE AT YOUR OWN RISK!

## Installing

Installation of the plugin can be done using these commands:

    git clone https://github.com/sbarakat/beets-copyartifacts.git
    cd beets-copyartifacts
    python setup.py install

If you get permission errors try running it with `sudo`

You will then need to enable the plugin in beets' config.yaml

    plugins: copyartifacts

## Configuration

It can copy files by file extenstion:

    copyartifacts:
        extensions: .cue .log

Or copy all non-music files (it does this by default):

    copyartifacts:
        extensions: .*

It can also print what got left:

    copyartifacts:
        print_ignored: yes

## License

Copyright (c) 2014 Sami Barakat

Licensed under the [MIT license](https://github.com/sbarakat/beets-copyartifacts/blob/master/MIT-LICENSE.txt).

