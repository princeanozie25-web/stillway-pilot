"""Author-written development bugs.  Each is a small change to a pinned library that breaks some of its own tests.
The reference fix is the library as published.  Reports are written the way a user of the library would write them."""
REPOS = {
    "inflection": dict(pythonpath=".", tests=["test_inflection.py"]),
    "cachetools": dict(pythonpath="src", tests=["tests"]),
    "toolz": dict(pythonpath=".", tests=["toolz"]),
    "boltons": dict(pythonpath=".", tests=["tests"]),
    "tabulate": dict(pythonpath=".", tests=["test"]),
}
BUGS = []
def bug(id, repo, report, *edits, kind="", examples=()):
    """examples: (setup, expression) pairs whose value differs between the bug and the reference; the builder checks that."""
    BUGS.append(dict(id=id, repo=repo, report=" ".join(report.split()), edits=edits, kind=kind, examples=list(examples)))

# ---------------------------------------------------------------- inflection
I = "import inflection"
bug("inflection-1", "inflection", """
    Ordinals for the teens come out wrong. ordinalize(11) gives '11st', ordinalize(12) gives '12nd' and ordinalize(113)
    gives '113rd'. I expected '11th', '12th' and '113th'. Other numbers such as 1, 2, 23 and 101 look right.""",
    ("inflection/__init__.py", """    number = abs(int(number))
    if number % 100 in (11, 12, 13):
""", """    number = abs(int(number))
    if number % 10 in (11, 12, 13):
"""), kind="condition", examples=[(I, "inflection.ordinalize(11)"), (I, "inflection.ordinalize(113)")])

bug("inflection-2", "inflection", """
    underscore() loses the word break after a run of capitals. underscore('HTMLParser') returns 'htmlparser' and
    underscore('SSLError') returns 'sslerror'. I expected 'html_parser' and 'ssl_error'. Names without a run of capitals,
    such as 'DeviceType', come out right.""",
    ("inflection/__init__.py", """    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\\1_\\2', word)
""", ""), kind="missing step", examples=[(I, "inflection.underscore('HTMLParser')"), (I, "inflection.underscore('SSLError')")])

bug("inflection-3", "inflection", """
    parameterize() leaves a separator at the end of the result. parameterize('Hello World!') returns 'hello-world-' and
    parameterize('What is this?', separator='_') returns 'what_is_this_'. I expected 'hello-world' and 'what_is_this'.
    A separator at the start is removed as it should be.""",
    ("inflection/__init__.py", """        string = re.sub(r"(?i)^{sep}|{sep}$".format(sep=re_sep), '', string)""", """        string = re.sub(r"(?i)^{sep}".format(sep=re_sep), '', string)"""),
    kind="incomplete pattern", examples=[(I, "inflection.parameterize('Hello World!')"), (I, "inflection.parameterize('What is this?', separator='_')")])

bug("inflection-4", "inflection", """
    humanize() no longer drops a trailing _id. humanize('author_id') returns 'Author id'; I expected 'Author', as in the
    documentation. Words without that ending, such as 'employee_salary', come out right.""",
    ("inflection/__init__.py", """    word = re.sub(r"_id$", "", word)
    word = word.replace('_', ' ')""", """    word = word.replace('_', ' ')"""), kind="missing step", examples=[(I, "inflection.humanize('author_id')")])

# ---------------------------------------------------------------- cachetools
C = "import cachetools, cachetools.keys"
bug("cachetools-1", "cachetools", """
    LRUCache throws away entries I have just read. With maxsize=2 I store 'a', then 'b', then read 'a', then store 'c'.
    Afterwards 'a' is gone and 'b' is still there. I expected the least recently used entry, 'b', to be evicted, since
    reading 'a' should count as using it.""",
    ("src/cachetools/__init__.py", """        value = cache_getitem(self, key)
        try:
            self.__order.move_to_end(key)
        except KeyError:  # __missing__ may not store item
            pass
        return value
""", """        return cache_getitem(self, key)
"""), kind="missing step", examples=[(C + "\nc = cachetools.LRUCache(maxsize=2); c['a'] = 1; c['b'] = 2; c['a']; c['c'] = 3", "sorted(c)")])

bug("cachetools-2", "cachetools", """
    When a cache has a getsizeof function, overwriting an existing key makes the cache think it is fuller than it is.
    c = Cache(maxsize=10, getsizeof=len); c['a'] = 'xxx'; c['a'] = 'xxxx' leaves c.currsize at 7, and I expected 4.
    After a few overwrites the cache starts evicting other entries although there is plenty of room.""",
    ("src/cachetools/__init__.py", """            else:
                diffsize = itemsize - size[key]
                while self.__currsize + diffsize > maxsize:""", """            else:
                diffsize = itemsize
                while self.__currsize + diffsize > maxsize:"""),
    kind="wrong arithmetic", examples=[(C + "\nc = cachetools.Cache(maxsize=10, getsizeof=len); c['a'] = 'xxx'; c['a'] = 'xxxx'", "c.currsize")])

