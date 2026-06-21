# PWOS3 - Python WOW Operating System
# Copyright (c) 2024-2026 moyixi123-git
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# std_lib.py - PWOS3 超级增强标准库 v3.0 (硬件增强版)
import os, sys, json, time, random, hashlib, datetime, shutil, zipfile, tarfile
import re, base64, csv, sqlite3, subprocess, socket, platform, math, textwrap
import io, glob, fnmatch, tempfile, configparser, logging, string, secrets
import getpass, threading, queue, struct, itertools, collections, enum as enum_module
import heapq, bisect, functools, operator, inspect, copy, weakref, contextlib
import concurrent.futures, asyncio, typing, urllib.request, urllib.parse, urllib.error
from typing import Any, Dict, List, Tuple, Optional, Union, Callable, TypeVar, Generic, Iterator, Set, Iterable
from collections import OrderedDict, defaultdict, Counter, deque, namedtuple
from functools import wraps, partial, reduce, lru_cache
from contextlib import contextmanager
import traceback
import uuid as _uuid
import gzip
import zlib
import abc
import dataclasses
import enum
import warnings
import webbrowser
import smtplib
import email.mime.text
import email.mime.multipart
import email.mime.base
import email.encoders
import mimetypes
import hashlib
import hmac
import secrets
import tempfile
import filecmp
import difflib
import pickle
import shelve
import marshal
import array
import mmap
import codecs
import unicodedata
import html
import xml.etree.ElementTree as ET
import xml.dom.minidom
import json
try:
    import yaml
except ImportError:
    yaml = None

# ==================== 1. 基础类型增强 ====================

class Ptr:
    def __init__(self, value=None):
        self._value = value
    def get(self):
        return self._value
    def set(self, value):
        self._value = value
    def __call__(self):
        return self._value
    def __repr__(self):
        return f"Ptr({self._value})"

class SharedPtr:
    def __init__(self, value=None):
        self._value = value
        self._ref_count = 1
    def copy(self):
        self._ref_count += 1
        return self
    def release(self):
        self._ref_count -= 1
        if self._ref_count <= 0:
            self._value = None
    def get(self):
        return self._value

class WeakPtr:
    def __init__(self, obj):
        self._ref = weakref.ref(obj)
    def lock(self):
        return self._ref()
    def expired(self):
        return self._ref() is None

class UniquePtr:
    def __init__(self, value=None):
        self._value = value
    def get(self):
        return self._value
    def release(self):
        val = self._value
        self._value = None
        return val
    def reset(self, value=None):
        self._value = value
    def __bool__(self):
        return self._value is not None

class Ref:
    def __init__(self, obj):
        self._obj = obj
    def __getattr__(self, name):
        return getattr(self._obj, name)
    def __setattr__(self, name, value):
        if name == '_obj':
            super().__setattr__(name, value)
        else:
            setattr(self._obj, name, value)

class TypeInfo:
    @staticmethod
    def name(obj):
        return type(obj).__name__
    @staticmethod
    def size(obj):
        return sys.getsizeof(obj)
    @staticmethod
    def is_type(obj, t):
        return isinstance(obj, t)
    @staticmethod
    def cast(obj, t):
        return t(obj)
    @staticmethod
    def is_subclass(cls, parent):
        return issubclass(cls, parent)
    @staticmethod
    def methods(obj):
        return [m for m in dir(obj) if callable(getattr(obj, m)) and not m.startswith('_')]
    @staticmethod
    def attributes(obj):
        return [a for a in dir(obj) if not callable(getattr(obj, a)) and not a.startswith('_')]

class AnyType:
    def __init__(self, value=None):
        self._type = type(value) if value is not None else None
        self._value = value
    def has_value(self):
        return self._value is not None
    def type(self):
        return self._type.__name__ if self._type else "None"
    def get(self):
        return self._value
    def set(self, value):
        self._type = type(value)
        self._value = value

class Optional:
    def __init__(self, value=None):
        self._value = value
    def has_value(self):
        return self._value is not None
    def value(self):
        if self._value is None:
            raise ValueError("Optional has no value")
        return self._value
    def value_or(self, default):
        return self._value if self._value is not None else default
    def __bool__(self):
        return self._value is not None

class Variant:
    def __init__(self, value):
        self._value = value
    def index(self):
        return type(self._value).__name__
    def get(self, t):
        if isinstance(self._value, t):
            return self._value
        raise TypeError(f"Variant does not hold {t.__name__}")
    def __repr__(self):
        return f"Variant({self._value})"

class Result:
    def __init__(self, value=None, error=None):
        self._value = value
        self._error = error
    def is_ok(self):
        return self._error is None
    def is_err(self):
        return self._error is not None
    def unwrap(self):
        if self._error:
            raise Exception(f"Result error: {self._error}")
        return self._value
    def unwrap_err(self):
        if not self._error:
            raise Exception("Result is not an error")
        return self._error
    def map(self, func):
        if self.is_ok():
            return Result(func(self._value))
        return self
    def and_then(self, func):
        if self.is_ok():
            return func(self._value)
        return self
    def or_else(self, func):
        if self.is_err():
            return func(self._error)
        return self
    def __repr__(self):
        if self.is_ok():
            return f"Ok({self._value})"
        return f"Err({self._error})"

class Enum:
    def __init__(self, **kwargs):
        self._values = {}
        self._names = {}
        auto_counter = 0
        for key, value in kwargs.items():
            if value == "AUTO":
                value = auto_counter
                auto_counter += 1
            setattr(self, key, value)
            self._values[value] = key
            self._names[key] = value
    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]
    def keys(self):
        return [k for k, _ in self.items()]
    def values(self):
        return [v for _, v in self.items()]
    def get_name(self, value):
        return self._values.get(value, None)
    def get_value(self, name):
        return self._names.get(name, None)
    def contains_value(self, value):
        return value in self._values
    def contains_name(self, name):
        return name in self._names
    def __iter__(self):
        return iter(self.items())
    def __repr__(self):
        items = ', '.join(f"{k}={v}" for k, v in self.items())
        return f"Enum({items})"

class Namespace:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def __repr__(self):
        return f"Namespace({self.to_dict()})"

class Struct:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    def __repr__(self):
        items = ', '.join(f"{k}={v}" for k, v in self.to_dict().items())
        return f"Struct({items})"

# ==================== 2. 容器增强 ====================

class Vector:
    def __init__(self, data=None, capacity=10):
        self._data = list(data) if data else []
        self._capacity = max(len(self._data), capacity)
    def push_back(self, value):
        self._data.append(value)
    def pop_back(self):
        return self._data.pop() if self._data else None
    def at(self, index):
        if 0 <= index < len(self._data):
            return self._data[index]
        raise IndexError(f"Vector索引越界: {index}")
    def front(self):
        return self._data[0] if self._data else None
    def back(self):
        return self._data[-1] if self._data else None
    def size(self) -> int:
        return len(self._data)
    def capacity(self) -> int:
        return self._capacity
    def empty(self) -> bool:
        return len(self._data) == 0
    def clear(self):
        self._data.clear()
    def insert(self, index, value):
        self._data.insert(index, value)
    def erase(self, index):
        return self._data.pop(index)
    def reserve(self, capacity):
        self._capacity = capacity
    def data(self) -> list:
        return self._data.copy()
    def sort(self, key=None, reverse=False):
        self._data.sort(key=key, reverse=reverse)
    def find(self, value) -> int:
        try:
            return self._data.index(value)
        except ValueError:
            return -1
    def for_each(self, func):
        for item in self._data:
            func(item)
    def filter(self, predicate):
        return Vector([x for x in self._data if predicate(x)])
    def map(self, func):
        return Vector([func(x) for x in self._data])
    def reduce(self, func, initial=None):
        if initial is None:
            return functools.reduce(func, self._data)
        return functools.reduce(func, self._data, initial)
    def __getitem__(self, index):
        return self._data[index]
    def __setitem__(self, index, value):
        self._data[index] = value
    def __len__(self):
        return len(self._data)
    def __iter__(self):
        return iter(self._data)
    def __repr__(self):
        return f"Vector({self._data})"

class Deque:
    def __init__(self, data=None):
        self._data = deque(data or [])
    def push_front(self, value):
        self._data.appendleft(value)
    def push_back(self, value):
        self._data.append(value)
    def pop_front(self):
        return self._data.popleft() if self._data else None
    def pop_back(self):
        return self._data.pop() if self._data else None
    def front(self):
        return self._data[0] if self._data else None
    def back(self):
        return self._data[-1] if self._data else None
    def size(self):
        return len(self._data)
    def empty(self):
        return len(self._data) == 0
    def rotate(self, n):
        self._data.rotate(n)
    def __iter__(self):
        return iter(self._data)
    def __repr__(self):
        return f"Deque({list(self._data)})"

class ListNode:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

class List:
    def __init__(self, data=None):
        self._head = None
        self._tail = None
        self._size = 0
        if data:
            for item in data:
                self.push_back(item)
    def push_front(self, value):
        node = ListNode(value)
        if not self._head:
            self._head = self._tail = node
        else:
            node.next = self._head
            self._head.prev = node
            self._head = node
        self._size += 1
    def push_back(self, value):
        node = ListNode(value)
        if not self._tail:
            self._head = self._tail = node
        else:
            node.prev = self._tail
            self._tail.next = node
            self._tail = node
        self._size += 1
    def pop_front(self):
        if not self._head:
            return None
        value = self._head.value
        self._head = self._head.next
        if self._head:
            self._head.prev = None
        else:
            self._tail = None
        self._size -= 1
        return value
    def pop_back(self):
        if not self._tail:
            return None
        value = self._tail.value
        self._tail = self._tail.prev
        if self._tail:
            self._tail.next = None
        else:
            self._head = None
        self._size -= 1
        return value
    def front(self):
        return self._head.value if self._head else None
    def back(self):
        return self._tail.value if self._tail else None
    def size(self) -> int:
        return self._size
    def empty(self) -> bool:
        return self._size == 0
    def to_list(self) -> list:
        result = []
        current = self._head
        while current:
            result.append(current.value)
            current = current.next
        return result
    def find(self, value):
        current = self._head
        idx = 0
        while current:
            if current.value == value:
                return idx
            current = current.next
            idx += 1
        return -1

class Stack:
    def __init__(self):
        self._data = []
    def push(self, value):
        self._data.append(value)
    def pop(self):
        return self._data.pop() if self._data else None
    def top(self):
        return self._data[-1] if self._data else None
    def size(self) -> int:
        return len(self._data)
    def empty(self) -> bool:
        return len(self._data) == 0
    def clear(self):
        self._data.clear()

class Queue:
    def __init__(self):
        self._data = deque()
    def push(self, value):
        self._data.append(value)
    def pop(self):
        return self._data.popleft() if self._data else None
    def front(self):
        return self._data[0] if self._data else None
    def back(self):
        return self._data[-1] if self._data else None
    def size(self) -> int:
        return len(self._data)
    def empty(self) -> bool:
        return len(self._data) == 0
    def clear(self):
        self._data.clear()

class PriorityQueue:
    def __init__(self, max_heap=True, key=None):
        self._data = []
        self._max_heap = max_heap
        self._key = key
    def push(self, value):
        if self._key:
            priority = self._key(value)
        else:
            priority = value
        sign = -1 if self._max_heap else 1
        heapq.heappush(self._data, (sign * priority, value))
    def pop(self):
        return heapq.heappop(self._data)[1] if self._data else None
    def top(self):
        return self._data[0][1] if self._data else None
    def size(self) -> int:
        return len(self._data)
    def empty(self) -> bool:
        return len(self._data) == 0
    def clear(self):
        self._data.clear()

class Set:
    def __init__(self, data=None):
        self._data = []
        self._set = set()
        if data:
            for item in data:
                self.insert(item)
    def insert(self, value):
        if value not in self._set:
            self._set.add(value)
            self._data.append(value)
            self._data.sort()
    def erase(self, value):
        if value in self._set:
            self._set.remove(value)
            self._data.remove(value)
    def contains(self, value) -> bool:
        return value in self._set
    def size(self) -> int:
        return len(self._set)
    def empty(self) -> bool:
        return len(self._set) == 0
    def to_list(self) -> list:
        return self._data.copy()
    def clear(self):
        self._set.clear()
        self._data.clear()
    def __iter__(self):
        return iter(self._data)

class HashSet:
    def __init__(self, data=None):
        self._set = set(data) if data else set()
    def insert(self, value):
        self._set.add(value)
    def erase(self, value):
        self._set.discard(value)
    def contains(self, value):
        return value in self._set
    def size(self):
        return len(self._set)
    def empty(self):
        return len(self._set) == 0
    def clear(self):
        self._set.clear()
    def union(self, other):
        return HashSet(self._set | other._set)
    def intersection(self, other):
        return HashSet(self._set & other._set)
    def difference(self, other):
        return HashSet(self._set - other._set)
    def __iter__(self):
        return iter(self._set)

class Map:
    def __init__(self):
        self._dict = OrderedDict()
    def insert(self, key, value):
        self._dict[key] = value
    def erase(self, key):
        if key in self._dict:
            del self._dict[key]
    def contains(self, key) -> bool:
        return key in self._dict
    def at(self, key):
        if key in self._dict:
            return self._dict[key]
        raise KeyError(f"Map键不存在: {key}")
    def size(self) -> int:
        return len(self._dict)
    def keys(self) -> list:
        return list(self._dict.keys())
    def values(self) -> list:
        return list(self._dict.values())
    def items(self):
        return list(self._dict.items())
    def clear(self):
        self._dict.clear()
    def __getitem__(self, key):
        return self._dict[key]
    def __setitem__(self, key, value):
        self._dict[key] = value

