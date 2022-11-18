#!/usr/bin/env python3

import click
import requests
from scan import ScanCollection
import musicbrainzngs


def map_collection(collection):

    batch_size = 100
    results = []
    unidentified = []
    index = 0
    while True:
        batch = collection[index:index + batch_size]
        if len(batch) == 0:
            break

        post_data = [{"[artist_credit_name]": r["artist"], "[recording_name]": r["recording"]} for r in batch]
        print("Map %d tracks" % len(batch))
        r = requests.post("https://labs.api.listenbrainz.org/mbid-mapping/json", json=post_data)
        if r.status_code != 200:
            print("Could not map tracks: %d (%s)" % (r.status_code, r.text))
            return

        recording_index = {}
        for result in r.json():
            recording_index[result["index"]] = result

        for i, recording in enumerate(batch):
            if i not in recording_index:
                unidentified.append(recording)
                continue

            recording["mapped"] = recording_index[i]
            results.append(recording)

        index += batch_size

    return results, unidentified

boo = """
[

    {
        "artist_credit_arg": "u2",
        "artist_credit_id": 197,
        "artist_credit_name": "U2",
        "artist_mbids": "{a3cb23fc-acd3-4ce0-8f36-1e5aa6a18432}",
        "index": 0,
        "match_type": 4,
        "recording_arg": "sunday bloody sunday",
        "recording_mbid": "e95e5009-99b3-42d2-abdd-477967233b08",
        "recording_name": "Sunday Bloody Sunday",
        "release_mbid": "259eafd8-f34b-4292-ab0a-c00ac221253c",
        "release_name": "War",
        "year": 1983
    }

]
"""

def load_releases(recordings):
    release_mbids = set([ r["mapped"]["release_mbid"] for r in recordings ])

    releases = {}
    print("Load releases:")
    for release_mbid in release_mbids:
        print("  %s" % release_mbid)
        releases[release_mbid] = musicbrainzngs.get_release_by_id(release_mbid)

    return releases


@click.command()
@click.argument('path')
def scan_collection(path):
    sc = ScanCollection(path)
    try:
        sc.scan()
    except Exception:
        raise
        return None

    collection = sc.get_collection()
    mapped, unidentified = map_collection(collection)
    print("Unknown: %d items" % len(unidentified))
    for mdata in unidentified:
        print("   add %-31s %-31s" % (mdata["recording"][:30], mdata["artist"][:30]))

    print(" Mapped: %d items" % len(mapped))
    release = load_releases(mapped)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    musicbrainzngs.set_useragent("autotag", "0.0.0", "rob@metabrainz.org")
    collection = scan_collection()
