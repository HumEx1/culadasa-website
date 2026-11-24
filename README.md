# Culadasa website

Source for the static mirror of culadasa.com, the legacy website of Culadasa (John Yates). Start with `docs/PROJECT_BRIEF.md`: the background, decisions, access inventory, maintenance-group plan and a full inventory of the existing site. The original WordPress export is in `source/wordpress-export/`.

This repository lives under HumEx1 for now and will be transferred to a "Culadasa" GitHub organisation shared by the maintenance group. Working rules for Claude sessions are in HumEx1/Claude under `Culadasa_Website/`.

**Read `PRIVACY.md` before contributing.** No private information about anyone who uses or edits this code base, and no credentials of any kind, are ever committed here; when in doubt, ask first.

Layout: `site/` is the website as served: an exact mirror of the live culadasa.com, built by `tools/mirror_build.py` (see `docs/MIRROR_NOTES.md` for every way it differs under the hood). `source/` holds read-only snapshots of the old site; `docs/` holds the project brief and the design options for a later refresh.
