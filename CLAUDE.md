# CLAUDE.md — culadasa-website

Instructions for any Claude session working in this repository.

1. **Read `PRIVACY.md` first and follow it as a hard rule.** No private information about anyone using or editing this code base goes into the repository; no credentials of any kind; when in doubt, ask before writing it. This repository is shared and will be public.
2. **Read `docs/PROJECT_BRIEF.md`** for the background, decisions, site inventory and open items.
3. **Nothing on the live culadasa.com is changed from here.** This repository is a sandbox for the replacement site. The domain, hosting and WordPress admin are controlled by people, not by this code, and no DNS or hosting change happens without the owner's explicit confirmation.
4. **Every existing URL keeps working.** The 14 page paths and the 28 media paths under `wp-content/uploads/2021/09/` in the brief §6b are the acceptance list.
5. **Snapshots are never edited.** `source/wordpress-export/` and `source/live-site-YYYY-MM-DD/` are what the site looked like on those dates. A new snapshot gets a new dated folder.
6. **Plain HTML and CSS, no build step, no frameworks**, so anyone in the maintenance group can edit a page with a text editor.
7. Commit messages say what changed and why. Before publishing a new version of the live site, tell the people who may be editing it and wait for their go.
