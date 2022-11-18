# -*- coding: utf-8 -*-

import mutagen
import mutagen.flac

unknown_str = "[unknown]"

def get(tags, tag, default):

    try:
        t = tags[tag]
    except KeyError:
        return default

    return t[0]


def read(file):
    mdata = { }

    tags = None
    try:
        tags = mutagen.flac.FLAC(file)
    except mutagen.flac.HeaderNotFoundError:
        print("Cannot read metadata from file %s" % file.encode('utf-8'))
        return None

    mdata['duration'] = int(tags.info.length * 1000)
    mdata['artist'] = get(tags, 'artist', unknown_str)
    mdata['sortname'] = get(tags, 'artistsort', mdata['artist'])
    mdata['release'] = get(tags, 'album', unknown_str)
    mdata['recording'] = get(tags, 'title', unknown_str)
    mdata['year'] = int(get(tags, 'originalyear', "0"))
    mdata['tnum'] = int(get(tags, 'tracknumber', "0"))

    return mdata