bug("cachetools-3", "cachetools", """
    setdefault() returns the default but does not store it. After c = Cache(maxsize=4); c.setdefault('a', 1), the key
    'a' is not in the cache and len(c) is 0. I expected setdefault to insert the value when the key is missing, as it
    does for a dict.""",
    ("src/cachetools/__init__.py", """        else:
            self[key] = value = default
        return value""", """        else:
            value = default
        return value"""), kind="missing step", examples=[(C + "\nc = cachetools.Cache(maxsize=4); c.setdefault('a', 1)", "len(c)")])

bug("cachetools-4", "cachetools", """
    pop() returns the value but does not remove the entry. After c = Cache(maxsize=4); c['a'] = 1; c.pop('a'), the key
    'a' is still in the cache and len(c) is still 1. I expected the entry to be gone. The same happens with LRUCache
    and the other cache classes.""",
    ("src/cachetools/__init__.py", """        if key in self:
            value = self[key]
            del self[key]
        elif default is self.__marker:""", """        if key in self:
            value = self[key]
        elif default is self.__marker:"""), kind="missing step", examples=[(C + "\nc = cachetools.Cache(maxsize=4); c['a'] = 1; c.pop('a')", "len(c)")])

# ---------------------------------------------------------------- toolz
T = "import toolz"
bug("toolz-1", "toolz", """
    unique() with a key function does not remove anything. list(unique(['cat', 'mouse', 'dog', 'hen'], key=len)) returns
    all four words. I expected ['cat', 'mouse'], one item for each distinct key. Without a key, unique works.""",
    ("toolz/itertoolz.py", """            val = key(item)
            if val not in seen:
                seen_add(val)
                yield item""", """            val = key(item)
            if val not in seen:
                seen_add(item)
                yield item"""), kind="wrong variable", examples=[(T, "list(toolz.unique(['cat', 'mouse', 'dog', 'hen'], key=len))")])

bug("toolz-2", "toolz", """
    update_in() does not apply the function when the key is missing. update_in({1: 'foo'}, [2, 3, 4], lambda x: x + 1, 0)
    returns {1: 'foo', 2: {3: {4: 0}}}. The documentation says the innermost value is set to func(default), so I
    expected {1: 'foo', 2: {3: {4: 1}}}. When the key exists the function is applied correctly.""",
    ("toolz/dicttoolz.py", """    else:
        inner[k] = func(default)
    return rv""", """    else:
        inner[k] = default
    return rv"""), kind="missing call", examples=[(T, "toolz.update_in({1: 'foo'}, [2, 3, 4], lambda x: x + 1, 0)")])

bug("toolz-3", "toolz", """
    get_in() with no_default=True does not raise. get_in(['y'], {}, no_default=True) returns None. The documentation
    says that with no_default=True a missing key raises the original error, so I expected a KeyError.""",
    ("toolz/dicttoolz.py", """    except (KeyError, IndexError, TypeError):
        if no_default:
            raise
        return default""", """    except (KeyError, IndexError, TypeError):
        return default"""), kind="missing step", examples=[(T, "toolz.get_in(['y'], {}, no_default=True)")])

bug("toolz-4", "toolz", """
    interpose() puts the separator in the wrong places. list(interpose('a', [1, 2, 3])) returns ['a', 2, 'a', 3, 'a']:
    the first element is lost and there is a separator at both ends. I expected [1, 'a', 2, 'a', 3].""",
    ("toolz/itertoolz.py", """    inposed = concat(zip(itertools.repeat(el), seq))""", """    inposed = concat(zip(seq, itertools.repeat(el)))"""),
    kind="wrong order", examples=[(T, "list(toolz.interpose('a', [1, 2, 3]))")])

# ---------------------------------------------------------------- boltons
B = "from boltons import iterutils, mathutils, strutils, timeutils\nfrom datetime import date"
bug("boltons-1", "boltons", """
    chunked() pads the last chunk with None even when I do not ask for a fill value. iterutils.chunked(range(10), 3)
    returns [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]. I expected the last chunk to be [9]; padding should
    happen only when the fill argument is given.""",
    ("boltons/iterutils.py", """        if lc < size and do_fill:""", """        if lc < size:"""), kind="condition", examples=[(B, "iterutils.chunked(range(10), 3)")])

