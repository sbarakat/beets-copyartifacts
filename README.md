# copyartifacts plugin for beets

A plugin that moves non-music files during the import process.

This is a plugin for [beets](http://beets.radbox.org/): a music library manager and much more.

## Warning

This code is very experimental. I'm learning how to use beets and its features
as I develop this. Please report any issues you may have and feel free to
contribute.

USE AT YOUR OWN RISK!!

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

### Renaming files

Renaming works in much the same way as beets [Path Formats](http://beets.readthedocs.org/en/v1.3.3/reference/pathformat.html)
with the following limitations:
- The fields available are `$artist`, `$albumartist`, `$album` and `$albumpath`.
- The full set of [built in functions](http://beets.readthedocs.org/en/v1.3.3/reference/pathformat.html#functions)
  are also supported, with the exception of `%aunique` - which will return an empty string.

Each template string uses a query syntax for each of the file extensions. For
example the following template string will be applied to `.log` files:

    paths:
        ext:log: $albumpath/$artist - $album

This will rename a log file to: `~/Music/Artist/2014 - Album/Artist - Album.log`

### Example config

```
plugins: copyartifacts

paths:
    default: $albumartist/$year - $album/$track - $title
    singleton: Singletons/$artist - $title
    ext:log: $albumpath/$artist - $album
    ext:cue: $albumpath/$artist - $album
    ext:jpg: $albumpath/cover

copyartifacts:
    extensions: .cue .log .jpg
    print_ignored: yes
```

## Roadmap

See [Milestones](https://github.com/sbarakat/beets-copyartifacts/issues/milestones)

## License

Copyright (c) 2014 Sami Barakat

Licensed under the [MIT license](https://github.com/sbarakat/beets-copyartifacts/blob/master/MIT-LICENSE.txt).

