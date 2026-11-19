# CS teacher marking – web app

The GCSE Computer Science teacher marking screen, for iPads and laptops.

**Address:** https://mrp-cs.github.io/cs-marking/ · **For staff only** – the passcode is in Teacher guide 1 in OneNote.

- The page in `site/` is locked: the marking screen (with the mark schemes) is stored encrypted in `app.bin` and only opens with the teacher passcode. Nothing readable is in this repository.
- It works offline: once opened, the whole screen is kept on the device and updates itself the next time it can reach this site.
- No student data is stored here. Class trackers stay in the department's OneDrive.
- The same build is attached to the Teacher marking pages in OneNote, so the laptop and iPad versions always match (same version number).

## Releases
Every push to `main` runs the checks in `tests/smoke.py` (passcode lock, opening offline, and the iPad route of opening a tracker, marking a notebook check and saving it through Save to Files) on Chromium and WebKit. The site is only published if they pass.

## Undo a bad release
Actions › the last good "Test and publish" run › **Re-run all jobs** puts that version back. Or revert the commit on `main`.

## Changing the passcode
Rebuild `site/` with the new passcode, update the `MARKING_PASSCODE` secret (Settings › Secrets and variables › Actions), and update Teacher guide 1. Teachers then type the new passcode once.
