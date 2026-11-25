"""Spelling corrections for text shown in the redesign (D, 25 Nov 2026: "fix Alex's typo and any other that you find").

Only plain misspellings are corrected; no word is changed for another and no sentence is reworded. Used for the
essays (tools/build_redesign.py, clean_essay) and for the questions, keywords and quotes in Alex's Q&A index
(tools/build_qna_index.py). The source snapshots and the mirror are not changed. Found by spell-checking every
page of redesign-2 and reading each hit in context; British spellings, Pāli terms and names are left alone.
"""
import re

FIXES = {
    # essays by Culadasa
    'experiement': 'experiment', 'occuring': 'occurring', 'noticieable': 'noticeable', 'indispensible': 'indispensable',
    # questions, keywords and quotes in Alex's Q&A index
    'abscence': 'absence', 'accesss': 'access', 'acheive': 'achieve', 'acheiving': 'achieving', 'addiciton': 'addiction',
    'althought': 'although', 'annnoyed': 'annoyed', 'anyting': 'anything', 'apppreciation': 'appreciation',
    'atempted': 'attempted', 'attentin': 'attention', 'attining': 'attaining', 'awarenes': 'awareness',
    'awarereness': 'awareness', 'becaused': 'because', 'beyone': 'beyond', 'bhikkus': 'bhikkhus', 'carreer': 'career',
    'catergories': 'categories', 'chnged': 'changed', 'commentk': 'comment', 'commited': 'committed',
    'comparisions': 'comparisons', 'compulstive': 'compulsive', 'conficting': 'conflicting',
    'consciouness': 'consciousness', 'consciounsess': 'consciousness', 'consciousnoss': 'consciousness',
    'consiousness': 'consciousness', 'consitently': 'consistently', 'corrctly': 'correctly', 'defferent': 'different',
    'deuality': 'duality', 'disappoined': 'disappointed', 'dissulution': 'dissolution', 'distinguisting': 'distinguishing',
    'elemnts': 'elements', 'enirety': 'entirety', 'everyting': 'everything', 'exhilirating': 'exhilarating',
    'expain': 'explain', 'experiece': 'experience', 'experince': 'experience', 'exprience': 'experience',
    'exporing': 'exploring', 'expreriencing': 'experiencing', 'exprienced': 'experienced', 'expriences': 'experiences',
    'extemely': 'extremely', 'feelng': 'feeling', 'felth': 'felt', 'folllows': 'follows', 'fourty': 'forty',
    'framewok': 'framework', 'genearally': 'generally', 'healped': 'helped', 'hime': 'him', 'hvven': 'haven',
    'hyphagogia': 'hypnagogia', 'hyphagogic': 'hypnagogic', 'increasingy': 'increasingly', 'instucted': 'instructed',
    'intellectuall': 'intellectual', 'intiuitive': 'intuitive', 'involbes': 'involves', 'kinf': 'kind', 'liek': 'like',
    'listenced': 'listened', 'mainaining': 'maintaining', 'mentined': 'mentioned', 'metitating': 'meditating',
    'mindfuless': 'mindfulness', 'modiality': 'modality', 'netword': 'network', 'occured': 'occurred',
    'occurences': 'occurrences', 'oportunity': 'opportunity', 'otehr': 'other', 'overwhelemed': 'overwhelmed',
    'palpabale': 'palpable', 'particualr': 'particular', 'particuar': 'particular', 'pleasand': 'pleasant',
    'pracitioners': 'practitioners', 'practic': 'practice', 'precice': 'precise', 'prominents': 'prominent',
    'purificaiton': 'purification', 'realease': 'release', 'recoginizing': 'recognizing', 'rememeber': 'remember',
    'renunication': 'renunciation', 'resouces': 'resources', 'rudimetary': 'rudimentary', 'scientic': 'scientific',
    'stablilize': 'stabilize', 'sublest': 'subtlest', 'subshapter': 'subchapter', 'techique': 'technique',
    'techniqes': 'techniques', 'thriggering': 'triggering', 'throught': 'through', 'thrroughout': 'throughout',
    'thuths': 'truths', 'traing': 'training', 'tranlation': 'translation', 'trining': 'training',
    'unconquerrable': 'unconquerable', 'undelying': 'underlying', 'understad': 'understand',
    'understaning': 'understanding', 'undestand': 'understand', 'unncecessary': 'unnecessary',
    'unnecesssary': 'unnecessary', 'virbratory': 'vibratory', 'woudn': 'wouldn', 'ideat': 'idea',
    'intenting': 'intending', 'workd': 'work',
}
_RE = re.compile(r'\b(' + '|'.join(sorted(FIXES, key=len, reverse=True)) + r')\b', re.I)
_THATS = re.compile(r'\bevent thats\b')   # "the memory of event thats happened" -> "that's"


def fix_spelling(text):
    """Correct the misspellings above, keeping a capital first letter."""
    def sub(m):
        w = m.group(0)
        r = FIXES[w.lower()]
        return r[0].upper() + r[1:] if w[0].isupper() else r
    return _THATS.sub('event that’s', _RE.sub(sub, text))