class HashMap:
    def __init__(self):
        self._dict = {}
    def insert(self, key, value):
        self._dict[key] = value
    def get(self, key, default=None):
        return self._dict.get(key, default)
    def remove(self, key):
        return self._dict.pop(key, None)
    def contains(self, key):
        return key in self._dict
    def size(self):
        return len(self._dict)
    def keys(self):
        return list(self._dict.keys())
    def values(self):
        return list(self._dict.values())
    def items(self):
        return list(self._dict.items())
    def clear(self):
        self._dict.clear()
    def __getitem__(self, key):
        return self._dict[key]
    def __setitem__(self, key, value):
        self._dict[key] = value

class MultiSet:
    def __init__(self, data=None):
        self._data = sorted(data) if data else []
    def insert(self, value):
        bisect.insort(self._data, value)
    def erase(self, value):
        i = bisect.bisect_left(self._data, value)
        if i < len(self._data) and self._data[i] == value:
            self._data.pop(i)
    def count(self, value):
        return self._data.count(value)
    def lower_bound(self, value):
        return bisect.bisect_left(self._data, value)
    def upper_bound(self, value):
        return bisect.bisect_right(self._data, value)
    def to_list(self):
        return self._data.copy()
    def size(self):
        return len(self._data)
    def clear(self):
        self._data.clear()

class MultiMap:
    def __init__(self):
        self._data = []
    def insert(self, key, value):
        bisect.insort(self._data, (key, value))
    def erase(self, key, value=None):
        if value is None:
            self._data = [(k, v) for k, v in self._data if k != key]
        else:
            self._data.remove((key, value))
    def find_all(self, key):
        return [v for k, v in self._data if k == key]
    def count(self, key):
        return sum(1 for k, _ in self._data if k == key)
    def to_list(self):
        return self._data.copy()
    def size(self):
        return len(self._data)
    def clear(self):
        self._data.clear()

class StringView:
    def __init__(self, s: str):
        self._s = s
    def substr(self, pos, length=None):
        if length is None:
            return StringView(self._s[pos:])
        return StringView(self._s[pos:pos+length])
    def find(self, sub, start=0):
        return self._s.find(sub, start)
    def rfind(self, sub, start=0):
        return self._s.rfind(sub, start)
    def replace(self, old, new):
        return StringView(self._s.replace(old, new))
    def split(self, sep=None, maxsplit=-1):
        return [StringView(s) for s in self._s.split(sep, maxsplit)]
    def strip(self):
        return StringView(self._s.strip())
    def size(self):
        return len(self._s)
    def empty(self):
        return len(self._s) == 0
    def data(self):
        return self._s
    def __str__(self):
        return self._s
    def __repr__(self):
        return f"StringView({self._s!r})"

class Span:
    def __init__(self, data, start=0, length=None):
        self._data = data
        self._start = start
        self._length = length if length is not None else len(data) - start
    def at(self, index):
        if index < 0 or index >= self._length:
            raise IndexError("Span index out of range")
        return self._data[self._start + index]
    def size(self):
        return self._length
    def slice(self, start, length=None):
        return Span(self._data, self._start + start,
                    length if length is not None else self._length - start)
    def to_list(self):
        return self._data[self._start:self._start + self._length]
    def __getitem__(self, i):
        return self.at(i)
    def __iter__(self):
        for i in range(self._length):
            yield self._data[self._start + i]

class Pair:
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def __repr__(self):
        return f"Pair({self.first}, {self.second})"

class Tuple:
    def __init__(self, *args):
        self._data = args
    def get(self, index):
        return self._data[index]
    def size(self) -> int:
        return len(self._data)
    def __iter__(self):
        return iter(self._data)

# ==================== 3. 算法库 ====================

class Algo:
    @staticmethod
    def sort(data, reverse=False, key=None):
        if key is not None:
            return sorted(data, key=key, reverse=reverse)
        return sorted(data, reverse=reverse)
    
    @staticmethod
    def stable_sort(data, key=None, reverse=False):
        return sorted(data, key=key, reverse=reverse)
    
    @staticmethod
    def partial_sort(data, n, key=None):
        temp = data.copy()
        temp.sort(key=key)
        return temp[:n]
    
    @staticmethod
    def find(data, value):
        try:
            return data.index(value)
        except ValueError:
            return -1
    
    @staticmethod
    def find_if(data, predicate):
        for i, item in enumerate(data):
            if predicate(item):
                return i
        return -1
    
    @staticmethod
    def count(data, value):
        return data.count(value)
    
    @staticmethod
    def count_if(data, predicate):
        return sum(1 for item in data if predicate(item))
    
    @staticmethod
    def reverse(data):
        return data[::-1]
    
    @staticmethod
    def rotate(data, n):
        n = n % len(data)
        return data[n:] + data[:n]
    
    @staticmethod
    def shuffle(data):
        result = data.copy()
        random.shuffle(result)
        return result
    
    @staticmethod
    def unique(data):
        return list(dict.fromkeys(data))
    
    @staticmethod
    def replace(data, old, new):
        return [new if x == old else x for x in data]
    
    @staticmethod
    def remove_if(data, predicate):
        return [x for x in data if not predicate(x)]
    
    @staticmethod
    def transform(data, func):
        return list(map(func, data))
    
    @staticmethod
    def for_each(data, func):
        for item in data:
            func(item)
    
    @staticmethod
    def fill(data, value):
        return [value] * len(data)
    
    @staticmethod
    def generate(n, func):
        return [func() for _ in range(n)]
    
    @staticmethod
    def min_element(data, key=None):
        return min(data, key=key) if data else None
    
    @staticmethod
    def max_element(data, key=None):
        return max(data, key=key) if data else None
    
    @staticmethod
    def min_max(data, key=None):
        if not data:
            return (None, None)
        return (min(data, key=key), max(data, key=key))
    
    @staticmethod
    def binary_search(data, value):
        data = sorted(data)
        i = bisect.bisect_left(data, value)
        return i < len(data) and data[i] == value
    
    @staticmethod
    def lower_bound(data, value):
        return bisect.bisect_left(sorted(data), value)
    
    @staticmethod
    def upper_bound(data, value):
        return bisect.bisect_right(sorted(data), value)
    
    @staticmethod
    def next_permutation(data):
        i = len(data) - 2
        while i >= 0 and data[i] >= data[i + 1]:
            i -= 1
        if i >= 0:
            j = len(data) - 1
            while data[j] <= data[i]:
                j -= 1
            data[i], data[j] = data[j], data[i]
        data[i + 1:] = reversed(data[i + 1:])
        return data
    
    @staticmethod
    def merge(a, b, key=None):
        result = []
        i = j = 0
        while i < len(a) and j < len(b):
            if (key(a[i]) if key else a[i]) <= (key(b[j]) if key else b[j]):
                result.append(a[i])
                i += 1
            else:
                result.append(b[j])
                j += 1
        result.extend(a[i:])
        result.extend(b[j:])
        return result
    
    @staticmethod
    def set_union(a, b):
        return list(set(a) | set(b))
    
    @staticmethod
    def set_intersection(a, b):
        return list(set(a) & set(b))
    
    @staticmethod
    def set_difference(a, b):
        return list(set(a) - set(b))
    
    @staticmethod
    def is_sorted(data, key=None, reverse=False):
        if not data:
            return True
        it = iter(data)
        prev = next(it)
        for cur in it:
            if key:
                p, c = key(prev), key(cur)
            else:
                p, c = prev, cur
            if (not reverse and p > c) or (reverse and p < c):
                return False
            prev = cur
        return True
    
    @staticmethod
    def clamp(value, lo, hi):
        return max(lo, min(value, hi))
    
    @staticmethod
    def sample(data, k):
        return random.sample(data, k)
    
    @staticmethod
    def partition(data, predicate):
        true_list = [x for x in data if predicate(x)]
        false_list = [x for x in data if not predicate(x)]
        return true_list, false_list
    
    @staticmethod
    def quick_sort(data, key=None, reverse=False):
        if len(data) <= 1:
            return data
        pivot = data[0]
        left = [x for x in data[1:] if (key(x) if key else x) <= (key(pivot) if key else pivot)]
        right = [x for x in data[1:] if (key(x) if key else x) > (key(pivot) if key else pivot)]
        if reverse:
            return Algo.quick_sort(right, key, reverse) + [pivot] + Algo.quick_sort(left, key, reverse)
        return Algo.quick_sort(left, key, reverse) + [pivot] + Algo.quick_sort(right, key, reverse)
    
    @staticmethod
    def all_of(data, predicate):
        return all(predicate(x) for x in data)
    
    @staticmethod
    def any_of(data, predicate):
        return any(predicate(x) for x in data)
    
    @staticmethod
    def none_of(data, predicate):
        return not any(predicate(x) for x in data)
    
    @staticmethod
    def adjacent_find(data, predicate=None):
        for i in range(len(data) - 1):
            if predicate is None:
                if data[i] == data[i+1]:
                    return i
            elif predicate(data[i], data[i+1]):
                return i
        return -1
    
    @staticmethod
    def mismatch(a, b, predicate=None):
        n = min(len(a), len(b))
        for i in range(n):
            if predicate is None:
                if a[i] != b[i]:
                    return i
            elif not predicate(a[i], b[i]):
                return i
        return n if len(a) == len(b) else -1

# ==================== 4. Range 类 ====================

class Range:
    def __init__(self, start, end=None, step=1):
        if end is None:
            self._start = 0
            self._end = start
        else:
            self._start = start
            self._end = end
        self._step = step
    def to_list(self):
        return list(self)
    def to_vector(self):
        return Vector(list(self))
    def filter(self, predicate):
        return [x for x in self if predicate(x)]
    def map(self, func):
        return [func(x) for x in self]
    def reduce(self, func, initial=None):
        it = iter(self)
        value = initial if initial is not None else next(it)
        for x in it:
            value = func(value, x)
        return value
    def sum(self):
        return sum(self)
    def product(self):
        result = 1
        for x in self:
            result *= x
        return result
    def count(self):
        return len(list(self))
    def __iter__(self):
        return iter(range(self._start, self._end, self._step))
    def __repr__(self):
        return f"Range({self._start}, {self._end}, {self._step})"

class Range2D:
    def __init__(self, x_start, x_end, y_start, y_end, x_step=1, y_step=1):
        self.x_range = Range(x_start, x_end, x_step)
        self.y_range = Range(y_start, y_end, y_step)
    def to_list(self):
        return [(x, y) for x in self.x_range for y in self.y_range]
    def __iter__(self):
        for x in self.x_range:
            for y in self.y_range:
                yield x, y

# ==================== 5. JSON 增强 ====================

