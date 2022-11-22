# auto-tag

THIS IS A PROOF OF CONCEPT!

Introduction
============

This tool could be used as a new clustering tool for Picard. Using the MBID Mapping from ListenBrainz, it does the following:

- Scan you music collection (mp3 and flac supported), ignore any MBID tags
- Map each of the tracks using the mapper
- Load all of the releases the mapped track could appear on
- For each track in the collection, add them to the loaded releases, based on MBID.
- Evaluate the mapped files/releases.

Why is this a good idea?
- FAST
- Speeds up the process of finding clusters
- Automatic duplicate detection

What do it not do?
- Acutally modify your files -- this tool prints out the suggested "clusters"/releases.


Improvements
------------

- Right now this tool ignores MBIDs in the source files, it could use them as hints.
- Right now the evaluation of the candidate releases is very basic. A lot more intelligence and logic can go into this process to drastically improve the effectiveness of this tool.
- Right now all possible releases are loaded, but it might be best to examine albums first.
- Variout artist albums could also be tagged with this easily, but this isn't supported (or tested).

Usage
-----

On Linux, clone this repo, then:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./auto_tag.py <audio file dir>
```
