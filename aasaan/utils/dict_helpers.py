'''Copyright 2018, Deepak

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

def pluck(iterable, key, missing_value="N/A"):
    result = list()
    for item in iterable:
        _item = dict(item)
        result.append(_item.pop(key, missing_value))

    return result


def normalize(iterable, cols, missing_value=""):
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
    cdict = dict(udict)

    return {key: cdict.pop(key, missing_value)}


def as_dict(keys, values):
    try:
        _ = iter(keys)
    except TypeError:
        return {keys: values}

    return dict(zip(keys, values))


def add_key(udict, key, value):
    cdict = dict(udict)

    cdict[key] = value
    return cdict


def rename_key(udict, key, new_key):
    cdict = dict(udict)

    _val = cdict.pop(key, "*****N/A*****")

    if _val == "*****N/A*****":
        return cdict

    cdict[new_key] = _val
    return cdict


def translate_value(udict, key, new_value):
    cdict = dict(udict)

    cdict[key] = new_value
    return cdict


def translate_keys(iterable, cols):
    _iterable = list()

    for item in iterable:
        _item = dict(item)

        for colmap in cols:
            _item = rename_key(_item, *colmap)

        _iterable.append(_item)

    return _iterable


def translate_values(iterable, key, func):
    _iterable = list()

    for item in iterable:
        _item = dict(item)

        if key in _item:
            _item[key] = func(_item[key])

        _iterable.append(_item)

    return _iterable


def append_values(iterable, key, new_key, func):
    _iterable = list()

    for item in iterable:
        _dict = add_key(item, new_key, item[key])        
        _iterable.append(_dict)

    _iterable = translate_values(_iterable, new_key, func)
    return _iterable


def merge_dicts(src, dest):
    ndict = dict(src)
    ndict.update(dest)
    return ndict