bug("boltons-2", "boltons", """
    mathutils.ceil() with options skips an option that equals the value. ceil(4, options=[1.5, 2.5, 4, 6]) returns 6.
    I expected 4, the smallest option greater than or equal to the value. Values strictly between two options, such as
    3.5, give the right answer.""",
    ("boltons/mathutils.py", """    i = bisect.bisect_left(options, x)
    if i == len(options):""", """    i = bisect.bisect_right(options, x)
    if i == len(options):"""), kind="boundary", examples=[(B, "mathutils.ceil(4, options=[1.5, 2.5, 4, 6])")])

bug("boltons-3", "boltons", """
    daterange() has the meaning of inclusive reversed when counting forwards. list(daterange(date(2020, 1, 1),
    date(2020, 1, 4))) yields four dates, ending with 4 January, and with inclusive=True it yields only three. I
    expected the stop date to be left out by default and included only with inclusive=True. Counting backwards with a
    negative step behaves correctly.""",
    ("boltons/timeutils.py", """    elif start <= stop:
        finished = operator.gt if inclusive else operator.ge""", """    elif start <= stop:
        finished = operator.ge if inclusive else operator.gt"""), kind="swapped", examples=[(B, "len(list(timeutils.daterange(date(2020, 1, 1), date(2020, 1, 4))))"), (B, "len(list(timeutils.daterange(date(2020, 1, 1), date(2020, 1, 4), inclusive=True)))")])

bug("boltons-4", "boltons", """
    bytes2human() does not switch to the next unit at an exact power of 1024. strutils.bytes2human(1024) returns
    '1024B' and bytes2human(1024 ** 2) returns '1024K'. I expected '1K' and '1M'. One byte more, for example 1025,
    gives '1K' as it should.""",
    ("boltons/strutils.py", """        if abs_bytes < next_size:
            break""", """        if abs_bytes <= next_size:
            break"""), kind="boundary", examples=[(B, "strutils.bytes2human(1024)"), (B, "strutils.bytes2human(1024 ** 2)")])

# ---------------------------------------------------------------- tabulate
TB = "from tabulate import tabulate"
bug("tabulate-1", "tabulate", """
    In the pipe (Markdown) format the alignment colons are on the wrong side. tabulate([['apple', 1]], headers=['item',
    'qty'], tablefmt='pipe') gives the separator line |-------:|:------|, which makes Markdown right-align the text
    column and left-align the numbers. I expected |:-------|------:|, left for text and right for numbers. Centred
    columns are marked correctly.""",
    ("tabulate/__init__.py", """    if align in ["right", "decimal"]:
        return ("-" * (w - 1)) + ":"
    elif align == "center":
        return ":" + ("-" * (w - 2)) + ":"
    elif align == "left":
        return ":" + ("-" * (w - 1))""", """    if align in ["right", "decimal"]:
        return ":" + ("-" * (w - 1))
    elif align == "center":
        return ":" + ("-" * (w - 2)) + ":"
    elif align == "left":
        return ("-" * (w - 1)) + ":\""""), kind="swapped", examples=[(TB, "tabulate([['apple', 1]], headers=['item', 'qty'], tablefmt='pipe').splitlines()[1]")])

bug("tabulate-2", "tabulate", """
    disable_numparse with a list of columns does the opposite of what I ask. tabulate([['1e3', '1e3']],
    disable_numparse=[0]) shows the first column as 1000 and leaves the second as the text 1e3. I expected the first
    column, the one I listed, to be left as text and the second to be parsed as a number. disable_numparse=True and
    False work as documented.""",
    ("tabulate/__init__.py", """        numparses = [True] * column_count
        for index in disable_numparse:
            numparses[index] = False
        return numparses""", """        numparses = [False] * column_count
        for index in disable_numparse:
            numparses[index] = True
        return numparses"""), kind="inverted", examples=[(TB, "tabulate([['1e3', '1e3']], disable_numparse=[0])")])

bug("tabulate-3", "tabulate", """
    The missingval option is ignored. tabulate([['a', None]], missingval='?') prints an empty cell for the None value.
    I expected the cell to show ?.""",
    ("tabulate/__init__.py", """    if val is None:
        return missingval
    if isinstance(val, (bytes, str)) and not val:
        return \"\"""", """    if val is None or (isinstance(val, (bytes, str)) and not val):
        return \"\""""), kind="lost branch", examples=[(TB, "tabulate([['a', None]], missingval='?')")])

bug("tabulate-4", "tabulate", """
    showindex puts the index in the wrong place. tabulate([['a', 1], ['b', 2]], showindex=True) prints the row numbers
    0 and 1 as the last column. I expected the index to be the first column, on the left.""",
    ("tabulate/__init__.py", """        new_rows.append([index_v] + list(row))""", """        new_rows.append(list(row) + [index_v])"""),
    kind="wrong order", examples=[(TB, "tabulate([['a', 1], ['b', 2]], showindex=True)")])
