# ==================== std_lib.py - PWOS3 超级增强标准库 ====================
# 版本: 2.0 - 超级增强版

import os, sys, json, time, random, hashlib, datetime, shutil, zipfile, tarfile
import re, base64, csv, sqlite3, subprocess, socket, platform, math, textwrap
import io, glob, fnmatch, tempfile, configparser, logging, string, secrets
import getpass, threading, queue, struct, itertools, collections, enum
import heapq, bisect, functools, operator, inspect, copy, weakref, contextlib
import concurrent.futures, asyncio, typing, urllib.request, urllib.parse
from typing import Any, Dict, List, Tuple, Optional, Union, Callable, TypeVar, Generic
from collections import OrderedDict, defaultdict, Counter, deque, namedtuple
from functools import wraps, partial, reduce, lru_cache
from contextlib import contextmanager
import traceback

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
    def __repr__(self):
        if self.is_ok():
            return f"Ok({self._value})"
        return f"Err({self._error})"

class Enum:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def items(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}.items()

class Namespace:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Struct:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}
    def __repr__(self):
        items = ', '.join(f"{k}={v}" for k, v in self.__dict__.items())
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

class StringView:
    def __init__(self, s: str):
        self._s = s
    def substr(self, pos, length=None):
        if length is None:
            return StringView(self._s[pos:])
        return StringView(self._s[pos:pos+length])
    def find(self, sub, start=0):
        return self._s.find(sub, start)
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

# ==================== 3. 算法库增强 ====================

class Algo:
    @staticmethod
    def sort(data, reverse=False):
        return sorted(data, reverse=reverse)
    
    @staticmethod
    def stable_sort(data, key=None):
        return sorted(data, key=key)
    
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

# ==================== 4. 新增：Range 类 ====================

class Range:
    """范围迭代器，支持多种用法"""
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
    def __iter__(self):
        return iter(range(self._start, self._end, self._step))
    def __repr__(self):
        return f"Range({self._start}, {self._end}, {self._step})"

class Range2D:
    """二维范围"""
    def __init__(self, x_start, x_end, y_start, y_end, x_step=1, y_step=1):
        self.x_range = Range(x_start, x_end, x_step)
        self.y_range = Range(y_start, y_end, y_step)
    def to_list(self):
        return [(x, y) for x in self.x_range for y in self.y_range]
    def __iter__(self):
        for x in self.x_range:
            for y in self.y_range:
                yield x, y

# ==================== 5. 新增：JSON 增强类 ====================

class JSON:
    @staticmethod
    def parse(text):
        return json.loads(text)
    @staticmethod
    def stringify(obj, indent=2):
        return json.dumps(obj, ensure_ascii=False, indent=indent)
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

# ==================== 6. 新增：HTTP 客户端增强 ====================

class HTTP:
    @staticmethod
    def get(url, headers=None, timeout=30):
        req = urllib.request.Request(url, headers=headers or {'User-Agent': 'PWOS3/2.0'})
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
    def download(url, save_path, timeout=30):
        urllib.request.urlretrieve(url, save_path)
        return True

# ==================== 7. 新增：加密工具增强 ====================

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
    def base64_encode(text):
        return base64.b64encode(text.encode()).decode()
    @staticmethod
    def base64_decode(text):
        return base64.b64decode(text.encode()).decode()
    @staticmethod
    def random_token(length=32):
        return secrets.token_hex(length)
    @staticmethod
    def random_string(length=8):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

# ==================== 8. 新增：表格美化类 ====================

class Table:
    """简单的表格美化器"""
    def __init__(self, headers=None):
        self.headers = headers or []
        self.rows = []
    def add_row(self, row):
        self.rows.append(row)
    def add_rows(self, rows):
        self.rows.extend(rows)
    def clear(self):
        self.rows.clear()
    def print(self):
        if not self.headers and not self.rows:
            return
        # 计算列宽
        col_widths = []
        if self.headers:
            col_widths = [len(str(h)) for h in self.headers]
        for row in self.rows:
            for i, cell in enumerate(row):
                if i >= len(col_widths):
                    col_widths.append(0)
                col_widths[i] = max(col_widths[i], len(str(cell)))
        # 构建分隔线
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
        # 打印表头
        if self.headers:
            print(separator)
            header_line = "| " + " | ".join(str(h).ljust(w) for h, w in zip(self.headers, col_widths)) + " |"
            print(header_line)
        print(separator)
        # 打印数据行
        for row in self.rows:
            line = "| " + " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)) + " |"
            print(line)
        print(separator)
    def to_string(self):
        output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output
        self.print()
        sys.stdout = old_stdout
        return output.getvalue()

# ==================== 9. 新增：进度条类 ====================

class ProgressBar:
    """终端进度条"""
    def __init__(self, total, width=50, prefix="Progress", suffix="Complete", color=True):
        self.total = total
        self.width = width
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        self.color = color
    def update(self, n=1):
        self.current += n
        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = "█" * filled + "░" * (self.width - filled)
        if self.color:
            if percent < 0.5:
                bar = f"\033[93m{bar}\033[0m"  # 黄色
            elif percent < 0.8:
                bar = f"\033[96m{bar}\033[0m"  # 青色
            else:
                bar = f"\033[92m{bar}\033[0m"  # 绿色
        print(f"\r{self.prefix}: |{bar}| {self.current}/{self.total} {self.suffix}", end="", flush=True)
        if self.current >= self.total:
            print()
    def reset(self):
        self.current = 0