class JSON:
    @staticmethod
    def parse(text):
        return json.loads(text)
    @staticmethod
    def stringify(obj, indent=2):
        return json.dumps(obj, ensure_ascii=False, indent=indent)
    @staticmethod
    def stringify_compact(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    @staticmethod
    def read(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    @staticmethod
    def write(filepath, data, indent=2):
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    @staticmethod
    def pretty_print(obj):
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    @staticmethod
    def validate(text):
        try:
            json.loads(text)
            return True
        except:
            return False
    @staticmethod
    def merge(a, b):
        result = a.copy()
        for key, value in b.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = JSON.merge(result[key], value)
            else:
                result[key] = value
        return result

# ==================== 6. HTTP 客户端 ====================

class HTTP:
    @staticmethod
    def get(url, headers=None, timeout=30):
        req = urllib.request.Request(url, headers=headers or {'User-Agent': 'PWOS3/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8')
    @staticmethod
    def get_json(url, headers=None, timeout=30):
        return json.loads(HTTP.get(url, headers, timeout))
    @staticmethod
    def post(url, data=None, headers=None, timeout=30):
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
            headers = headers or {}
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=data, headers=headers or {}, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8')
    @staticmethod
    def post_json(url, data, headers=None, timeout=30):
        headers = headers or {}
        headers['Content-Type'] = 'application/json'
        return HTTP.post(url, json.dumps(data).encode('utf-8'), headers, timeout)
    @staticmethod
    def download(url, save_path, timeout=30):
        urllib.request.urlretrieve(url, save_path)
        return True
    @staticmethod
    def head(url, timeout=30):
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return dict(resp.headers)
    @staticmethod
    def status(url, timeout=30):
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status
        except urllib.error.URLError:
            return None

# ==================== 7. 加密工具 ====================

class Crypto:
    @staticmethod
    def md5(text):
        return hashlib.md5(text.encode()).hexdigest()
    @staticmethod
    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()
    @staticmethod
    def sha1(text):
        return hashlib.sha1(text.encode()).hexdigest()
    @staticmethod
    def sha512(text):
        return hashlib.sha512(text.encode()).hexdigest()
    @staticmethod
    def base64_encode(text):
        return base64.b64encode(text.encode()).decode()
    @staticmethod
    def base64_decode(text):
        return base64.b64decode(text.encode()).decode()
    @staticmethod
    def base64_url_encode(text):
        return base64.urlsafe_b64encode(text.encode()).decode().rstrip('=')
    @staticmethod
    def base64_url_decode(text):
        padding = 4 - len(text) % 4
        if padding != 4:
            text += '=' * padding
        return base64.urlsafe_b64decode(text).decode()
    @staticmethod
    def random_token(length=32):
        return secrets.token_hex(length)
    @staticmethod
    def random_string(length=8):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    @staticmethod
    def hmac_sha256(key, message):
        return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()
    @staticmethod
    def hmac_md5(key, message):
        return hmac.new(key.encode(), message.encode(), hashlib.md5).hexdigest()
    @staticmethod
    def aes_encrypt(key, data):
        try:
            from cryptography.fernet import Fernet
            import base64
            if len(key) < 32:
                key = hashlib.sha256(key.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key[:32])
            f = Fernet(fernet_key)
            return f.encrypt(data.encode() if isinstance(data, str) else data)
        except ImportError:
            raise ImportError("需要安装 cryptography 库: pip install cryptography")
    @staticmethod
    def aes_decrypt(key, encrypted):
        try:
            from cryptography.fernet import Fernet
            import base64
            if len(key) < 32:
                key = hashlib.sha256(key.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key[:32])
            f = Fernet(fernet_key)
            return f.decrypt(encrypted).decode()
        except ImportError:
            raise ImportError("需要安装 cryptography 库: pip install cryptography")

# ==================== 8. 表格美化 ====================

class Table:
    def __init__(self, headers=None):
        self.headers = headers or []
        self.rows = []
        self.alignments = {}
    def add_row(self, row):
        self.rows.append(row)
    def add_rows(self, rows):
        self.rows.extend(rows)
    def set_alignment(self, col, align='left'):
        self.alignments[col] = align
    def clear(self):
        self.rows.clear()
    def print(self):
        if not self.headers and not self.rows:
            return
        col_widths = []
        if self.headers:
            col_widths = [len(str(h)) for h in self.headers]
        for row in self.rows:
            for i, cell in enumerate(row):
                if i >= len(col_widths):
                    col_widths.append(0)
                col_widths[i] = max(col_widths[i], len(str(cell)))
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
        if self.headers:
            print(separator)
            header_line = "| "
            for i, (h, w) in enumerate(zip(self.headers, col_widths)):
                align = self.alignments.get(i, 'left')
                if align == 'right':
                    header_line += str(h).rjust(w) + " | "
                elif align == 'center':
                    header_line += str(h).center(w) + " | "
                else:
                    header_line += str(h).ljust(w) + " | "
            print(header_line)
        print(separator)
        for row in self.rows:
            line = "| "
            for i, (cell, w) in enumerate(zip(row, col_widths)):
                align = self.alignments.get(i, 'left')
                if align == 'right':
                    line += str(cell).rjust(w) + " | "
                elif align == 'center':
                    line += str(cell).center(w) + " | "
                else:
                    line += str(cell).ljust(w) + " | "
            print(line)
        print(separator)
    def to_string(self):
        output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output
        self.print()
        sys.stdout = old_stdout
        return output.getvalue()

# ==================== 9. 进度条 ====================

class ProgressBar:
    def __init__(self, total, width=50, prefix="Progress", suffix="Complete", color=True):
        self.total = total
        self.width = width
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        self.color = color
        self.start_time = time.time()
    def update(self, n=1):
        self.current += n
        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = "█" * filled + "░" * (self.width - filled)
        if self.color:
            if percent < 0.5:
                bar = f"\033[93m{bar}\033[0m"
            elif percent < 0.8:
                bar = f"\033[96m{bar}\033[0m"
            else:
                bar = f"\033[92m{bar}\033[0m"
        elapsed = time.time() - self.start_time
        if self.current > 0 and percent > 0:
            eta = elapsed / percent * (1 - percent)
            eta_str = f"ETA: {int(eta)}s"
        else:
            eta_str = ""
        print(f"\r{self.prefix}: |{bar}| {self.current}/{self.total} {percent*100:.1f}% {eta_str} {self.suffix}", end="", flush=True)
        if self.current >= self.total:
            print()
    def reset(self):
        self.current = 0
        self.start_time = time.time()

# ==================== 10. 配置管理 ====================

class Config:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self._config = {}
        if filepath and os.path.exists(filepath):
            self.load(filepath)
    def load(self, filepath=None):
        path = filepath or self.filepath
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.json'):
                    self._config = json.load(f)
                elif path.endswith('.yaml') or path.endswith('.yml'):
                    if yaml:
                        self._config = yaml.safe_load(f) or {}
                    else:
                        raise ImportError("PyYAML not installed")
                else:
                    self._config = json.loads(f.read())
        return self
    def save(self, filepath=None):
        path = filepath or self.filepath
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                if path.endswith('.yaml') or path.endswith('.yml'):
                    if yaml:
                        yaml.dump(self._config, f, allow_unicode=True)
                    else:
                        raise ImportError("PyYAML not installed")
                else:
                    json.dump(self._config, f, ensure_ascii=False, indent=2)
    def get(self, key, default=None):
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    def set(self, key, value):
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        return self
    def has(self, key):
        return self.get(key) is not None
    def all(self):
        return self._config.copy()
    def delete(self, key):
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                return
            config = config[k]
        if keys[-1] in config:
            del config[keys[-1]]
    def __getitem__(self, key):
        return self.get(key)
    def __setitem__(self, key, value):
        self.set(key, value)

# ==================== 11. 日志工具 ====================

class Logger:
    LEVELS = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "FATAL": 4}
    COLORS = {
        "DEBUG": "\033[90m",
        "INFO": "\033[92m",
        "WARN": "\033[93m",
        "ERROR": "\033[91m",
        "FATAL": "\033[95m"
    }
    def __init__(self, name="app", level="INFO", color=True, log_file=None):
        self.name = name
        self.level = self.LEVELS.get(level.upper(), 1)
        self.color = color
        self.log_file = log_file
        if log_file:
            os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
    def _log(self, level, msg, color_func=None):
        if self.LEVELS[level] >= self.level:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            log_msg = f"[{timestamp}] [{level}] [{self.name}] {msg}"
            if self.color and color_func:
                log_msg = color_func(log_msg)
            print(log_msg)
            if self.log_file:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_msg + '\n')
    def debug(self, msg):
        self._log("DEBUG", msg, lambda x: f"{self.COLORS['DEBUG']}{x}\033[0m")
    def info(self, msg):
        self._log("INFO", msg, lambda x: f"{self.COLORS['INFO']}{x}\033[0m")
    def warn(self, msg):
        self._log("WARN", msg, lambda x: f"{self.COLORS['WARN']}{x}\033[0m")
    def error(self, msg):
        self._log("ERROR", msg, lambda x: f"{self.COLORS['ERROR']}{x}\033[0m")
    def fatal(self, msg):
        self._log("FATAL", msg, lambda x: f"{self.COLORS['FATAL']}{x}\033[0m")

# ==================== 12. 系统工具 ====================

class Memory:
    @staticmethod
    def alloc(size):
        return bytearray(size)
    @staticmethod
    def memset(data, value, count=None):
        if count is None:
            count = len(data)
        for i in range(count):
            data[i] = value & 0xFF
    @staticmethod
    def memcpy(dst, src, count):
        dst[:count] = src[:count]
    @staticmethod
    def memcmp(a, b):
        return 1 if a > b else (-1 if a < b else 0)
    @staticmethod
    def size_of(obj):
        return sys.getsizeof(obj)
    @staticmethod
    def hex_dump(data, bytes_per_line=16):
        result = []
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i+bytes_per_line]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            result.append(f'{i:08x}  {hex_str:<{bytes_per_line*3}}  {ascii_str}')
        return '\n'.join(result)

class IOStream:
    @staticmethod
    def read_line(prompt=""):
        return input(prompt)
    @staticmethod
    def read_int(prompt=""):
        return int(input(prompt))
    @staticmethod
    def read_float(prompt=""):
        return float(input(prompt))
    @staticmethod
    def write(*args, **kwargs):
        print(*args, **kwargs)
    @staticmethod
    def error(*args):
        print(*args, file=sys.stderr)
    @staticmethod
    def format(fmt, *args):
        return fmt % args if args else fmt
    @staticmethod
    def printf(fmt, *args):
        print(fmt % args if args else fmt, end='')

class StringStream:
    def __init__(self, s=""):
        self._buffer = io.StringIO(s)
    def write(self, s):
        self._buffer.write(s)
    def read(self):
        return self._buffer.read()
    def readline(self):
        return self._buffer.readline()
    def str(self):
        return self._buffer.getvalue()
    def seek(self, pos):
        self._buffer.seek(pos)
    def tell(self):
        return self._buffer.tell()

class FileStream:
    def __init__(self, filepath, mode='r'):
        self._filepath = filepath
        self._mode = mode
        self._handle = None
    def open(self, filepath=None, mode=None):
        if filepath: self._filepath = filepath
        if mode: self._mode = mode
        self._handle = open(self._filepath, self._mode)
        return self
    def close(self):
        if self._handle: self._handle.close()
    def read(self, size=-1):
        return self._handle.read(size) if self._handle else ''
    def read_line(self):
        return self._handle.readline() if self._handle else ''
    def read_lines(self):
        return self._handle.readlines() if self._handle else []
    def write(self, data):
        if self._handle: self._handle.write(data)
    def writelines(self, lines):
        if self._handle: self._handle.writelines(lines)
    def flush(self):
        if self._handle: self._handle.flush()
    def seek(self, pos):
        if self._handle: self._handle.seek(pos)
    def tell(self):
        return self._handle.tell() if self._handle else 0
    def eof(self):
        if not self._handle: return True
        pos = self._handle.tell()
        data = self._handle.read(1)
        self._handle.seek(pos)
        return not data
    def __enter__(self):
        self.open()
        return self
    def __exit__(self, *args):
        self.close()

class Chrono:
    def __init__(self):
        self._start = time.time()
    def reset(self):
        self._start = time.time()
    def elapsed(self):
        return time.time() - self._start
    def elapsed_ms(self):
        return int((time.time() - self._start) * 1000)
    def elapsed_us(self):
        return int((time.time() - self._start) * 1000000)
    @staticmethod
    def now():
        return time.time()
    @staticmethod
    def sleep_for(seconds):
        time.sleep(seconds)

class Duration:
    def __init__(self, seconds):
        self._sec = seconds
    def count(self):
        return self._sec
    def to_milliseconds(self):
        return int(self._sec * 1000)
    def to_minutes(self):
        return self._sec / 60
    def to_hours(self):
        return self._sec / 3600
    def to_days(self):
        return self._sec / 86400
    def __repr__(self):
        return f"Duration({self._sec}s)"

class Bitset:
    def __init__(self, size_or_value, size=None):
        if size is not None:
            self._size = size
            self._value = int(size_or_value)
        else:
            self._value = int(size_or_value) if isinstance(size_or_value, (int, str)) else 0
            self._size = max(8, self._value.bit_length())
    def set(self, pos, value=True):
        if 0 <= pos < self._size:
            if value: self._value |= (1 << pos)
            else: self._value &= ~(1 << pos)
    def get(self, pos):
        return bool(self._value & (1 << pos)) if 0 <= pos < self._size else False
    def flip(self, pos=None):
        if pos is not None: self._value ^= (1 << pos)
        else: self._value = ~self._value
    def count(self):
        return bin(self._value).count('1')
    def size(self):
        return self._size
    def to_int(self):
        return self._value
    def to_binary(self):
        return bin(self._value)[2:].zfill(self._size)
    def to_hex(self):
        return hex(self._value)[2:].upper()

class Regex:
    def __init__(self, pattern, flags=0):
        self._compiled = re.compile(pattern, flags)
    def match(self, text):
        return self._compiled.search(text)
    def matches(self, text):
        return self._compiled.fullmatch(text) is not None
    def find_all(self, text):
        return self._compiled.findall(text)
    def find_iter(self, text):
        return self._compiled.finditer(text)
    def replace(self, text, repl):
        return self._compiled.sub(repl, text)
    def replace_n(self, text, repl, count):
        return self._compiled.subn(repl, text, count)
    def split(self, text, maxsplit=0):
        return self._compiled.split(text, maxsplit)

class RandomEngine:
    def __init__(self, seed=None):
        self._rng = random.Random(seed)
    def uniform_int(self, a, b):
        return self._rng.randint(a, b)
    def uniform_real(self, a, b):
        return self._rng.uniform(a, b)
    def normal(self, mu=0, sigma=1):
        return self._rng.gauss(mu, sigma)
    def choice(self, seq):
        return self._rng.choice(seq)
    def choices(self, seq, k=1, weights=None):
        return self._rng.choices(seq, weights=weights, k=k)
    def shuffle(self, seq):
        self._rng.shuffle(seq)
    def sample(self, seq, k):
        return self._rng.sample(seq, k)
    def random(self):
        return self._rng.random()
    def seed(self, seed):
        self._rng.seed(seed)

class Thread:
    def __init__(self, target, args=(), kwargs={}):
        self._thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    def start(self):
        self._thread.start()
    def join(self, timeout=None):
        self._thread.join(timeout)
    def is_alive(self):
        return self._thread.is_alive()
    def get_id(self):
        return self._thread.ident

class Mutex:
    def __init__(self):
        self._lock = threading.Lock()
    def lock(self):
        self._lock.acquire()
    def unlock(self):
        self._lock.release()
    def try_lock(self):
        return self._lock.acquire(blocking=False)

class ConditionVariable:
    def __init__(self):
        self._cond = threading.Condition()
    def wait(self, predicate=None):
        with self._cond:
            if predicate: self._cond.wait_for(predicate)
            else: self._cond.wait()
    def notify_one(self):
        with self._cond:
            self._cond.notify(n=1)
    def notify_all(self):
        with self._cond:
            self._cond.notify_all()

class AsyncExecutor:
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4)
    @staticmethod
    def run(func, *args, **kwargs):
        return AsyncExecutor._executor.submit(func, *args, **kwargs)
    @staticmethod
    def map(func, *iterables):
        return AsyncExecutor._executor.map(func, *iterables)
    @staticmethod
    def shutdown(wait=True):
        AsyncExecutor._executor.shutdown(wait=wait)

