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

- **Topics and words.** The topic list and the words for each are at the top of `tools/build_topic_pages.py` (`TOPICS`). A word matches without accents and at the start of a word, so "dullness" also finds "dullnesses" and "jhana" finds "jhāna". Hyphens and spaces are interchangeable: "mind-wandering" finds "mind wandering".
- **Sources.** The same as the stage pages (`docs/STAGES.md`):
  - the video transcripts, with AMA recordings counted under AMA videos;
  - Alex's AMA questions;
  - the writings;
  - the audio titles and descriptions;
  - the book index, which gives the pages for the matching book term (2015 first edition).
- **Counting.** In a video, mentions less than 25 seconds apart are one moment. Rows are listed most mentions first.
- **The video to start with.** It is the video or AMA recording with the most moments within any ten minutes; a talk wins a tie. It starts five seconds before that stretch, and the page says the choice is provisional.
- **Known limits.**
  - Broad words ("insight", "awakening", "pain") also count passing mentions.
  - A topic discussed without its words is missed.
  - The glossary meanings are Claude's draft, not his words, until the teachers replace them.