# ==================== 10. 新增：配置管理类 ====================

class Config:
    """简单的配置管理器"""
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
                else:
                    self._config = json.loads(f.read())
        return self
    def save(self, filepath=None):
        path = filepath or self.filepath
        if path:
            with open(path, 'w', encoding='utf-8') as f:
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

# ==================== 11. 新增：日志工具 ====================

class Logger:
    """简单日志工具"""
    LEVELS = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}
    def __init__(self, name="app", level="INFO", color=True):
        self.name = name
        self.level = self.LEVELS.get(level.upper(), 1)
        self.color = color
    def _log(self, level, msg, color_func=None):
        if self.LEVELS[level] >= self.level:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"[{timestamp}] [{level}] [{self.name}] {msg}"
            if self.color and color_func:
                log_msg = color_func(log_msg)
            print(log_msg)
    def debug(self, msg):
        self._log("DEBUG", msg, lambda x: f"\033[90m{x}\033[0m")  # 灰色
    def info(self, msg):
        self._log("INFO", msg, lambda x: f"\033[92m{x}\033[0m")   # 绿色
    def warn(self, msg):
        self._log("WARN", msg, lambda x: f"\033[93m{x}\033[0m")   # 黄色
    def error(self, msg):
        self._log("ERROR", msg, lambda x: f"\033[91m{x}\033[0m")  # 红色

# ==================== 12. 系统工具类 ====================

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
    def str(self):
        return self._buffer.getvalue()

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
    def replace(self, text, repl):
        return self._compiled.sub(repl, text)
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
    def shuffle(self, seq):
        self._rng.shuffle(seq)
    def sample(self, seq, k):
        return self._rng.sample(seq, k)

class Thread:
    def __init__(self, target, args=(), kwargs={}):
        self._thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    def start(self):
        self._thread.start()
    def join(self):
        self._thread.join()
    def is_alive(self):
        return self._thread.is_alive()

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

class Future:
    def __init__(self, cf):
        self._cf = cf
    def get(self, timeout=None):
        return self._cf.result(timeout)
    def wait(self, timeout=None):
        concurrent.futures.wait([self._cf], timeout)
    def done(self):
        return self._cf.done()
    @staticmethod
    def all(futures):
        concurrent.futures.wait([f._cf for f in futures])

class Path:
    def __init__(self, path):
        self._path = os.path.normpath(path)
    def exists(self):
        return os.path.exists(self._path)
    def is_file(self):
        return os.path.isfile(self._path)
    def is_dir(self):
        return os.path.isdir(self._path)
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
        return glob.glob(os.path.join(self._path, pattern))
    def mkdir(self, exist_ok=True):
        os.makedirs(self._path, exist_ok=exist_ok)
    def remove(self):
        if self.is_file(): os.remove(self._path)
        elif self.is_dir(): shutil.rmtree(self._path)
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
    def order_by(self, key):
        return Enumerable(sorted(self._seq, key=key))
    def order_by_desc(self, key):
        return Enumerable(sorted(self._seq, key=key, reverse=True))
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
        results = [None] * len(promises)
        completed = 0
        def handler(i, res):
            nonlocal completed
            results[i] = res
            completed += 1
            if completed == len(promises):
                future.set_result(results)
        future = concurrent.futures.Future()
        for i, p in enumerate(promises):
            p.then(lambda r, i=i: handler(i, r), future.set_exception)
        return Promise(lambda res, rej: None)  # Simplified

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

# ==================== 13. 文件工具类（增强） ====================

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
            if os.path.isdir(src_full): shutil.copytree(src_full, dst_full)
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

# ==================== 14. 字符串工具类（增强） ====================

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
    def is_email(s):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, s) is not None
    @staticmethod
    def is_url(s):
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return re.match(pattern, s) is not None
    @staticmethod
    def is_phone(s):
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, s) is not None

# ==================== 15. 网络工具类（增强） ====================

class Network:
    @staticmethod
    def get(url, timeout=30):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PWOS3/2.0'})
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

# ==================== 16. 数学工具类（增强） ====================

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

# ==================== 17. 时间日期工具类（增强） ====================

class TimeDate:
    @staticmethod
    def now(fmt="%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.now().strftime(fmt)
    @staticmethod
    def timestamp():
        return int(time.time())
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

# ==================== 18. 随机工具类（增强） ====================

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

# ==================== 19. 颜色工具类（增强） ====================

class Color:
    # 基本颜色
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
    
    # 背景色
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
    
    # 样式
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
    
    # 组合样式
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

# ==================== StdLib 统一实例（超级增强版） ====================

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
        
        # 新增
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
        
        # 新增强大工具
        self.file = File()
        self.string = String()
        self.network = Network()
        self.math = MathUtil()
        self.timedate = TimeDate()
        self.random = RandomUtil()
        self.color = Color()
        
        # 新增模块
        self.json = JSON()
        self.http = HTTP()
        self.crypto = Crypto()
        self.table = Table
        self.progress = ProgressBar
        self.config = Config
        self.logger = Logger

# 创建全局实例
std = StdLib()