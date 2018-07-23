'''Copyright 2018, Deepak

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

def pluck(iterable, key, missing_value="N/A"):
    """In an iterable of dicts, return a list of
    values from one key
    """
    result = list()
    for item in iterable:
        _item = dict(item)
        result.append(_item.pop(key, missing_value))

    return result


def normalize(iterable, cols, missing_value=""):
    """In an iterable of dicts, make sure each
    dict corresponds to keys in the 'cols' list.
    Missing values are plugged with 'missing_value'
    """
    result = list()
    for item in iterable:
        _item = dict(item)
        _normalized = dict()

        for col in cols:
            _val = _item.pop(col, "*****N/A*****")

            if _val == "*****N/A*****":
                _val = missing_value

            _normalized[col] = _val

        result.append(_normalized)

    return result


def get_key(udict, key, missing_value=""):
    """Return a key:value pair as dict
    """

    cdict = dict(udict)

    return {key: cdict.pop(key, missing_value)}


def as_dict(keys, values):
    """Take two iterables, one with keys and other
    with values and return a dict
    """

    try:
        _ = iter(keys)
    except TypeError:
        return {keys: values}

    return dict(zip(keys, values))


def add_key(udict, key, value):
    """Add a new key:value combo to dict
    """

    cdict = dict(udict)

    cdict[key] = value
    return cdict


def rename_key(udict, key, new_key):
    """Rename a key in dict
    """
    cdict = dict(udict)

    _val = cdict.pop(key, "*****N/A*****")

    if _val == "*****N/A*****":
        return cdict

    cdict[new_key] = _val
    return cdict


def translate_value(udict, key, new_value):
    """Plug new value for key
    """

    cdict = dict(udict)

    cdict[key] = new_value
    return cdict


def translate_keys(iterable, cols):
    """An iterable of dicts, change a set of 
    key names to another
    """

    _iterable = list()

    for item in iterable:
        _item = dict(item)

        for colmap in cols:
            _item = rename_key(_item, *colmap)

        _iterable.append(_item)

    return _iterable


def translate_values(iterable, key, func):
    """Run key values through func and plug that
    value in
    """

    _iterable = list()

    for item in iterable:
        _item = dict(item)

        if key in _item:
            _item[key] = func(_item[key])

        _iterable.append(_item)

    return _iterable


def append_values(iterable, key, new_key, func):
    """Analogous functionality to translate_values
    except a new key is put in
    """    
    _iterable = list()

    for item in iterable:
        _dict = add_key(item, new_key, item[key])        
        _iterable.append(_dict)

    _iterable = translate_values(_iterable, new_key, func)
    return _iterable


def merge_dicts(src, dest):
    """Merge to dictionaries and return a new dictionary
    """
    ndict = dict(src)
    ndict.update(dest)
    return ndict


def merge_values(src, dest, key):
    """src and dest are iterable of dicts
    Merge and return a new iterable
    Key is assumed to be unique in the iterable if present.
    However, the key can be missing values in either iterable
    In case of conflicting values dest will prevail
    """

    src_keys = list(filter(lambda x: x != "N/A", pluck(src, key)))
    dest_keys = list(filter(lambda x: x != "N/A", pluck(dest, key)))

    all_keys = list(set(src_keys) | set(dest_keys))

    result = []

    for key_value in all_keys:
        src_filter = list(filter(lambda x: x.get(key, "##N/A##") == key_value, src))

        if len(src_filter) > 1:
            continue

        dest_filter = list(filter(lambda x: x.get(key, "##N/A##") == key_value, dest))

        if len(dest_filter) > 1:
            continue

        if not src_filter:
            src_filter = dict()
        else:
            src_filter = src_filter[0]

        if not dest_filter:
            dest_filter = dict()
        else:
            dest_filter = dest_filter[0]

        result.append(merge_dicts(src_filter, dest_filter))

    return result
