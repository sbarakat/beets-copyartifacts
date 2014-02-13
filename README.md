# copyartifacts plugin for beets

This is a simple plugin that copies all files, that don't get imported by beets, into the library directory.

## Installing

**Warning**: This code is very experimental - USE AT YOUR OWN RISK!

Installation of the plugin can be done using these commands:

    git clone https://github.com/sbarakat/beets-copyartifacts.git
    cd beets-copyartifacts
    python setup.py install

If you get permission errors try running it with `sudo`

You will then need to enable the plugin in beets' config.yaml

    plugins: copyartifacts

## License

Copyright (c) 2014 Sami Barakat
Licensed under the [MIT license](https://github.com/sbarakat/beets-copyartifacts/blob/master/MIT-LICENSE.txt).

