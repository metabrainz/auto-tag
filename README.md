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

Start with at most 1,000 audio files to begin with. Perhaps just a single release or small artist to get your feet wet.

Example output
--------------

The following output show the output if you provide one single album of tracks:

```
(.ve) >./auto_tag.py ~/Downloads/test
Scan collection...
Map tracks...
Load releases...
Examine matches...
FULL MATCH! (release group 053388 'Will of the People')
  1   1 Will of the People                       01. Will Of The People.mp3
  1   2 Compliance                               02. Compliance.mp3
  1   3 Liberation                               03. Liberation.mp3
  1   4 Won’t Stand Down                         04. Won’t Stand Down.mp3
  1   5 Ghosts (How Can I Move On)               05. Ghosts (How Can I Move On).mp3
  1   6 You Make Me Feel Like It’s Halloween     06. You Make Me Feel Like It's Halloween.mp3
  1   7 Kill or Be Killed                        07. Kill Or Be Killed.mp3
  1   8 Verona                                   08. Verona.mp3
  1   9 Euphoria                                 09. Euphoria.mp3
  1  10 We Are Fucking Fucked                    10. We Are Fucking Fucked.mp3

FULL MATCH! (release group 237108 'Compliance')
  1   1 Compliance                               02. Compliance.mp3
  1   2 Won’t Stand Down                         04. Won’t Stand Down.mp3

FULL MATCH! (release group 24a5c4 'Will of the People')
  1   1 Will of the People                       01. Will Of The People.mp3
  1   2 Compliance                               02. Compliance.mp3
  1   3 Won’t Stand Down                         04. Won’t Stand Down.mp3

FULL MATCH! (release group 6cf3ce 'Kill or Be Killed')
  1   1 Kill or Be Killed                        07. Kill Or Be Killed.mp3
  1   2 Will of the People                       01. Will Of The People.mp3
  1   3 Compliance                               02. Compliance.mp3
  1   4 Won’t Stand Down                         04. Won’t Stand Down.mp3
```