class Future:
    def __init__(self, cf):
        self._cf = cf
    def get(self, timeout=None):
        return self._cf.result(timeout)
    def wait(self, timeout=None):
        concurrent.futures.wait([self._cf], timeout)
    def done(self):
        return self._cf.done()
    def cancel(self):
        return self._cf.cancel()
    def add_done_callback(self, fn):
        self._cf.add_done_callback(fn)
    @staticmethod
    def all(futures):
        concurrent.futures.wait([f._cf for f in futures])
    @staticmethod
    def first(futures):
        return concurrent.futures.wait([f._cf for f in futures], return_when=concurrent.futures.FIRST_COMPLETED)

class Path:
    def __init__(self, path):
        self._path = os.path.normpath(path)
    def exists(self):
        return os.path.exists(self._path)
    def is_file(self):
        return os.path.isfile(self._path)
    def is_dir(self):
        return os.path.isdir(self._path)
    def is_absolute(self):
        return os.path.isabs(self._path)
    def size(self):
        return os.path.getsize(self._path)
    def name(self):
        return os.path.basename(self._path)
    def stem(self):
        return os.path.splitext(self.name())[0]
    def suffix(self):
        return os.path.splitext(self.name())[1]
    def parent(self):
        return Path(os.path.dirname(self._path))
    def child(self, *parts):
        return Path(os.path.join(self._path, *parts))
    def resolve(self):
        return Path(os.path.abspath(self._path))
    def glob(self, pattern):
        return [Path(p) for p in glob.glob(os.path.join(self._path, pattern))]
    def rglob(self, pattern):
        return [Path(p) for p in glob.glob(os.path.join(self._path, '**', pattern), recursive=True)]
    def mkdir(self, exist_ok=True):
        os.makedirs(self._path, exist_ok=exist_ok)
    def remove(self):
        if self.is_file(): os.remove(self._path)
        elif self.is_dir(): shutil.rmtree(self._path)
    def rename(self, new_name):
        os.rename(self._path, new_name)
    def __str__(self):
        return self._path
    def __repr__(self):
        return f"Path({self._path!r})"

class ArrayList:
    def __init__(self, data=None):
        self._data = list(data or [])
    def add(self, value):
        self._data.append(value)
    def get(self, index):
        return self._data[index]
    def set(self, index, value):
        self._data[index] = value
    def remove(self, index):
        return self._data.pop(index)
    def size(self):
        return len(self._data)
    def contains(self, value):
        return value in self._data
    def to_list(self):
        return self._data.copy()
    def iterator(self):
        return Iterator(self._data)
    def __repr__(self):
        return f"ArrayList({self._data})"

class LinkedList:
    def __init__(self, data=None):
        self._list = List(data or [])
    def add_first(self, value):
        self._list.push_front(value)
    def add_last(self, value):
        self._list.push_back(value)
    def remove_first(self):
        return self._list.pop_front()
    def remove_last(self):
        return self._list.pop_back()
    def get_first(self):
        return self._list.front()
    def get_last(self):
        return self._list.back()
    def size(self):
        return self._list.size()
    def to_list(self):
        return self._list.to_list()

class Enumerable:
    def __init__(self, sequence):
        self._seq = sequence
    def where(self, predicate):
        return Enumerable(filter(predicate, self._seq))
    def select(self, selector):
        return Enumerable(map(selector, self._seq))
    def select_many(self, selector):
        result = []
        for item in self._seq:
            result.extend(selector(item))
        return Enumerable(result)
    def order_by(self, key):
        return Enumerable(sorted(self._seq, key=key))
    def order_by_desc(self, key):
        return Enumerable(sorted(self._seq, key=key, reverse=True))
    def then_by(self, key):
        return Enumerable(sorted(self._seq, key=lambda x: (self._get_key(x), key(x))))
    def first(self, predicate=None):
        for item in self._seq:
            if predicate is None or predicate(item):
                return item
        raise ValueError("No element")
    def first_or_default(self, predicate=None, default=None):
        try:
            return self.first(predicate)
        except ValueError:
            return default
    def last(self, predicate=None):
        result = None
        found = False
        for item in self._seq:
            if predicate is None or predicate(item):
                result = item
                found = True
        if not found:
            raise ValueError("No element")
        return result
    def count(self, predicate=None):
        if predicate:
            return sum(1 for x in self._seq if predicate(x))
        return sum(1 for _ in self._seq)
    def any(self, predicate=None):
        if predicate:
            return any(predicate(x) for x in self._seq)
        return any(True for _ in self._seq)
    def all(self, predicate):
        return all(predicate(x) for x in self._seq)
    def to_list(self):
        return list(self._seq)
    def to_vector(self):
        return Vector(self._seq)
    def aggregate(self, seed, func):
        result = seed
        for item in self._seq:
            result = func(result, item)
        return result
    def distinct(self):
        seen = set()
        result = []
        for x in self._seq:
            if x not in seen:
                seen.add(x)
                result.append(x)
        return Enumerable(result)
    def skip(self, n):
        it = iter(self._seq)
        for _ in range(n):
            try: next(it)
            except StopIteration: return Enumerable([])
        return Enumerable(list(it))
    def take(self, n):
        return Enumerable(list(itertools.islice(self._seq, n)))
    def group_by(self, key_selector):
        result = defaultdict(list)
        for item in self._seq:
            result[key_selector(item)].append(item)
        return Enumerable(result.items())

class Promise:
    PENDING = 'pending'
    FULFILLED = 'fulfilled'
    REJECTED = 'rejected'
    def __init__(self, executor):
        self._state = Promise.PENDING
        self._value = None
        self._callbacks = []
        try:
            executor(self._resolve, self._reject)
        except Exception as e:
            self._reject(e)
    def _resolve(self, value):
        if self._state != Promise.PENDING: return
        self._state = Promise.FULFILLED
        self._value = value
        for on_fulfilled, _ in self._callbacks:
            if on_fulfilled: on_fulfilled(self._value)
    def _reject(self, reason):
        if self._state != Promise.PENDING: return
        self._state = Promise.REJECTED
        self._value = reason
        for _, on_rejected in self._callbacks:
            if on_rejected: on_rejected(self._value)
    def then(self, on_fulfilled=None, on_rejected=None):
        if self._state == Promise.FULFILLED and on_fulfilled:
            on_fulfilled(self._value)
        elif self._state == Promise.REJECTED and on_rejected:
            on_rejected(self._value)
        else:
            self._callbacks.append((on_fulfilled, on_rejected))
        return self
    def catch(self, on_rejected):
        return self.then(None, on_rejected)
    @staticmethod
    def resolve(value):
        return Promise(lambda res, _: res(value))
    @staticmethod
    def reject(reason):
        return Promise(lambda _, rej: rej(reason))
    @staticmethod
    def all(promises):
        def handler(res, rej):
            results = [None] * len(promises)
            completed = 0
            for i, p in enumerate(promises):
                p.then(
                    lambda r, i=i: (results.__setitem__(i, r), (completed := completed + 1) or (completed == len(promises) and res(results))),
                    rej
                )
        return Promise(handler)

class Iterator:
    def __init__(self, data):
        self._data = data
        self._index = 0
    def has_next(self):
        return self._index < len(self._data)
    def next(self):
        if self.has_next():
            value = self._data[self._index]
            self._index += 1
            return value
        raise StopIteration()
    def reset(self):
        self._index = 0
    def __iter__(self):
        return self
    def __next__(self):
        return self.next()

class Const:
    def __init__(self, value):
        object.__setattr__(self, '_value', value)
    def __getattr__(self, name):
        return getattr(self._value, name)
    def __setattr__(self, name, value):
        raise AttributeError("常量不可修改")
    def __delattr__(self, name):
        raise AttributeError("常量不可删除")
    def __call__(self):
        return self._value

def constexpr(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return Const(func(*args, **kwargs))
    return wrapper

class Template:
    @staticmethod
    def max(a, b):
        return a if a > b else b
    @staticmethod
    def min(a, b):
        return a if a < b else b
    @staticmethod
    def swap(a, b):
        return b, a
    @staticmethod
    def clamp(value, lo, hi):
        return max(lo, min(value, hi))

# ==================== 13. 文件工具类 ====================

class File:
    @staticmethod
    def _get_base_dir():
        try:
            import __main__
            if hasattr(__main__, '__file__'):
                return os.path.dirname(os.path.abspath(__main__.__file__))
        except: pass
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        cwd = os.getcwd()
        if 'system32' in cwd.lower():
            return os.path.expanduser('~')
        return cwd
    
    @staticmethod
    def get_abs_path(filepath):
        if os.path.isabs(filepath): return filepath
        return os.path.join(File._get_base_dir(), filepath)
    
    @staticmethod
    def read(filepath, encoding='utf-8'):
        full = File.get_abs_path(filepath)
        try:
            with open(full, 'r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            return f"[文件不存在: {full}]"
        except Exception as e:
            return f"[错误: {e}]"
    
    @staticmethod
    def read_binary(filepath):
        full = File.get_abs_path(filepath)
        with open(full, 'rb') as f:
            return f.read()
    
    @staticmethod
    def write(filepath, content, encoding='utf-8'):
        full = File.get_abs_path(filepath)
        try:
            os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
            with open(full, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except:
            return False
    
    @staticmethod
    def write_binary(filepath, content):
        full = File.get_abs_path(filepath)
        try:
            os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
            with open(full, 'wb') as f:
                f.write(content)
            return True
        except:
            return False
    
    @staticmethod
    def append(filepath, content, encoding='utf-8'):
        full = File.get_abs_path(filepath)
        try:
            os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
            with open(full, 'a', encoding=encoding) as f:
                f.write(content)
            return True
        except:
            return False
    
    @staticmethod
    def read_json(filepath):
        full = File.get_abs_path(filepath)
        with open(full, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(filepath, data, indent=2):
        full = File.get_abs_path(filepath)
        os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    
    @staticmethod
    def exists(filepath):
        return os.path.exists(File.get_abs_path(filepath))
    
    @staticmethod
    def list_dir(directory='.', pattern='*'):
        full = File.get_abs_path(directory)
        return glob.glob(os.path.join(full, pattern))
    
    @staticmethod
    def mkdir(directory):
        os.makedirs(File.get_abs_path(directory), exist_ok=True)
        return True
    
    @staticmethod
    def copy(src, dst):
        try:
            src_full = File.get_abs_path(src)
            dst_full = File.get_abs_path(dst)
            if os.path.isdir(src_full): shutil.copytree(src_full, dst_full, dirs_exist_ok=True)
            else: shutil.copy2(src_full, dst_full)
            return True
        except:
            return False
    
    @staticmethod
    def delete(filepath):
        try:
            full = File.get_abs_path(filepath)
            if os.path.isdir(full): shutil.rmtree(full)
            else: os.remove(full)
            return True
        except:
            return False
    
    @staticmethod
    def size(filepath):
        full = File.get_abs_path(filepath)
        return os.path.getsize(full) if os.path.exists(full) else 0
    
    @staticmethod
    def lines(filepath, encoding='utf-8'):
        full = File.get_abs_path(filepath)
        with open(full, 'r', encoding=encoding) as f:
            return f.readlines()
    
    @staticmethod
    def walk(directory='.'):
        full = File.get_abs_path(directory)
        result = []
        for root, dirs, files in os.walk(full):
            result.append((root, dirs, files))
        return result
    
    @staticmethod
    def touch(filepath):
        full = File.get_abs_path(filepath)
        os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
        with open(full, 'a'):
            os.utime(full, None)
        return True
    
    @staticmethod
    def get_mtime(filepath):
        full = File.get_abs_path(filepath)
        return os.path.getmtime(full) if os.path.exists(full) else None
    
    @staticmethod
    def get_ctime(filepath):
        full = File.get_abs_path(filepath)
        return os.path.getctime(full) if os.path.exists(full) else None

# ==================== 14. 字符串工具类 ====================

class String:
    @staticmethod
    def md5(text):
        return hashlib.md5(text.encode()).hexdigest()
    @staticmethod
    def sha256(text):
        return hashlib.sha256(text.encode()).hexdigest()
    @staticmethod
    def sha1(text):
        return hashlib.sha1(text.encode()).hexdigest()
    @staticmethod
    def random(length=8):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    @staticmethod
    def truncate(s, length):
        return s[:length] + '...' if len(s) > length else s
    @staticmethod
    def truncate_middle(s, length):
        if len(s) <= length:
            return s
        half = (length - 3) // 2
        return s[:half] + '...' + s[-half:]
    @staticmethod
    def capitalize_first(s):
        return s[0].upper() + s[1:] if s else s
    @staticmethod
    def to_snake_case(s):
        s = re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
        return re.sub(r'[^a-z0-9_]', '_', s)
    @staticmethod
    def to_camel_case(s):
        parts = re.split(r'[_-]+', s)
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])
    @staticmethod
    def to_kebab_case(s):
        return String.to_snake_case(s).replace('_', '-')
    @staticmethod
    def is_email(s):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, s) is not None
    @staticmethod
    def is_url(s):
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?::\d+)?(?:/[-\w./?%&=]*)?$'
        return re.match(pattern, s) is not None
    @staticmethod
    def is_phone(s):
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, s) is not None
    @staticmethod
    def is_ipv4(s):
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, s):
            return False
        return all(0 <= int(x) <= 255 for x in s.split('.'))
    @staticmethod
    def is_ipv6(s):
        try:
            socket.inet_pton(socket.AF_INET6, s)
            return True
        except:
            return False
    @staticmethod
    def pretty_json(obj):
        return json.dumps(obj, ensure_ascii=False, indent=2)
    @staticmethod
    def pretty_xml(xml_str, indent=2):
        try:
            import xml.dom.minidom
            dom = xml.dom.minidom.parseString(xml_str)
            return dom.toprettyxml(indent=" " * indent)
        except:
            return xml_str
    @staticmethod
    def wrap(text, width=80):
        return textwrap.fill(text, width=width)
    @staticmethod
    def indent(text, prefix='    '):
        return '\n'.join(prefix + line for line in text.splitlines())
    @staticmethod
    def strip_html(text):
        return re.sub(r'<[^>]+>', '', text)
    @staticmethod
    def escape_html(text):
        return html.escape(text)
    @staticmethod
    def unescape_html(text):
        return html.unescape(text)
    @staticmethod
    def slugify(text):
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
        text = re.sub(r'[^\w\s-]', '', text).strip().lower()
        return re.sub(r'[-\s]+', '-', text)

