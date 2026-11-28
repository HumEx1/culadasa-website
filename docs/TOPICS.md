# Topic pages and the glossary

Added 28 Nov 2026 at the owner's request. Under Learn:

- `learn/topics/` lists the topics, A to Z;
- `learn/topics/<topic>/` gathers everything Culadasa said about one topic;
- `learn/glossary/` gives Pāli and method terms, each with a one-line meaning.

They are linked from the Learn page (after the ten stages), from the stage pages ("Related topics"), and from Search: searching a topic's word offers its page first.

**Both lists are a first draft for the teachers to confirm:** the twenty topics, the words that count for each, the one-line introductions and the glossary meanings. Checking them is one of the teachers' tasks in `docs/VOLUNTEER_TASKS.md`.

## How the mentions are found

`tools/build_topic_pages.py` reads the site's own data and writes `redesign/data/topic_pages.json`; `tools/build_redesign.py` turns that into the pages. The commands are:

```
python3 tools/build_topic_pages.py
python3 tools/build_redesign.py 2
```

- **Topics and words.** The topic list and the words for each are at the top of `tools/build_topic_pages.py` (`TOPICS`).
  - A word matches without accents, as a whole word, with a plural or possessive ending: "jhana" finds "jhāna" and "jhānas", but "sati" does not find "satisfaction" and "pain" does not find "paint" (fixed 28 Nov 2026 after review).
  - Hyphens and spaces are interchangeable: "mind-wandering" finds "mind wandering".
  - Names and titles that contain a topic word are left out (`EXCLUDE`): "Path of Purification", "Insight Meditation Society", Sāti the fisherman's son.
- **Sources.** The same as the stage pages (`docs/STAGES.md`):
  - the video transcripts, with AMA recordings counted under AMA videos;
  - Alex's AMA questions;
  - the writings;
  - the audio titles and descriptions;
  - the book index, which gives the pages for the matching book term (2015 first edition).
- **Counting.** In a video, mentions less than 25 seconds apart are one moment. Rows are listed most mentions first.
- **The video to start with.** If a talk's title names the topic and the talk mentions it at least five times, it is that talk (most mentions first). Otherwise it is the video or AMA recording with the most mentions, every one counted, within any ten minutes. It starts ten seconds before them, and the page says the choice is provisional.
- **The book.** The pages of every book index term that matches the topic, together, numbered pages only (not the contents).
- **Known limits.**
  - Broad words ("insight", "awakening", "pain") also count passing mentions.
  - A topic discussed without its words is missed.
  - The glossary meanings are Claude's draft, not his words, until the teachers replace them.
