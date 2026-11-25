# The ten stages in his words

Added 25 Nov 2026 at the group's request (D). Each of the ten stages of *The Mind Illuminated* has a page, `ten-stages/stage-1/` to `ten-stages/stage-10/`, under an overview at `ten-stages/`. Each page has:

- a video to start with, pinned at the top;
- every place Culadasa talks about that stage, as title rows in the same groups as the search: Videos, AMA sessions, Writings, Audio, The Book.

Many of these talks came after the book, so they add to it.

They are linked from:

- The Book page's list of stages;
- Learn (The method → The ten stages);
- Start here (Learn the map);
- the home page.

## How the mentions are found

`tools/build_stages.py` reads the site's own data and writes `redesign/data/stages.json`; `tools/build_redesign.py` turns that into the pages. Run:

```
python3 tools/build_stages.py
python3 tools/build_redesign.py 2
python3 tools/build_redesign.py
```

**Sources:**

- the video transcripts (`redesign/data/transcripts.json`), with AMA recordings counted under AMA sessions;
- Alex's AMA questions, the writings and the audio titles and descriptions (`redesign/data/topics.json`);
- the book's chapter pages (`redesign/data/book.json`).

**What counts as a mention of stage N** (the exact patterns are in `tools/build_stages.py`):

| Rule | Example | Counts for |
|---|---|---|
| "stage" followed by a number, in figures or words | "stage four", "Stage 4" | 4 |
| A list after "stages" | "stages five and six", "stage one two three" | each stage named |
| A range of up to four stages | "stages two to four", "Stage 3–4" | 2, 3, 4 |
| A range of more than four stages | "stages one to six" | none (it is about the stages in general) |
| "the Nth stage" | "the fourth stage" | 4, but only when no word within 100 characters is awakening, path, insight, stream, jhāna or fetter |
| Followed by "of awakening", "of insight", "of the path", "path" or "ñāṇa" | "first stage of awakening" | none |
| Preceded by "insight" | "insight stage four" | none |

**Counting:**

- In a video, mentions less than 25 seconds apart are one moment with one time button, but each mention still counts.
- In an AMA session, the count is the mentions in Alex's questions plus those in the recording.
- Rows are listed most mentions first.

**The Book.** A stage's chapter runs from the first page whose running footer names the stage to the page before the next part of the book begins. Page numbers are from the 2015 first edition (final draft); later editions may differ.

**The video to start with, until the teachers choose one:**

- It is the video or AMA recording with the most moments on that stage within any ten minutes; a talk wins a tie with an AMA session.
- It starts five seconds before that stretch.
- Each page says the choice is provisional.

**Known limits:**

- YouTube's captions sometimes mishear numbers ("stage for"); those are missed.
- A stage mentioned only by its name ("subtle dullness") without its number is not counted, because those words are used for other things too.
- Some matches will be wrong. Checking them is a teachers' task in `docs/VOLUNTEER_TASKS.md` §9.

**Choosing the pinned videos.** When the teachers choose them, record each one (video, start time, who chose it and when) in the table below. `tools/build_stages.py` will then use it in place of the provisional rule.

| Stage | Video | Start | Chosen by | Date |
|---|---|---|---|---|
| 1–10 | provisional (rule above) | | | |
