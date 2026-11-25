"""Corrections to YouTube's automatic captions of Culadasa's talks: the Pāli terms it mishears.

Agreed with D on 25 Nov 2026. Corrections are to the Pāli form, because he mostly used Pāli. Words he
said in Sanskrit (nirvana, karma, dharma, arhat) are left as he said them; the search matches both forms.
Each rule is a regular expression (case-insensitive) and its replacement, applied in this order. Words
that are also English or names ("john", "pity", "meta", "vedanta") change only in the contexts written
into their rule, so John of the Cross, the questioners named John, "I pity the poor immigrant",
"meta-cognitive" and "Advaita Vedanta" stay as they are. docs/TRANSCRIPTS.md lists every rule in plain words.
"""
import re
RULES = [
 (r"\bnagg?ar jonah'?s?\b", "Nāgārjuna's"),
 (r"\b(dukan (yanis|youngins)|duquesne jana)\b", "dukkha ñāṇas"),
 (r"\bsati saa jana\b", "sati sampajañña"),
 (r"\bsati some vagina\b", "sati sampajañña"),
 (r"\bsampaja(nna)?\b", "sampajañña"),
 (r"\b(yanis|nyanas|nanas|nana's)\b", "ñāṇas"),
 (r"\bdupin ñāṇas\b", "dukkha ñāṇas"),   # found 25 Nov 2026 in the January 2018 AMA
 (r"\b(jonah|janna|jana|jonna|jannah|jhana)'?s\b|\b(jonas|john's|johns)\b", "jhānas"),   # YouTube writes the plural as "Jonah's"
 (r"\b(jonah|janna|jana|jonna|jannah|jhana)\b", "jhāna"),
 (r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|1st|2nd|3rd|4th|the|a|into|enter|entering|in|of|body|luminous|pleasure|form|formless|deepest|deeper|higher|that) john\b(?!\s+(of|yates|kabat)\b)", r"\1 jhāna"),
 (r"\bjohn (factors?|states?|practice)\b", r"jhāna \1"),
 (r"\b(suka|sukkah|sooka)\b", "sukha"),
 (r"\b(dooka|dooku)\b", "dukkha"),
 (r"\bduke\b", "dukkha"),
 (r"\bpt\b", "pīti"),
 (r"\b(?<!i )(?<!word )pity\b(?! the poor)", "pīti"),
 (r"\bmeta\b(?![-\s]?(cognit|awareness|level|analysis|data|physic))", "mettā"),
 (r"\bmetta\b", "mettā"),
 (r"\b(nibana|nibbana)('s)?\b", r"nibbāna\2"),
 (r"\banata\b", "anattā"),
 (r"\bvipassan\b", "vipassanā"),
 (r"\b(samata|shamata|shamita)\b", "samatha"),
 (r"\babidama\b", "Abhidhamma"),
 (r"\bnimita\b", "nimitta"),
 (r"\bsatipatan(as|os)\b", "satipaṭṭhānas"),
 (r"\bteravan\b", "Theravāda"),
 (r"\bteravoden\b", "Theravādin"),
 (r"\bpolly\b", "Pāli"),
 (r"\bcetap?h?ana\b", "sotāpanna"),
 (r"\btana\b", "taṇhā"),
 (r"\bikki\b", "ekaggatā"),
 (r"\b(vadana|vedna|vedan|vedanos|vedanes)\b", "vedanā"),
 (r"\bvedna's\b", "vedanā's"),
 (r"(?<!advaita )\bvedanta\b(?! (teaching|practice|tradition|and other))", "vedanā"),
 (r"\b(biku|biko|bikkhu|bhikku)\b", "bhikkhu"),
]
CRE = [(re.compile(p, re.I), r) for p, r in RULES]
def fix(text, log=None):
    """Return text with every rule applied; if log is a list, append (rule number, heard, written) for each change."""
    for i,(c, r) in enumerate(CRE):
        def sub(m, r=r, i=i):
            out = m.expand(r) if '\\' in r else r
            if log is not None: log.append((i, m.group(0), out))
            return out
        text = c.sub(sub, text)
    return text