# ==================== 15. 网络工具类 ====================

class Network:
    @staticmethod
    def get(url, timeout=30):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PWOS3/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode('utf-8')
        except:
            return ''
    @staticmethod
    def get_json(url, timeout=30):
        text = Network.get(url, timeout)
        return json.loads(text) if text else None
    @staticmethod
    def download(url, save_path, timeout=30):
        try:
            urllib.request.urlretrieve(url, save_path)
            return True
        except:
            return False
    @staticmethod
    def ping(host, count=1, timeout=3):
        import subprocess
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        try:
            result = subprocess.run(['ping', param, str(count), host], 
                                   capture_output=True, timeout=timeout)
            return result.returncode == 0
        except:
            return False
    @staticmethod
    def get_ip(host):
        try:
            return socket.gethostbyname(host)
        except:
            return None
    @staticmethod
    def get_local_ips():
        ips = []
        for name, addrs in socket.getaddrinfo(socket.gethostname(), None):
            ip = addrs[4][0]
            if ip.startswith('127.'):
                continue
            if ':' in ip:
                continue
            if ip not in ips:
                ips.append(ip)
        return ips
    @staticmethod
    def port_open(host, port, timeout=3):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    @staticmethod
    def get_public_ip(timeout=10):
        try:
            return Network.get('https://api.ipify.org', timeout)
        except:
            return None
    @staticmethod
    def whois(domain):
        try:
            import whois
            return whois.whois(domain)
        except ImportError:
            return None
    @staticmethod
    def scan_ports(host, ports, timeout=1):
        """扫描指定端口列表"""
        results = {}
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                results[port] = (result == 0)
                sock.close()
            except:
                results[port] = False
        return results

# ==================== 16. 数学工具类 ====================

