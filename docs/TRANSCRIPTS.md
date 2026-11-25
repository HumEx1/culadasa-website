# Video transcripts

D, 25 Nov 2026: "take the close caption text off of all the videos, record those into documents that are kept in the repo and have every video searchable."

## What there is

- **99 transcripts**, one per video on Culadasa's YouTube channel that has English captions: `docs/transcripts/` (list: `docs/transcripts/README.md`). 835,042 words. Each paragraph starts with a time stamp that opens the video at that moment.
- **Search:** `redesign/data/transcripts.json` holds the same text with its time stamps. The Topics search reads it when the search covers Videos (or the whole site), and only then, because it is about 5 MB (1.7 MB as sent). Each video result shows up to three passages, each with a time link into the video. AMA-only, Writings-only and Audio-only searches never download it.
- The transcripts are **YouTube's automatic captions**, not a person's transcription. Every document and the Topics page say so.

## How they were made

1. On D's Mac, 25 Nov 2026, from `https://www.youtube.com/@Culadasa/videos` (the cloud environment cannot reach YouTube):
   `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en,en-orig,en-US,en-GB" --sub-format vtt --sleep-requests 1 --sleep-subtitles 2 --ignore-errors -o "%(upload_date)s %(id)s %(title).80B.%(ext)s" "https://www.youtube.com/@Culadasa/videos"`
   179 caption files for 99 videos, 43 MB. They are data, not documents, so the maintainers keep them outside this repository.
2. `python3 tools/build_transcripts.py <folder of the .vtt files>` reads the one `.en-orig.vtt` per video (YouTube's own English captions, not a translation), joins YouTube's rolling caption lines once each, applies the corrections below, and writes the documents, their list and the search data. Titles come from the site's video list where the video is on it, otherwise from the file name (cut at 80 bytes by the download).
3. Nothing else is reworded.

## Pāli corrections (agreed with D, 25 Nov 2026)

YouTube mishears his Pāli terms. Culadasa mostly used the Pāli forms, so mishearings are corrected to Pāli. Words he said in Sanskrit (nirvana, karma, dharma, arhat) are left as he said them, because YouTube heard those correctly; the search matches the Pāli and Sanskrit forms of a word to each other instead (`SYN` in `redesign/assets/topics.js`). The exact rules are `RULES` in `tools/caption_corrections.py`, applied in that order, ignoring case. 998 changes in all.

| YouTube wrote | Corrected to | Condition |
|---|---|---|
| jonah, janna, jana, jonna, jannah, jhana (and their plurals, including "Jonah's") | jhāna, jhānas | always |
| john | jhāna | only after first, second … eighth, the, a, into, enter, entering, in, of, body, luminous, pleasure, form, formless, deepest, deeper, higher, that, or before factor, state, practice; never before "of", "Yates", "Kabat". About 89 "John"s are left, most of them real people (John of the Cross, questioners named John). |
| PT, pity | pīti | pity: not "I pity the poor immigrant", not "that word pity" (the Dylan story) |
| meta, metta | mettā | meta: not before "-cognitive", awareness, level, analysis, data, physics |
| suka, sukkah, sooka | sukha | always |
| dooka, dooku, duke | dukkha | always |
| Dukan Yanis, Dukan youngins, Duquesne Jana, Dupin ñāṇas | dukkha ñāṇas | always |
| yanis, nyanas, nanas | ñāṇas | always |
| sati some vagina, sati SAA Jana, sampaja, sampajanna | sati sampajañña / sampajañña | always |
| samata, shamata, shamita | samatha | always |
| nibana, nibbana | nibbāna | always |
| anata | anattā | always |
| vipassan | vipassanā | always |
| tana | taṇhā | always |
| nimita | nimitta | always |
| vedna, vadana, vedan, vedanos, vedanes; vedanta | vedanā | vedanta: not after "Advaita", not before teaching, practice, tradition, "and other" |
| abidama | Abhidhamma | always |
| satipatanas, satipatanos | satipaṭṭhānas | always |
| polly | Pāli | always |
| cetapana, cetaphana | sotāpanna | always |
| ikki | ekaggatā | always |
| teravan, teravoden | Theravāda, Theravādin | always |
| biku, biko, bikkhu, bhikku | bhikkhu | always |
| Naggar Jonah's | Nāgārjuna's | always |

Not corrected: words YouTube already spelled right (samadhi, sangha, dharma, rigpa, mahamudra…); juno (a questioner called Juno); Sanskrit he actually said.

## To redo or extend

Download new captions with the same command into a new folder, then run `python3 tools/build_transcripts.py <folder>`, `python3 tools/build_redesign.py` and `python3 tools/build_redesign.py 2`. A new mishearing gets a new rule in `tools/caption_corrections.py` and a new row above.
