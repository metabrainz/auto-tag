#!/usr/bin/env python3
import os
import sys
from collections import defaultdict

import click
import requests
from scan import ScanCollection
import musicbrainzngs


class AutoTagger():

    def __init__(self):
        self.releases = {}

    def map_collection(self, collection):

        sys.stdout.flush()
        batch_size = 50
        results = []
        unidentified = []
        index = 0
        while True:
            batch = collection[index:index + batch_size]
            if len(batch) == 0:
                break
            sys.stdout.flush()

            post_data = [{"[artist_credit_name]": r["artist"], "[recording_name]": r["recording"]} for r in batch]
            r = requests.post("https://labs.api.listenbrainz.org/mbid-mapping/json", json=post_data)
            if r.status_code != 200:
                print("Could not map tracks: %d (%s)" % (r.status_code, r.text))
                return None, None

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

    def load_releases(self, recording_mbids):

        sys.stdout.flush()
        batch_size = 20
        index = 0
        while True:
            batch = recording_mbids[index:index + batch_size]
            if len(batch) == 0:
                break

            post_data = [{"[recording_mbid]": r["mapped"]["recording_mbid"]} for r in batch]
            r = requests.post("https://datasets.listenbrainz.org/releases-from-recordings/json", json=post_data)
            if r.status_code != 200:
                print("Could not load releases tracks: %d (%s)" % (r.status_code, r.text))
                return

            for result in r.json():
                if result["release_mbid"] not in self.releases:
                    self.releases[result["release_mbid"]] = result

            index += batch_size

    def load_recordings_into_releases(self, recordings):

        release_index = defaultdict(list)
        for release_mbid in self.releases:
            release = self.releases[release_mbid]
            for tnum, recording in enumerate(release["release"]):
                release_index[recording["recording_mbid"]].append((release, tnum))

        for recording in recordings:
            recording_mbid = recording["mapped"]["recording_mbid"]
            for release, tnum in release_index[recording_mbid]:
                rel_recording = release["release"][tnum]
                if "files" not in rel_recording:
                    rel_recording["files"] = []
                rel_recording["files"].append(recording["file_name"])

        stats = []
        for release_mbid in self.releases:
            total = 0
            file_count = 0
            for recording in self.releases[release_mbid]["release"]:
                if "files" in recording:
                    file_count += 1
                total += 1

            if file_count == 1:
                continue

            stats.append({
                "release": self.releases[release_mbid],
                "file_count": file_count,
                "total": total,
                "match": file_count / total,
                "release": self.releases[release_mbid]
            })

        last_rg = ""
        group = []
        for entry in sorted(stats, key=lambda i: (i["release"]["release_group_mbid"], i["release"]["release_mbid"], i["match"])):
            if last_rg != entry["release"]["release_group_mbid"]:
                self.evaluate_match(group)
                group = []

            group.append(entry)
            last_rg = entry["release"]["release_group_mbid"]

        if len(group) != 0:
            self.evaluate_match(group)

    def evaluate_match(self, release_candidates):

        release_candidates.sort(key=lambda i: i["release"]["release_group_mbid"])

        # Check for perfect matches
        for i, c in enumerate(release_candidates):
            #print("%s %-30s %d %d %d%%" % (c["release"]["release_group_mbid"], c["release"]["release_name"][:29], c["file_count"],
            #                               c["total"], int(c["match"] * 100)))
            if c["file_count"] == c["total"]:
                print("FULL MATCH! (release group %s '%s')" %
                      (c["release"]["release_group_mbid"][:6], c["release"]["release_name"]))
                self.print_match(c)
                release_candidates.pop(i)
                return


#        print("")

# Check for partial matches
        max_value = 0
        max_index = None
        for index, c in enumerate(release_candidates):
            if c["file_count"] == c["total"]:
                continue

            if max_index is None:
                max_index = 0
                max_value = c["match"]

            if c["match"] > max_value:
                max_index = index
                max_value = c["match"]

            if max_value > .25:
                print("partial match! (release group %s '%s')" %
                      (c["release"]["release_group_mbid"][:6], c["release"]["release_name"]))
                self.print_match(release_candidates[max_index])
            return

    def print_match(self, release_candidate):
        for r in release_candidate["release"]["release"]:
            try:
                files = ",".join([os.path.basename(f) for f in r["files"]])
            except KeyError:
                files = ""
            print("%3d %3d %-40s %s" % (r["medium_position"], r["position"], r["recording_name"][:39], files))
        print("")


@click.command()
@click.argument('path')
def scan_collection(path):
    sc = ScanCollection(path)
    try:
        sc.scan()
    except Exception:
        raise
        return None

    
    print("Scan collection...")
    collection = sc.get_collection()

    at = AutoTagger()
    print("Map tracks...")
    mapped, unidentified = at.map_collection(collection)
    if mapped is None:
        print("unable to map tracks.")
        return

    #print("Unmapped: %d tracks, ignoring" % len(unidentified))
    #    for mdata in unidentified:
    #        print("   add %-31s %-31s" % (mdata["recording"][:30], mdata["artist"][:30]))
    #print("  Mapped: %d tracks" % len(mapped))

    print("Load releases...")
    at.load_releases(mapped)

    print("Examine matches...")
    at.load_recordings_into_releases(mapped)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    musicbrainzngs.set_useragent("autotag", "0.0.0", "rob@metabrainz.org")
    collection = scan_collection()