class MathUtil:
    @staticmethod
    def sum(data):
        return sum(data)
    @staticmethod
    def avg(data):
        return sum(data) / len(data) if data else 0
    @staticmethod
    def max(data):
        return max(data) if data else None
    @staticmethod
    def min(data):
        return min(data) if data else None
    @staticmethod
    def median(data):
        if not data:
            return None
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n % 2 == 0:
            return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        return sorted_data[n//2]
    @staticmethod
    def mode(data):
        if not data:
            return None
        counter = Counter(data)
        return counter.most_common(1)[0][0]
    @staticmethod
    def variance(data):
        if len(data) < 2:
            return 0
        avg = MathUtil.avg(data)
        return sum((x - avg) ** 2 for x in data) / (len(data) - 1)
    @staticmethod
    def stdev(data):
        return MathUtil.variance(data) ** 0.5
    @staticmethod
    def factorial(n):
        return math.factorial(n)
    @staticmethod
    def gcd(a, b):
        return math.gcd(a, b)
    @staticmethod
    def lcm(a, b):
        return a * b // math.gcd(a, b)
    @staticmethod
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    @staticmethod
    def primes_upto(n):
        sieve = [True] * (n + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(n**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, n+1, i):
                    sieve[j] = False
        return [i for i, is_prime in enumerate(sieve) if is_prime]
    @staticmethod
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    @staticmethod
    def combination(n, k):
        return math.comb(n, k)
    @staticmethod
    def permutation(n, k):
        return math.perm(n, k)
    @staticmethod
    def distance_2d(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    @staticmethod
    def angle_2d(x1, y1, x2, y2):
        return math.atan2(y2 - y1, x2 - x1)

# ==================== 17. 时间日期工具类 ====================

class TimeDate:
    @staticmethod
    def now(fmt="%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.now().strftime(fmt)
    @staticmethod
    def today(fmt="%Y-%m-%d"):
        return datetime.datetime.now().strftime(fmt)
    @staticmethod
    def timestamp():
        return int(time.time())
    @staticmethod
    def timestamp_ms():
        return int(time.time() * 1000)
    @staticmethod
    def from_timestamp(ts, fmt="%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.fromtimestamp(ts).strftime(fmt)
    @staticmethod
    def parse(date_str, fmt="%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.strptime(date_str, fmt)
    @staticmethod
    def diff(start, end):
        delta = end - start
        return delta.total_seconds()
    @staticmethod
    def add_days(date_str, days, fmt="%Y-%m-%d %H:%M:%S"):
        dt = datetime.datetime.strptime(date_str, fmt)
        return (dt + datetime.timedelta(days=days)).strftime(fmt)
    @staticmethod
    def add_hours(date_str, hours, fmt="%Y-%m-%d %H:%M:%S"):
        dt = datetime.datetime.strptime(date_str, fmt)
        return (dt + datetime.timedelta(hours=hours)).strftime(fmt)
    @staticmethod
    def format_duration(seconds):
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if days > 0:
            return f"{days}d {hours}h {minutes}m {secs}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    @staticmethod
    def is_weekend(date_str, fmt="%Y-%m-%d"):
        dt = datetime.datetime.strptime(date_str, fmt)
        return dt.weekday() >= 5
    @staticmethod
    def week_number(date_str, fmt="%Y-%m-%d"):
        dt = datetime.datetime.strptime(date_str, fmt)
        return dt.isocalendar()[1]

# ==================== 18. 随机工具类 ====================

class RandomUtil:
    @staticmethod
    def int_range(min_val, max_val):
        return random.randint(min_val, max_val)
    @staticmethod
    def float_range(min_val, max_val):
        return random.uniform(min_val, max_val)
    @staticmethod
    def choice(data):
        return random.choice(data) if data else None
    @staticmethod
    def choices(data, k=1):
        return random.choices(data, k=k) if data else []
    @staticmethod
    def shuffle(data):
        result = data.copy()
        random.shuffle(result)
        return result
    @staticmethod
    def sample(data, k):
        return random.sample(data, k) if len(data) >= k else data
    @staticmethod
    def color():
        colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
        return random.choice(colors)
    @staticmethod
    def hex_color():
        return f"#{random.randint(0, 0xFFFFFF):06x}"
    @staticmethod
    def uuid():
        return str(_uuid.uuid4())
    @staticmethod
    def uuid4():
        return _uuid.uuid4()
    @staticmethod
    def name():
        first_names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    @staticmethod
    def email():
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'example.com', 'test.com']
        return f"{RandomUtil.string(8).lower()}@{random.choice(domains)}"
    @staticmethod
    def string(length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ==================== 19. 颜色工具类 ====================

class Color:
    @staticmethod
    def red(text):
        return f"\033[91m{text}\033[0m"
    @staticmethod
    def green(text):
        return f"\033[92m{text}\033[0m"
    @staticmethod
    def yellow(text):
        return f"\033[93m{text}\033[0m"
    @staticmethod
    def blue(text):
        return f"\033[94m{text}\033[0m"
    @staticmethod
    def magenta(text):
        return f"\033[95m{text}\033[0m"
    @staticmethod
    def cyan(text):
        return f"\033[96m{text}\033[0m"
    @staticmethod
    def white(text):
        return f"\033[97m{text}\033[0m"
    @staticmethod
    def black(text):
        return f"\033[90m{text}\033[0m"
    @staticmethod
    def bg_red(text):
        return f"\033[101m{text}\033[0m"
    @staticmethod
    def bg_green(text):
        return f"\033[102m{text}\033[0m"
    @staticmethod
    def bg_yellow(text):
        return f"\033[103m{text}\033[0m"
    @staticmethod
    def bg_blue(text):
        return f"\033[104m{text}\033[0m"
    @staticmethod
    def bg_cyan(text):
        return f"\033[106m{text}\033[0m"
    @staticmethod
    def bold(text):
        return f"\033[1m{text}\033[0m"
    @staticmethod
    def dim(text):
        return f"\033[2m{text}\033[0m"
    @staticmethod
    def italic(text):
        return f"\033[3m{text}\033[0m"
    @staticmethod
    def underline(text):
        return f"\033[4m{text}\033[0m"
    @staticmethod
    def blink(text):
        return f"\033[5m{text}\033[0m"
    @staticmethod
    def error(text):
        return f"\033[91;1m[ERROR] {text}\033[0m"
    @staticmethod
    def success(text):
        return f"\033[92;1m[SUCCESS] {text}\033[0m"
    @staticmethod
    def warning(text):
        return f"\033[93;1m[WARNING] {text}\033[0m"
    @staticmethod
    def info(text):
        return f"\033[96;1m[INFO] {text}\033[0m"
    @staticmethod
    def debug(text):
        return f"\033[90;1m[DEBUG] {text}\033[0m"
    @staticmethod
    def rgb(r, g, b, text):
        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"
    @staticmethod
    def bg_rgb(r, g, b, text):
        return f"\033[48;2;{r};{g};{b}m{text}\033[0m"

# ==================== 20. 系统信息类 ====================

class SystemInfo:
    @staticmethod
    def info() -> Dict[str, str]:
        return {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python': sys.version,
            'python_version': sys.version.split()[0]
        }
    @staticmethod
    def name() -> str:
        return platform.system()
    @staticmethod
    def version() -> str:
        return platform.version()
    @staticmethod
    def machine() -> str:
        return platform.machine()
    @staticmethod
    def processor() -> str:
        return platform.processor()
    @staticmethod
    def hostname() -> str:
        return platform.node()
    @staticmethod
    def is_windows() -> bool:
        return platform.system() == "Windows"
    @staticmethod
    def is_linux() -> bool:
        return platform.system() == "Linux"
    @staticmethod
    def is_macos() -> bool:
        return platform.system() == "Darwin"
    @staticmethod
    def cpu_count() -> int:
        return os.cpu_count() or 1
    @staticmethod
    def user() -> str:
        return os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    @staticmethod
    def home() -> str:
        return os.path.expanduser('~')
    @staticmethod
    def cwd() -> str:
        return os.getcwd()

# ==================== 21. 实用工具类 ====================

class Utils:
    @staticmethod
    def wait(seconds: float):
        time.sleep(seconds)
    @staticmethod
    def clear_screen():
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    @staticmethod
    def get_input(prompt: str, default: str = "") -> str:
        result = input(prompt).strip()
        return result if result else default
    @staticmethod
    def confirm(prompt: str, default: bool = False) -> bool:
        default_text = "Y/n" if default else "y/N"
        result = input(f"{prompt} ({default_text}): ").strip().lower()
        if not result:
            return default
        return result in ['y', 'yes', '是', '确认']
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 50, prefix: str = "") -> str:
        percent = current / total
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        return f"{prefix}[{bar}] {percent*100:.1f}% ({current}/{total})"
    @staticmethod
    def safe_divide(a: float, b: float, default: float = 0) -> float:
        return a / b if b != 0 else default
    @staticmethod
    def chunk_list(data: List, size: int) -> list:
        return [data[i:i+size] for i in range(0, len(data), size)]
    @staticmethod
    def flatten(lst: List) -> List:
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(Utils.flatten(item))
            else:
                result.append(item)
        return result
    @staticmethod
    def unique_preserve_order(lst: List) -> List:
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    @staticmethod
    def open_browser(url):
        webbrowser.open(url)
    @staticmethod
    def get_env(key, default=None):
        return os.environ.get(key, default)
    @staticmethod
    def set_env(key, value):
        os.environ[key] = value
    @staticmethod
    def is_interactive():
        return sys.stdin.isatty()
    @staticmethod
    def exit_code(code=0):
        sys.exit(code)

# ==================== BFS/图论扩展模块 ====================

class GraphAlgo:
    """图论算法扩展模块"""
    
    @staticmethod
    def bfs_graph(graph, start, target, o=False):
        from collections import deque
        start_time = time.time()
        
        queue = deque([(start, [start])])
        visited = {start}
        visited_count = 1
        
        while queue:
            node, path = queue.popleft()
            if node == target:
                elapsed_ms = (time.time() - start_time) * 1000
                if o:
                    return path, elapsed_ms, visited_count
                return path
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    visited_count += 1
                    queue.append((neighbor, path + [neighbor]))
        
        elapsed_ms = (time.time() - start_time) * 1000
        if o:
            return [], elapsed_ms, visited_count
        return []
    
    @staticmethod
    def bfs_grid(grid, start, target_value, o=False):
        from collections import deque
        start_time = time.time()
        
        target = None
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == target_value:
                    target = (i, j)
                    break
            if target:
                break
        
        if not target:
            if o:
                return [], 0, 0
            return []
        
        sx, sy = start
        queue = deque([(sx, sy, [(sx, sy)])])
        visited = {(sx, sy)}
        visited_count = 1
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            cx, cy, path = queue.popleft()
            if (cx, cy) == target:
                elapsed_ms = (time.time() - start_time) * 1000
                if o:
                    return path, elapsed_ms, visited_count
                return path
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                    if grid[nx][ny] != 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        visited_count += 1
                        queue.append((nx, ny, path + [(nx, ny)]))
        
        if o:
            return [], (time.time() - start_time) * 1000, visited_count
        return []
    
    @staticmethod
    def bfs_shortest_distance(graph, start, target):
        path = GraphAlgo.bfs_graph(graph, start, target)
        return len(path) - 1 if path else -1
    
    @staticmethod
    def has_path(graph, start, target):
        path = GraphAlgo.bfs_graph(graph, start, target)
        return len(path) > 0
    
    @staticmethod
    def dfs(graph, start, target, o=False):
        start_time = time.time()
        
        stack = [(start, [start])]
        visited = {start}
        visited_count = 1
        
        while stack:
            node, path = stack.pop()
            if node == target:
                elapsed_ms = (time.time() - start_time) * 1000
                if o:
                    return path, elapsed_ms, visited_count
                return path
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    visited_count += 1
                    stack.append((neighbor, path + [neighbor]))
        
        elapsed_ms = (time.time() - start_time) * 1000
        if o:
            return [], elapsed_ms, visited_count
        return []
    
    @staticmethod
    def dijkstra(graph, start, target, o=False):
        import heapq
        start_time = time.time()
        
        pq = [(0, start, [start])]
        distances = {start: 0}
        visited_count = 1
        
        while pq:
            dist, node, path = heapq.heappop(pq)
            if node == target:
                elapsed_ms = (time.time() - start_time) * 1000
                if o:
                    return path, dist, elapsed_ms, visited_count
                return path
            if dist > distances.get(node, float('inf')):
                continue
            for neighbor, weight in graph.get(node, []):
                new_dist = dist + weight
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    visited_count += 1
                    heapq.heappush(pq, (new_dist, neighbor, path + [neighbor]))
        
        elapsed_ms = (time.time() - start_time) * 1000
        if o:
            return [], -1, elapsed_ms, visited_count
        return []
    
    @staticmethod
    def has_cycle(graph):
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        return False
    
    @staticmethod
    def topological_sort(graph):
        from collections import deque
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
        
        queue = deque([node for node in graph if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result if len(result) == len(graph) else []

# ==================== 22. 新增功能模块 ====================

# 22.1 ThreadPool - 线程池轻量封装
class ThreadPool:
    def __init__(self, max_workers=None):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    def submit(self, fn, *args, **kwargs):
        return Future(self._executor.submit(fn, *args, **kwargs))
    def map(self, fn, *iterables):
        return self._executor.map(fn, *iterables)
    def shutdown(self, wait=True):
        self._executor.shutdown(wait=wait)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

# 22.2 Cache - LRU/LFU 缓存，支持 TTL
class Cache:
    def __init__(self, maxsize=128, ttl=None, policy='lru'):
        self.maxsize = maxsize
        self.ttl = ttl
        self.policy = policy
        self._cache = {}
        self._usage = {}
    def _evict(self):
        if len(self._cache) < self.maxsize:
            return
        if self.policy == 'lru':
            key = min(self._usage.keys(), key=lambda k: self._usage[k])
        else:
            key = min(self._usage.keys(), key=lambda k: self._usage[k])
        if key in self._cache:
            del self._cache[key]
            del self._usage[key]
    def set(self, key, value):
        self._evict()
        self._cache[key] = (value, time.time())
        self._usage[key] = 0 if self.policy == 'lfu' else time.time()
    def get(self, key, default=None):
        if key not in self._cache:
            return default
        value, ts = self._cache[key]
        if self.ttl and time.time() - ts > self.ttl:
            del self._cache[key]
            del self._usage[key]
            return default
        if self.policy == 'lru':
            self._usage[key] = time.time()
        else:
            self._usage[key] = self._usage.get(key, 0) + 1
        return value
    def contains(self, key):
        return key in self._cache
    def clear(self):
        self._cache.clear()
        self._usage.clear()
    def size(self):
        return len(self._cache)

# 22.3 Retry - 重试装饰器
def retry(max_attempts=3, delay=1, backoff=2, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _delay = delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(_delay)
                    _delay *= backoff
            return None
        return wrapper
    return decorator

# 22.4 RingBuffer - 循环队列
class RingBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self._buffer = [None] * capacity
        self._head = 0
        self._tail = 0
        self._size = 0
    def push_back(self, value):
        if self._size == self.capacity:
            self._head = (self._head + 1) % self.capacity
        else:
            self._size += 1
        self._buffer[self._tail] = value
        self._tail = (self._tail + 1) % self.capacity
    def pop_front(self):
        if self._size == 0:
            return None
        value = self._buffer[self._head]
        self._head = (self._head + 1) % self.capacity
        self._size -= 1
        return value
    def front(self):
        if self._size == 0:
            return None
        return self._buffer[self._head]
    def back(self):
        if self._size == 0:
            return None
        return self._buffer[(self._tail - 1) % self.capacity]
    def size(self):
        return self._size
    def empty(self):
        return self._size == 0
    def full(self):
        return self._size == self.capacity

# 22.5 Stopwatch - 高精度计时器
class Stopwatch:
    def __init__(self):
        self._start = None
        self._elapsed = 0
        self._running = False
    def start(self):
        if not self._running:
            self._start = time.perf_counter()
            self._running = True
        return self
    def stop(self):
        if self._running:
            self._elapsed += time.perf_counter() - self._start
            self._running = False
        return self
    def reset(self):
        self._elapsed = 0
        self._start = None
        self._running = False
        return self
    def elapsed(self):
        if self._running:
            return self._elapsed + (time.perf_counter() - self._start)
        return self._elapsed
    def elapsed_ms(self):
        return self.elapsed() * 1000
    def elapsed_us(self):
        return self.elapsed() * 1000000

# 22.6 Lazy - 延迟求值
class Lazy:
    def __init__(self, func):
        self._func = func
        self._value = None
        self._evaluated = False
    def get(self):
        if not self._evaluated:
            self._value = self._func()
            self._evaluated = True
        return self._value
    def is_evaluated(self):
        return self._evaluated
    def reset(self):
        self._evaluated = False
        self._value = None

# 22.7 CsvReader / CsvWriter
class CsvReader:
    def __init__(self, filepath, delimiter=','):
        self.filepath = filepath
        self.delimiter = delimiter
    def __enter__(self):
        self._file = open(self.filepath, 'r', encoding='utf-8')
        self._reader = csv.reader(self._file, delimiter=self.delimiter)
        return self
    def __exit__(self, *args):
        self._file.close()
    def __iter__(self):
        return self
    def __next__(self):
        return next(self._reader)
    def read_all(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return list(csv.reader(f, delimiter=self.delimiter))

class CsvWriter:
    def __init__(self, filepath, delimiter=','):
        self.filepath = filepath
        self.delimiter = delimiter
    def __enter__(self):
        self._file = open(self.filepath, 'w', encoding='utf-8', newline='')
        self._writer = csv.writer(self._file, delimiter=self.delimiter)
        return self
    def __exit__(self, *args):
        self._file.close()
    def writerow(self, row):
        self._writer.writerow(row)
    def writerows(self, rows):
        self._writer.writerows(rows)

# 22.8 IniConfig - 轻量级 INI 读写
class IniConfig:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self._config = configparser.ConfigParser()
        if filepath and os.path.exists(filepath):
            self._config.read(filepath, encoding='utf-8')
    def get(self, section, key, default=None):
        if self._config.has_section(section) and self._config.has_option(section, key):
            return self._config.get(section, key)
        return default
    def get_int(self, section, key, default=0):
        try:
            return int(self.get(section, key, default))
        except:
            return default
    def get_float(self, section, key, default=0.0):
        try:
            return float(self.get(section, key, default))
        except:
            return default
    def get_bool(self, section, key, default=False):
        try:
            return self._config.getboolean(section, key) if self._config.has_section(section) else default
        except:
            return default
    def set(self, section, key, value):
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, str(value))
    def save(self, filepath=None):
        path = filepath or self.filepath
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                self._config.write(f)

# 22.9 SortedSet - 有序集合
class SortedSet:
    def __init__(self, iterable=None, key=None):
        self._data = []
        self.key = key
        if iterable:
            for item in iterable:
                self.add(item)
    def add(self, value):
        pos = self._find_pos(value)
        if pos < len(self._data) and self._equal(self._data[pos], value):
            return
        self._data.insert(pos, value)
    def remove(self, value):
        pos = self._find_pos(value)
        if pos < len(self._data) and self._equal(self._data[pos], value):
            self._data.pop(pos)
    def _find_pos(self, value):
        k = self.key(value) if self.key else value
        lo, hi = 0, len(self._data)
        while lo < hi:
            mid = (lo + hi) // 2
            mk = self.key(self._data[mid]) if self.key else self._data[mid]
            if mk < k:
                lo = mid + 1
            else:
                hi = mid
        return lo
    def _equal(self, a, b):
        ka = self.key(a) if self.key else a
        kb = self.key(b) if self.key else b
        return ka == kb
    def __contains__(self, value):
        pos = self._find_pos(value)
        return pos < len(self._data) and self._equal(self._data[pos], value)
    def __len__(self):
        return len(self._data)
    def __iter__(self):
        return iter(self._data)
    def to_list(self):
        return self._data.copy()

# 22.10 Batched - 批量处理迭代器
def Batched(iterable, size):
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, size))
        if not batch:
            break
        yield batch

# 22.11 Profiler - 上下文管理器性能分析
class Profiler:
    def __init__(self, name="block"):
        self.name = name
        self._sw = Stopwatch()
    def __enter__(self):
        self._sw.start()
        return self
    def __exit__(self, *args):
        self._sw.stop()
        print(f"[Profiler] {self.name} took {self._sw.elapsed_ms():.2f} ms")
    def elapsed_ms(self):
        return self._sw.elapsed_ms()

# 22.12 Zip - 并行迭代器
def Zip(*iterables, fill=None):
    iters = [iter(it) for it in iterables]
    while True:
        result = []
        for it in iters:
            try:
                result.append(next(it))
            except StopIteration:
                result.append(fill)
        if all(v is fill and i == 0 for i, v in enumerate(result)):
            break
        yield tuple(result)

# 22.13 Tee - 复制流
def Tee(iterator, n=2):
    from itertools import tee
    return tee(iterator, n)

# 22.14 EventBus - 观察者模式事件总线
class EventBus:
    def __init__(self):
        self._listeners = defaultdict(list)
    def on(self, event, callback):
        self._listeners[event].append(callback)
    def off(self, event, callback):
        if callback in self._listeners[event]:
            self._listeners[event].remove(callback)
    def emit(self, event, **kwargs):
        for callback in self._listeners[event]:
            callback(**kwargs)
    def clear(self, event=None):
        if event:
            self._listeners[event].clear()
        else:
            self._listeners.clear()

# 22.15 Semaphore - 信号量
class Semaphore:
    def __init__(self, value=1):
        self._sem = threading.Semaphore(value)
    def acquire(self, blocking=True, timeout=None):
        return self._sem.acquire(blocking=blocking, timeout=timeout)
    def release(self):
        self._sem.release()
    def __enter__(self):
        self.acquire()
        return self
    def __exit__(self, *args):
        self.release()

# 22.16 MemoryPool - 内存池
class MemoryPool:
    def __init__(self, object_type, capacity=100):
        self.object_type = object_type
        self.capacity = capacity
        self._pool = []
        self._allocated = 0
    def alloc(self, *args, **kwargs):
        if self._pool:
            obj = self._pool.pop()
        else:
            obj = self.object_type(*args, **kwargs)
            self._allocated += 1
        return obj
    def free(self, obj):
        if len(self._pool) < self.capacity:
            self._pool.append(obj)
    def size(self):
        return len(self._pool)
    def allocated_count(self):
        return self._allocated

# 22.17 BitField - 位域读写
class BitField:
    def __init__(self, value=0, bits=32):
        self._value = value & ((1 << bits) - 1)
        self._bits = bits
    def set(self, pos, val):
        if val:
            self._value |= (1 << pos)
        else:
            self._value &= ~(1 << pos)
    def get(self, pos):
        return (self._value >> pos) & 1
    def set_range(self, start, length, val):
        mask = ((1 << length) - 1) << start
        self._value = (self._value & ~mask) | ((val << start) & mask)
    def get_range(self, start, length):
        return (self._value >> start) & ((1 << length) - 1)
    def to_int(self):
        return self._value
    def to_binary(self):
        return bin(self._value)[2:].zfill(self._bits)
    def __int__(self):
        return self._value

# ==================== 23. 全新功能模块 ====================

# 23.1 Task - 简易异步任务
class Task:
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._future = None
        self._done = False
        self._result = None
        self._error = None
    def start(self):
        if self._future is None:
            self._future = AsyncExecutor.run(self._run)
        return self
    def _run(self):
        try:
            self._result = self._func(*self._args, **self._kwargs)
            self._done = True
        except Exception as e:
            self._error = e
            self._done = True
    def get(self, timeout=None):
        if self._future is None:
            self.start()
        self._future.wait(timeout)
        if self._error:
            raise self._error
        return self._result
    def is_done(self):
        return self._done
    def wait(self, timeout=None):
        self.get(timeout)
        return self

# 23.2 Trie - 前缀树
class Trie:
    def __init__(self):
        self._root = {}
    def insert(self, word, value=None):
        node = self._root
        for ch in word:
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        node['__end__'] = value if value is not None else True
    def search(self, word):
        node = self._root
        for ch in word:
            if ch not in node:
                return None
            node = node[ch]
        return node.get('__end__')
    def starts_with(self, prefix):
        node = self._root
        for ch in prefix:
            if ch not in node:
                return []
            node = node[ch]
        return self._collect(node, prefix)
    def _collect(self, node, prefix):
        results = []
        if '__end__' in node:
            results.append(prefix)
        for ch, child in node.items():
            if ch != '__end__':
                results.extend(self._collect(child, prefix + ch))
        return results
    def remove(self, word):
        def _remove(node, word, depth):
            if depth == len(word):
                if '__end__' in node:
                    del node['__end__']
                return len(node) == 0
            ch = word[depth]
            if ch not in node:
                return False
            should_delete = _remove(node[ch], word, depth + 1)
            if should_delete:
                del node[ch]
            return len(node) == 0
        _remove(self._root, word, 0)

# 23.3 BloomFilter - 布隆过滤器
class BloomFilter:
    def __init__(self, capacity=1000, error_rate=0.001):
        self.capacity = capacity
        self.error_rate = error_rate
        self._size = self._optimal_size(capacity, error_rate)
        self._hash_count = self._optimal_hash_count(capacity, self._size)
        self._bits = BitField(0, self._size)
    def _optimal_size(self, n, p):
        import math
        return int(-n * math.log(p) / (math.log(2) ** 2))
    def _optimal_hash_count(self, n, m):
        import math
        return int((m / n) * math.log(2))
    def _hashes(self, item):
        h1 = hashlib.md5(item.encode()).hexdigest()
        h2 = hashlib.sha256(item.encode()).hexdigest()
        return [int(h1[i:i+4], 16) % self._size for i in range(0, 16, 4)] + \
               [int(h2[i:i+4], 16) % self._size for i in range(0, 16, 4)]
    def add(self, item):
        for pos in self._hashes(item)[:self._hash_count]:
            self._bits.set(pos, True)
    def contains(self, item):
        for pos in self._hashes(item)[:self._hash_count]:
            if not self._bits.get(pos):
                return False
        return True
    def clear(self):
        self._bits = BitField(0, self._size)
    def size(self):
        return self._size

# 23.4 RateLimiter - 令牌桶限流器
class RateLimiter:
    def __init__(self, max_tokens=10, refill_rate=1):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self._tokens = max_tokens
        self._last_refill = time.time()
        self._lock = threading.Lock()
    def _refill(self):
        now = time.time()
        elapsed = now - self._last_refill
        refill = elapsed * self.refill_rate
        self._tokens = min(self.max_tokens, self._tokens + refill)
        self._last_refill = now
    def acquire(self, tokens=1, timeout=None):
        start = time.time()
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
            if timeout is not None and time.time() - start > timeout:
                return False
            time.sleep(0.01)
    def try_acquire(self, tokens=1):
        return self.acquire(tokens, timeout=0)
    def reset(self):
        with self._lock:
            self._tokens = self.max_tokens
            self._last_refill = time.time()

# 23.5 Diff - 文本差异对比
class Diff:
    @staticmethod
    def compare(text1, text2):
        import difflib
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        differ = difflib.Differ()
        return list(differ.compare(lines1, lines2))
    @staticmethod
    def unified_diff(text1, text2, fromfile='a', tofile='b'):
        import difflib
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        return list(difflib.unified_diff(lines1, lines2, fromfile, tofile))
    @staticmethod
    def context_diff(text1, text2, fromfile='a', tofile='b'):
        import difflib
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        return list(difflib.context_diff(lines1, lines2, fromfile, tofile))
    @staticmethod
    def similarity(text1, text2):
        import difflib
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    @staticmethod
    def html_diff(text1, text2):
        import difflib
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        return difflib.HtmlDiff().make_file(lines1, lines2)

# 23.6 Levenshtein - 编辑距离
class Levenshtein:
    @staticmethod
    def distance(s1, s2):
        if len(s1) < len(s2):
            return Levenshtein.distance(s2, s1)
        if not s2:
            return len(s1)
        prev = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                insert = curr[j] + 1
                delete = prev[j + 1] + 1
                replace = prev[j] + (c1 != c2)
                curr.append(min(insert, delete, replace))
            prev = curr
        return prev[-1]
    @staticmethod
    def ratio(s1, s2):
        dist = Levenshtein.distance(s1, s2)
        max_len = max(len(s1), len(s2))
        return 1 - (dist / max_len) if max_len > 0 else 1
    @staticmethod
    def fuzzy_match(s1, s2, threshold=0.8):
        return Levenshtein.ratio(s1, s2) >= threshold

# 23.7 HumanReadable - 人类可读格式
class HumanReadable:
    @staticmethod
    def bytes(size):
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        idx = 0
        while size >= 1024 and idx < len(units) - 1:
            size /= 1024
            idx += 1
        return f"{size:.1f} {units[idx]}"
    @staticmethod
    def time(seconds):
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = seconds / 60
        if minutes < 60:
            return f"{minutes:.1f}m"
        hours = minutes / 60
        if hours < 24:
            return f"{hours:.1f}h"
        days = hours / 24
        return f"{days:.1f}d"
    @staticmethod
    def number(num):
        if num < 1000:
            return str(num)
        if num < 1000000:
            return f"{num/1000:.1f}K"
        if num < 1000000000:
            return f"{num/1000000:.1f}M"
        return f"{num/1000000000:.1f}B"
    @staticmethod
    def percent(value, total):
        return f"{(value/total*100):.1f}%" if total > 0 else "0%"

# 23.8 SemanticVersion - 语义化版本号
class SemanticVersion:
    def __init__(self, major=0, minor=0, patch=0, prerelease='', build=''):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build
    def __str__(self):
        ver = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            ver += f"-{self.prerelease}"
        if self.build:
            ver += f"+{self.build}"
        return ver
    def __lt__(self, other):
        return self._cmp(other) < 0
    def __eq__(self, other):
        return self._cmp(other) == 0
    def __le__(self, other):
        return self._cmp(other) <= 0
    def __gt__(self, other):
        return self._cmp(other) > 0
    def __ge__(self, other):
        return self._cmp(other) >= 0
    def _cmp(self, other):
        if self.major != other.major:
            return self.major - other.major
        if self.minor != other.minor:
            return self.minor - other.minor
        if self.patch != other.patch:
            return self.patch - other.patch
        return 0
    @staticmethod
    def parse(version_str):
        import re
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'
        match = re.match(pattern, version_str)
        if not match:
            raise ValueError(f"Invalid version: {version_str}")
        return SemanticVersion(int(match[1]), int(match[2]), int(match[3]), match[4] or '', match[5] or '')

# 23.9 ObservableList - 可观察列表
class ObservableList:
    def __init__(self, data=None):
        self._data = list(data) if data else []
        self._listeners = []
    def on_change(self, callback):
        self._listeners.append(callback)
    def _notify(self, operation, *args):
        for cb in self._listeners:
            cb(operation, *args)
    def append(self, item):
        self._data.append(item)
        self._notify('append', item)
    def insert(self, index, item):
        self._data.insert(index, item)
        self._notify('insert', index, item)
    def pop(self, index=-1):
        item = self._data.pop(index)
        self._notify('pop', index, item)
        return item
    def remove(self, item):
        self._data.remove(item)
        self._notify('remove', item)
    def clear(self):
        self._data.clear()
        self._notify('clear')
    def extend(self, items):
        self._data.extend(items)
        self._notify('extend', items)
    def __getitem__(self, index):
        return self._data[index]
    def __setitem__(self, index, value):
        self._data[index] = value
        self._notify('set', index, value)
    def __len__(self):
        return len(self._data)
    def __iter__(self):
        return iter(self._data)
    def to_list(self):
        return self._data.copy()

# 23.10 Event - 简单事件系统
class Event:
    def __init__(self):
        self._handlers = []
    def add(self, handler):
        self._handlers.append(handler)
    def remove(self, handler):
        if handler in self._handlers:
            self._handlers.remove(handler)
    def trigger(self, *args, **kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)
    def clear(self):
        self._handlers.clear()

# 23.11 Debounce - 防抖装饰器
def debounce(wait):
    def decorator(func):
        _timer = None
        def wrapper(*args, **kwargs):
            nonlocal _timer
            if _timer:
                _timer.cancel()
            _timer = threading.Timer(wait, lambda: func(*args, **kwargs))
            _timer.start()
        return wrapper
    return decorator

# 23.12 Throttle - 节流装饰器
def throttle(wait):
    def decorator(func):
        _last_call = 0
        def wrapper(*args, **kwargs):
            nonlocal _last_call
            now = time.time()
            if now - _last_call >= wait:
                _last_call = now
                return func(*args, **kwargs)
            return None
        return wrapper
    return decorator

# 23.13 Timeout - 超时上下文
@contextmanager
def Timeout(seconds):
    import signal
    def handler(signum, frame):
        raise TimeoutError(f"操作超时 ({seconds}秒)")
    old_handler = signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

# 23.14 Lock - 锁上下文
@contextmanager
def Lock(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()

# 23.15 Atomic - 原子操作装饰器
def atomic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with threading.Lock():
            return func(*args, **kwargs)
    return wrapper

# 23.16 Singleton - 单例装饰器
def singleton(cls):
    instances = {}
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

# 23.17 LazyCache - 懒加载缓存
class LazyCache:
    def __init__(self, loader):
        self._loader = loader
        self._cache = {}
        self._lock = threading.Lock()
    def get(self, key):
        with self._lock:
            if key not in self._cache:
                self._cache[key] = self._loader(key)
            return self._cache[key]
    def invalidate(self, key):
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    def clear(self):
        with self._lock:
            self._cache.clear()

# 23.18 压缩工具
def gzip_compress(data):
    return gzip.compress(data.encode() if isinstance(data, str) else data)

def gzip_decompress(data):
    return gzip.decompress(data).decode()

def zlib_compress(data):
    return zlib.compress(data.encode() if isinstance(data, str) else data)

def zlib_decompress(data):
    return zlib.decompress(data).decode()

# ==================== 24. 硬件控制模块 (新增) ====================

class Hardware:
    """硬件控制模块 - 支持 GPIO、串口、传感器等"""
    
    @staticmethod
    def get_cpu_temperature():
        """获取CPU温度 (支持 Windows/Linux/macOS)"""
        try:
            if platform.system() == "Windows":
                try:
                    import wmi
                    c = wmi.WMI()
                    for sensor in c.Win32_PerfFormattedData_Counters_ThermalZoneInformation():
                        if hasattr(sensor, 'Temperature'):
                            return sensor.Temperature / 10.0
                except ImportError:
                    pass
                # 备用方案: 使用 psutil
                try:
                    import psutil
                    return psutil.sensors_temperatures().get('coretemp', [{}])[0].current
                except:
                    return None
            elif platform.system() == "Linux":
                temp_files = [
                    '/sys/class/thermal/thermal_zone0/temp',
                    '/sys/class/hwmon/hwmon0/temp1_input',
                    '/sys/class/hwmon/hwmon1/temp1_input'
                ]
                for path in temp_files:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            temp = int(f.read().strip()) / 1000.0
                            return temp
                return None
            elif platform.system() == "Darwin":
                try:
                    import subprocess
                    result = subprocess.run(['sysctl', 'hw.sensor.acpictp.temperature'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return float(result.stdout.split()[-1])
                except:
                    pass
                return None
            return None
        except:
            return None
    
    @staticmethod
    def get_gpu_info():
        """获取GPU信息"""
        try:
            if platform.system() == "Windows":
                try:
                    import wmi
                    c = wmi.WMI()
                    for gpu in c.Win32_VideoController():
                        return {
                            'name': gpu.Name,
                            'driver': gpu.DriverVersion,
                            'memory': gpu.AdapterRAM
                        }
                except:
                    pass
            elif platform.system() == "Linux":
                try:
                    import subprocess
                    result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        parts = result.stdout.strip().split(',')
                        return {'name': parts[0].strip(), 'memory': parts[1].strip()}
                except:
                    pass
                try:
                    import subprocess
                    result = subprocess.run(['lspci', '-vnn'], capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if 'VGA' in line or '3D' in line:
                            return {'name': line.strip()}
                except:
                    pass
            return None
        except:
            return None
    
    @staticmethod
    def get_battery_status():
        """获取电池状态"""
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != -1 else None
                }
        except:
            pass
        
        # 备用方案: Windows API
        if platform.system() == "Windows":
            try:
                import ctypes
                from ctypes import wintypes
                
                class SYSTEM_POWER_STATUS(ctypes.Structure):
                    _fields_ = [
                        ('ACLineStatus', ctypes.c_byte),
                        ('BatteryFlag', ctypes.c_byte),
                        ('BatteryLifePercent', ctypes.c_byte),
                        ('Reserved1', ctypes.c_byte),
                        ('BatteryLifeTime', wintypes.DWORD),
                        ('BatteryFullLifeTime', wintypes.DWORD),
                    ]
                
                power_status = SYSTEM_POWER_STATUS()
                result = ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(power_status))
                if result:
                    return {
                        'percent': power_status.BatteryLifePercent if power_status.BatteryLifePercent <= 100 else 100,
                        'plugged': power_status.ACLineStatus == 1,
                        'time_left': power_status.BatteryLifeTime if power_status.BatteryLifeTime != 0xFFFFFFFF else None
                    }
            except:
                pass
        return None
    
    @staticmethod
    def get_disk_info():
        """获取磁盘信息"""
        result = []
        try:
            import psutil
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result.append({
                        'device': partition.device,
                        'mount': partition.mountpoint,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except:
                    pass
        except:
            pass
        return result
    
    @staticmethod
    def get_network_interfaces():
        """获取网络接口信息"""
        result = []
        try:
            import psutil
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        result.append({
                            'interface': interface,
                            'ip': addr.address,
                            'netmask': addr.netmask
                        })
        except:
            pass
        return result
    
    @staticmethod
    def get_system_load():
        """获取系统负载"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'cpu_count': psutil.cpu_count(),
                'memory_percent': psutil.virtual_memory().percent,
                'swap_percent': psutil.swap_memory().percent
            }
        except:
            return None
    
    @staticmethod
    def get_process_list(limit=20):
        """获取进程列表"""
        result = []
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    result.append(info)
                except:
                    pass
            result.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            return result[:limit]
        except:
            return []
    
    @staticmethod
    def get_screen_info():
        """获取屏幕信息"""
        try:
            if platform.system() == "Windows":
                import ctypes
                user32 = ctypes.windll.user32
                return {
                    'width': user32.GetSystemMetrics(0),
                    'height': user32.GetSystemMetrics(1),
                }
            elif platform.system() == "Linux":
                try:
                    import subprocess
                    result = subprocess.run(['xdpyinfo'], capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if 'dimensions' in line:
                            parts = line.split(':')[1].strip().split('x')
                            return {'width': int(parts[0]), 'height': int(parts[1].split()[0])}
                except:
                    pass
            elif platform.system() == "Darwin":
                try:
                    import subprocess
                    result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                          capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if 'Resolution' in line:
                            parts = line.split(':')[1].strip().split('x')
                            return {'width': int(parts[0]), 'height': int(parts[1].split()[0])}
                except:
                    pass
        except:
            pass
        return None
    
    @staticmethod
    def beep(frequency=1000, duration=200):
        """发出蜂鸣声"""
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.Beep(frequency, duration)
            else:
                # Linux/macOS 使用 \a
                print('\a', end='', flush=True)
        except:
            pass
    
    @staticmethod
    def get_mac_address():
        """获取MAC地址"""
        try:
            import uuid
            mac = uuid.getnode()
            return ':'.join(('%012x' % mac)[i:i+2] for i in range(0, 12, 2))
        except:
            return None
    
    @staticmethod
    def get_hardware_id():
        """获取硬件唯一ID"""
        try:
            import uuid
            return str(uuid.getnode())
        except:
            return None

# ==================== 25. 串口通信模块 (新增) ====================

class SerialPort:
    """串口通信模块"""
    
    def __init__(self, port=None, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None
        
    def open(self, port=None, baudrate=None, timeout=None):
        """打开串口"""
        try:
            import serial
            port = port or self.port
            baudrate = baudrate or self.baudrate
            timeout = timeout or self.timeout
            
            if not port:
                raise ValueError("请指定串口号")
            
            self._serial = serial.Serial(port, baudrate, timeout=timeout)
            return True
        except ImportError:
            return False
        except Exception as e:
            return False
    
    def close(self):
        """关闭串口"""
        if self._serial and self._serial.is_open:
            self._serial.close()
            return True
        return False
    
    def write(self, data):
        """写入数据"""
        if not self._serial or not self._serial.is_open:
            return False
        try:
            if isinstance(data, str):
                data = data.encode()
            return self._serial.write(data)
        except:
            return 0
    
    def read(self, size=1):
        """读取数据"""
        if not self._serial or not self._serial.is_open:
            return b''
        try:
            return self._serial.read(size)
        except:
            return b''
    
    def readline(self):
        """读取一行"""
        if not self._serial or not self._serial.is_open:
            return b''
        try:
            return self._serial.readline()
        except:
            return b''
    
    def read_all(self):
        """读取所有可用数据"""
        if not self._serial or not self._serial.is_open:
            return b''
        try:
            return self._serial.read_all()
        except:
            return b''
    
    def is_open(self):
        """检查串口是否打开"""
        return self._serial is not None and self._serial.is_open
    
    def get_ports(self):
        """获取可用串口列表"""
        try:
            import serial.tools.list_ports
            return [port.device for port in serial.tools.list_ports.comports()]
        except:
            return []
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args):
        self.close()

# ==================== 26. 传感器模拟模块 (新增) ====================

class SensorSimulator:
    """传感器模拟器 - 用于开发和测试"""
    
    @staticmethod
    def temperature(min_val=20, max_val=35, variation=2):
        """模拟温度传感器"""
        import random
        return random.uniform(min_val, max_val) + random.uniform(-variation, variation)
    
    @staticmethod
    def humidity(min_val=30, max_val=80, variation=5):
        """模拟湿度传感器"""
        import random
        return random.uniform(min_val, max_val) + random.uniform(-variation, variation)
    
    @staticmethod
    def pressure(min_val=980, max_val=1030, variation=5):
        """模拟气压传感器 (hPa)"""
        import random
        return random.uniform(min_val, max_val) + random.uniform(-variation, variation)
    
    @staticmethod
    def light(min_val=0, max_val=1000, variation=50):
        """模拟光照传感器 (lux)"""
        import random
        return max(0, random.uniform(min_val, max_val) + random.uniform(-variation, variation))
    
    @staticmethod
    def distance(min_val=0.1, max_val=5.0, variation=0.1):
        """模拟距离传感器 (米)"""
        import random
        return max(0, random.uniform(min_val, max_val) + random.uniform(-variation, variation))
    
    @staticmethod
    def accelerometer(g=9.8):
        """模拟加速度计 (m/s²)"""
        import random
        return {
            'x': random.uniform(-g, g),
            'y': random.uniform(-g, g),
            'z': random.uniform(-g, g)
        }
    
    @staticmethod
    def gyroscope(deg=180):
        """模拟陀螺仪 (°/s)"""
        import random
        return {
            'x': random.uniform(-deg, deg),
            'y': random.uniform(-deg, deg),
            'z': random.uniform(-deg, deg)
        }
    
    @staticmethod
    def gps(lat_min=-90, lat_max=90, lon_min=-180, lon_max=180):
        """模拟GPS坐标"""
        import random
        return {
            'latitude': random.uniform(lat_min, lat_max),
            'longitude': random.uniform(lon_min, lon_max)
        }
    
    @staticmethod
    def analog_input(min_val=0, max_val=1023):
        """模拟模拟输入 (0-1023)"""
        import random
        return random.randint(min_val, max_val)
    
    @staticmethod
    def digital_input():
        """模拟数字输入 (0或1)"""
        import random
        return random.randint(0, 1)

# ==================== 27. 音频模块 (新增) ====================

class Audio:
    """音频控制模块"""
    
    @staticmethod
    def play_sound(frequency=440, duration=0.5):
        """播放声音"""
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.Beep(frequency, int(duration * 1000))
            else:
                # 使用系统蜂鸣
                print('\a', end='', flush=True)
                time.sleep(duration)
        except:
            pass
    
    @staticmethod
    def play_wav(filepath):
        """播放WAV文件"""
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.PlaySound(filepath, winsound.SND_FILENAME)
                return True
            else:
                import subprocess
                subprocess.run(['aplay', filepath] if platform.system() == "Linux" else ['afplay', filepath],
                             capture_output=True)
                return True
        except:
            return False
    
    @staticmethod
    def get_audio_devices():
        """获取音频设备列表"""
        devices = []
        try:
            if platform.system() == "Windows":
                try:
                    import wave
                    import pyaudio
                    p = pyaudio.PyAudio()
                    for i in range(p.get_device_count()):
                        info = p.get_device_info_by_index(i)
                        devices.append({
                            'index': i,
                            'name': info['name'],
                            'channels': info['maxInputChannels'],
                            'sample_rate': int(info['defaultSampleRate'])
                        })
                    p.terminate()
                except:
                    pass
            else:
                import subprocess
                result = subprocess.run(['arecord', '-L'] if platform.system() == "Linux" else ['system_profiler', 'SPAudioDataType'],
                                      capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if ':' in line and not line.startswith(' '):
                        devices.append({'name': line.strip()})
        except:
            pass
        return devices

# ==================== 28. GPIO 模拟模块 (新增) ====================

class GPIO:
    """GPIO 控制模拟模块 (支持树莓派和模拟模式)"""
    
    MODES = {
        'BOARD': 'BOARD',
        'BCM': 'BCM'
    }
    
    DIRECTIONS = {
        'IN': 'IN',
        'OUT': 'OUT'
    }
    
    PULL = {
        'UP': 'UP',
        'DOWN': 'DOWN',
        'OFF': 'OFF'
    }
    
    def __init__(self, mode='BCM', simulation=True):
        self.mode = mode
        self.simulation = simulation
        self._pins = {}
        self._used = set()
        
    def setmode(self, mode):
        """设置引脚编号模式"""
        if mode in self.MODES.values():
            self.mode = mode
    
    def setup(self, pin, direction, pull=None):
        """设置引脚方向"""
        if pin in self._used and self._pins.get(pin, {}).get('direction') != direction:
            pass  # 允许重新配置
        self._used.add(pin)
        self._pins[pin] = {
            'direction': direction,
            'pull': pull,
            'value': 0 if direction == self.DIRECTIONS['OUT'] else None
        }
    
    def output(self, pin, value):
        """输出值"""
        if pin in self._pins and self._pins[pin]['direction'] == self.DIRECTIONS['OUT']:
            self._pins[pin]['value'] = int(bool(value))
            return True
        return False
    
    def input(self, pin):
        """读取输入值"""
        if pin in self._pins and self._pins[pin]['direction'] == self.DIRECTIONS['IN']:
            if self.simulation:
                import random
                return random.randint(0, 1)
            return self._pins[pin].get('value', 0)
        return 0
    
    def set_simulation_value(self, pin, value):
        """设置模拟值 (仅模拟模式)"""
        if self.simulation and pin in self._pins:
            self._pins[pin]['value'] = int(bool(value))
            return True
        return False
    
    def cleanup(self, pin=None):
        """清理引脚"""
        if pin is not None:
            if pin in self._pins:
                del self._pins[pin]
                self._used.discard(pin)
        else:
            self._pins.clear()
            self._used.clear()
    
    def get_pin_state(self, pin):
        """获取引脚状态"""
        return self._pins.get(pin)

# ==================== 29. StdLib 统一实例 ====================

class StdLib:
    def __init__(self):
        # 容器
        self.vector = Vector
        self.deque = Deque
        self.list = List
        self.stack = Stack
        self.queue = Queue
        self.priority_queue = PriorityQueue
        self.set = Set
        self.hash_set = HashSet
        self.map = Map
        self.hash_map = HashMap
        self.multi_set = MultiSet
        self.multi_map = MultiMap
        
        # 辅助类型
        self.pair = Pair
        self.tuple = Tuple
        self.optional = Optional
        self.variant = Variant
        self.result = Result
        self.string_view = StringView
        self.span = Span
        
        # 范围
        self.range = Range
        self.range2d = Range2D
        
        # 算法
        self.algo = Algo()
        
        # 智能指针
        self.ptr = Ptr
        self.shared_ptr = SharedPtr
        self.weak_ptr = WeakPtr
        self.unique_ptr = UniquePtr
        self.ref = Ref
        
        # 通用类型
        self.any = AnyType
        self.enum = Enum
        self.struct = Struct
        self.namespace = Namespace
        self.type_info = TypeInfo()
        
        # 系统工具
        self.memory = Memory()
        self.io = IOStream()
        self.string_stream = StringStream
        self.file_stream = FileStream
        self.chrono = Chrono
        self.duration = Duration
        self.bitset = Bitset
        self.regex = Regex
        self.random_engine = RandomEngine
        
        # 常量
        self.const = Const
        self.constexpr = constexpr
        self.template = Template()
        
        # 并发
        self.thread = Thread
        self.mutex = Mutex
        self.condition = ConditionVariable
        self.async_task = AsyncExecutor
        self.future = Future
        
        # 路径和集合
        self.path = Path
        self.array_list = ArrayList
        self.linked_list = LinkedList
        self.enumerable = Enumerable
        self.promise = Promise
        
        # 工具类
        self.file = File()
        self.string = String()
        self.network = Network()
        self.math = MathUtil()
        self.timedate = TimeDate()
        self.random = RandomUtil()
        self.color = Color()
        
        # 基础模块
        self.json = JSON()
        self.http = HTTP()
        self.crypto = Crypto()
        self.table = Table
        self.progress = ProgressBar
        self.config = Config
        self.logger = Logger
        
        # 实用模块
        self.system = SystemInfo()
        self.utils = Utils()
        self.sys = SystemInfo()
        
        # 图论算法模块
        self.graph = GraphAlgo()
        
        # 新增功能
        self.thread_pool = ThreadPool
        self.cache = Cache
        self.retry = retry
        self.ring_buffer = RingBuffer
        self.stopwatch = Stopwatch
        self.lazy = Lazy
        self.csv_reader = CsvReader
        self.csv_writer = CsvWriter
        self.ini_config = IniConfig
        self.sorted_set = SortedSet
        self.batched = Batched
        self.profiler = Profiler
        self.zip = Zip
        self.tee = Tee
        self.event_bus = EventBus
        self.semaphore = Semaphore
        self.memory_pool = MemoryPool
        self.bitfield = BitField
        
        # 全新功能
        self.task = Task
        self.trie = Trie
        self.bloom_filter = BloomFilter
        self.rate_limiter = RateLimiter
        self.diff = Diff
        self.levenshtein = Levenshtein
        self.human = HumanReadable
        self.semver = SemanticVersion
        self.observable_list = ObservableList
        self.event = Event
        self.debounce = debounce
        self.throttle = throttle
        self.timeout = Timeout
        self.lock = Lock
        self.atomic = atomic
        self.singleton = singleton
        self.lazy_cache = LazyCache
        self.gzip_compress = gzip_compress
        self.gzip_decompress = gzip_decompress
        self.zlib_compress = zlib_compress
        self.zlib_decompress = zlib_decompress
        
        # ========== 硬件控制模块 (新增) ==========
        self.hardware = Hardware()
        self.serial = SerialPort
        self.sensor = SensorSimulator()
        self.audio = Audio()
        self.gpio = GPIO

# 创建全局实例
std = StdLib()
