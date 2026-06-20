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

# ==================== std_lib.py - PWOS3 超级增强标准库 ====================
# 版本: 4.1 - 完整硬件控制版
# 包含: 基础类型、容器、算法、网络、加密、表格、进度条、配置、日志
#       + 完整 IO 硬件控制 (GPIO/I2C/SPI/UART/USB/PCIe/CSI/DSI/传感器/电机/AI)
#       + BFS/图论扩展
#       + ThreadPool, Cache, Retry, RingBuffer, Stopwatch, LRU, EventBus
#       + ObjectPool, Lazy, CsvReader, IniConfig, SortedSet, Batched
#       + Profiler, Zip, Tee, Observer, Semaphore, MemoryPool, BitField

import os, sys, json, time, random, hashlib, datetime, shutil, zipfile, tarfile
import re, base64, csv, sqlite3, subprocess, socket, platform, math, textwrap
import io, glob, fnmatch, tempfile, configparser, logging, string, secrets
import getpass, threading, queue, struct, itertools, collections, enum
import heapq, bisect, functools, operator, inspect, copy, weakref, contextlib
import concurrent.futures, asyncio, typing, urllib.request, urllib.parse
from typing import Any, Dict, List, Tuple, Optional, Union, Callable, TypeVar, Generic, Iterator
from collections import OrderedDict, defaultdict, Counter, deque, namedtuple
from functools import wraps, partial, reduce, lru_cache
from contextlib import contextmanager
import traceback
import uuid as _uuid

# ==================== 硬件控制导入 ====================
try:
    import RPi.GPIO as _RPi_GPIO
    _HAS_RPI_GPIO = True
except ImportError:
    _HAS_RPI_GPIO = False

try:
    import smbus2 as _smbus
    _HAS_SMBUS = True
except ImportError:
    try:
        import smbus as _smbus
        _HAS_SMBUS = True
    except ImportError:
        _HAS_SMBUS = False

try:
    import spidev as _spidev
    _HAS_SPIDEV = True
except ImportError:
    _HAS_SPIDEV = False

try:
    import serial as _serial
    _HAS_SERIAL = True
except ImportError:
    _HAS_SERIAL = False

try:
    import usb.core as _usb_core
    import usb.util as _usb_util
    _HAS_PYUSB = True
except ImportError:
    _HAS_PYUSB = False

try:
    import picamera as _picamera
    _HAS_PICAMERA = True
except ImportError:
    _HAS_PICAMERA = False

try:
    import cv2 as _cv2
    _HAS_OPENCV = True
except ImportError:
    _HAS_OPENCV = False

try:
    import torch as _torch
    _HAS_TORCH = True
except ImportError:
    _HAS_TORCH = False

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
    def items(self):
        return list(self._dict.items())
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

# ==================== 4. Range ====================

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

# ==================== 5. JSON ====================

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

# ==================== 6. HTTP ====================

class HTTP:
    @staticmethod
    def get(url, headers=None, timeout=30):
        req = urllib.request.Request(url, headers=headers or {'User-Agent': 'PWOS3/4.1'})
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

# ==================== 7. 加密 ====================

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

# ==================== 8. 表格 ====================

class Table:
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
            header_line = "| " + " | ".join(str(h).ljust(w) for h, w in zip(self.headers, col_widths)) + " |"
            print(header_line)
        print(separator)
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

# ==================== 9. 进度条 ====================

class ProgressBar:
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
                bar = f"\033[93m{bar}\033[0m"
            elif percent < 0.8:
                bar = f"\033[96m{bar}\033[0m"
            else:
                bar = f"\033[92m{bar}\033[0m"
        print(f"\r{self.prefix}: |{bar}| {self.current}/{self.total} {self.suffix}", end="", flush=True)
        if self.current >= self.total:
            print()
    def reset(self):
        self.current = 0

# ==================== 10. 配置 ====================

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

# ==================== 11. 日志 ====================

class Logger:
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
        self._log("DEBUG", msg, lambda x: f"\033[90m{x}\033[0m")
    def info(self, msg):
        self._log("INFO", msg, lambda x: f"\033[92m{x}\033[0m")
    def warn(self, msg):
        self._log("WARN", msg, lambda x: f"\033[93m{x}\033[0m")
    def error(self, msg):
        self._log("ERROR", msg, lambda x: f"\033[91m{x}\033[0m")

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
        return Promise(lambda res, rej: None)

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

# ==================== 13. 文件 ====================

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

# ==================== 14. 字符串 ====================

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

# ==================== 15. 网络 ====================

class Network:
    @staticmethod
    def get(url, timeout=30):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PWOS3/4.1'})
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

# ==================== 16. 数学 ====================

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

# ==================== 17. 时间日期 ====================

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

# ==================== 18. 随机 ====================

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
    def uuid():
        return str(_uuid.uuid4())

# ==================== 19. 颜色 ====================

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

# ==================== 20. 系统信息 ====================

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

# ==================== 21. 实用工具 ====================

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

# ==================== BFS/图论 ====================

class GraphAlgo:
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

# ==================== 22. 新增功能 ====================

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

def Batched(iterable, size):
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, size))
        if not batch:
            break
        yield batch

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

def Tee(iterator, n=2):
    from itertools import tee
    return tee(iterator, n)

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

# ==================== 23. IO 硬件控制 (完整版) ====================

class IOPortType:
    """端口类型枚举 - 覆盖所有已知接口"""
    # GPIO
    GPIO = "gpio"
    GPIO_BCM = "gpio_bcm"
    GPIO_WIRING = "gpio_wiring"
    GPIO_SYSFS = "gpio_sysfs"
    
    # I2C
    I2C = "i2c"
    I2C_SMBUS = "i2c_smbus"
    I2C_DEV = "i2c_dev"
    
    # SPI
    SPI = "spi"
    SPI_DEV = "spi_dev"
    
    # UART
    UART = "uart"
    UART_TTY = "uart_tty"
    UART_USB = "uart_usb"
    
    # USB
    USB = "usb"
    USB_HOST = "usb_host"
    USB_OTG = "usb_otg"
    USB_DEVICE = "usb_device"
    
    # PCIe
    PCIE = "pcie"
    PCIE_X1 = "pcie_x1"
    PCIE_X4 = "pcie_x4"
    PCIE_X8 = "pcie_x8"
    PCIE_X16 = "pcie_x16"
    PCIE_MINI = "pcie_mini"
    PCIE_M2 = "pcie_m2"
    
    # 摄像头
    CSI = "csi"
    CSI_0 = "csi0"
    CSI_1 = "csi1"
    CSI_2 = "csi2"
    USB_CAM = "usb_cam"
    IP_CAM = "ip_cam"
    HDMI_CAM = "hdmi_cam"
    
    # 显示
    DSI = "dsi"
    HDMI = "hdmi"
    DP = "dp"
    VGA = "vga"
    LVDS = "lvds"
    EDP = "edp"
    
    # 音频
    AUDIO = "audio"
    AUDIO_HDMI = "audio_hdmi"
    AUDIO_USB = "audio_usb"
    AUDIO_I2S = "audio_i2s"
    AUDIO_PCM = "audio_pcm"
    
    # 存储
    STORAGE = "storage"
    SATA = "sata"
    NVME = "nvme"
    EMMC = "emmc"
    SDIO = "sdio"
    SDMMC = "sdmmc"
    
    # AI 加速
    AI = "ai"
    AI_PCIE = "ai_pcie"
    AI_USB = "ai_usb"
    AI_M2 = "ai_m2"
    AI_NPU = "ai_npu"
    AI_TPU = "ai_tpu"
    AI_CORAL = "ai_coral"
    
    # 网络
    ETH = "eth"
    WIFI = "wifi"
    BT = "bt"
    LTE = "lte"
    CAN = "can"
    RS485 = "rs485"
    RS232 = "rs232"
    
    # 传感器
    SENSOR = "sensor"
    SENSOR_I2C = "sensor_i2c"
    SENSOR_SPI = "sensor_spi"
    SENSOR_GPIO = "sensor_gpio"
    SENSOR_ANALOG = "sensor_analog"
    
    # 电机
    MOTOR = "motor"
    SERVO = "servo"
    STEPPER = "stepper"
    DC_MOTOR = "dc_motor"
    BRUSHLESS = "brushless"
    
    # 开发板专用
    JETSON_GPIO = "jetson_gpio"
    JETSON_CAM = "jetson_cam"
    ORANGE_PI_GPIO = "orange_gpio"
    ROCKCHIP_GPIO = "rockchip_gpio"
    ALLWINNER_GPIO = "allwinner_gpio"
    BANANA_PI_GPIO = "banana_pi_gpio"
    
    # ESP32/Arduino
    ESP32_UART = "esp32_uart"
    ESP32_SPI = "esp32_spi"
    ESP32_I2C = "esp32_i2c"
    ARDUINO_UART = "arduino_uart"
    ARDUINO_I2C = "arduino_i2c"
    ARDUINO_SPI = "arduino_spi"
    
    # 虚拟
    VIRTUAL = "virtual"
    SIMULATOR = "simulator"
    DEBUG = "debug"
    UNKNOWN = "unknown"

class _PortAlias:
    """端口别名映射"""
    ALIASES = {
        # GPIO
        "gpio": IOPortType.GPIO, "gpio0": IOPortType.GPIO, "gpio1": IOPortType.GPIO,
        "gpio_bcm": IOPortType.GPIO_BCM, "bcm": IOPortType.GPIO_BCM,
        "gpio_wiring": IOPortType.GPIO_WIRING, "wiring": IOPortType.GPIO_WIRING,
        "gpio_sysfs": IOPortType.GPIO_SYSFS, "sysfs": IOPortType.GPIO_SYSFS,
        # I2C
        "i2c": IOPortType.I2C, "i2c0": IOPortType.I2C, "i2c1": IOPortType.I2C,
        "i2c_smbus": IOPortType.I2C_SMBUS, "smbus": IOPortType.I2C_SMBUS,
        "i2c_dev": IOPortType.I2C_DEV,
        # SPI
        "spi": IOPortType.SPI, "spi0": IOPortType.SPI, "spi1": IOPortType.SPI,
        "spi_dev": IOPortType.SPI_DEV,
        # UART
        "uart": IOPortType.UART, "uart0": IOPortType.UART, "uart1": IOPortType.UART,
        "tty": IOPortType.UART_TTY, "ttyAMA": IOPortType.UART_TTY,
        "ttyS": IOPortType.UART_TTY, "ttyUSB": IOPortType.UART_USB,
        # USB
        "usb": IOPortType.USB, "usb0": IOPortType.USB, "usb1": IOPortType.USB,
        "usb2": IOPortType.USB, "usb3": IOPortType.USB,
        "usb_host": IOPortType.USB_HOST, "usb_otg": IOPortType.USB_OTG,
        "usb_device": IOPortType.USB_DEVICE,
        # PCIe
        "pcie": IOPortType.PCIE, "pcie0": IOPortType.PCIE, "pcie1": IOPortType.PCIE,
        "pcie_x1": IOPortType.PCIE_X1, "pcie_x4": IOPortType.PCIE_X4,
        "pcie_x8": IOPortType.PCIE_X8, "pcie_x16": IOPortType.PCIE_X16,
        "pcie_mini": IOPortType.PCIE_MINI, "mini_pcie": IOPortType.PCIE_MINI,
        "pcie_m2": IOPortType.PCIE_M2, "m2": IOPortType.PCIE_M2, "m.2": IOPortType.PCIE_M2,
        # 摄像头
        "csi": IOPortType.CSI, "csi0": IOPortType.CSI_0, "csi1": IOPortType.CSI_1,
        "csi2": IOPortType.CSI_2, "camera": IOPortType.CSI, "cam": IOPortType.CSI,
        "cam0": IOPortType.CSI_0, "cam1": IOPortType.CSI_1,
        "usb_cam": IOPortType.USB_CAM, "usbcam": IOPortType.USB_CAM,
        "ip_cam": IOPortType.IP_CAM, "ipcam": IOPortType.IP_CAM,
        "hdmi_cam": IOPortType.HDMI_CAM, "hdmicam": IOPortType.HDMI_CAM,
        # 显示
        "dsi": IOPortType.DSI, "dsi0": IOPortType.DSI, "display": IOPortType.DSI,
        "hdmi": IOPortType.HDMI, "hdmi0": IOPortType.HDMI, "hdmi1": IOPortType.HDMI,
        "dp": IOPortType.DP, "dp0": IOPortType.DP,
        "vga": IOPortType.VGA, "lvds": IOPortType.LVDS, "edp": IOPortType.EDP,
        # 音频
        "audio": IOPortType.AUDIO, "audio0": IOPortType.AUDIO,
        "hdmi_audio": IOPortType.AUDIO_HDMI, "usb_audio": IOPortType.AUDIO_USB,
        "i2s": IOPortType.AUDIO_I2S, "pcm": IOPortType.AUDIO_PCM,
        # 存储
        "storage": IOPortType.STORAGE, "sata": IOPortType.SATA,
        "nvme": IOPortType.NVME, "emmc": IOPortType.EMMC,
        "sdio": IOPortType.SDIO, "sdmmc": IOPortType.SDMMC,
        # AI
        "ai": IOPortType.AI, "ai0": IOPortType.AI,
        "ai_pcie": IOPortType.AI_PCIE, "ai_usb": IOPortType.AI_USB,
        "ai_m2": IOPortType.AI_M2, "npu": IOPortType.AI_NPU,
        "tpu": IOPortType.AI_TPU, "coral": IOPortType.AI_CORAL,
        "edge_tpu": IOPortType.AI_CORAL,
        # 网络
        "eth": IOPortType.ETH, "eth0": IOPortType.ETH, "ethernet": IOPortType.ETH,
        "wifi": IOPortType.WIFI, "wlan": IOPortType.WIFI, "wlan0": IOPortType.WIFI,
        "bt": IOPortType.BT, "bluetooth": IOPortType.BT,
        "lte": IOPortType.LTE, "4g": IOPortType.LTE, "5g": IOPortType.LTE,
        "can": IOPortType.CAN, "can0": IOPortType.CAN,
        "rs485": IOPortType.RS485, "rs232": IOPortType.RS232,
        # 传感器
        "sensor": IOPortType.SENSOR,
        "sensor_i2c": IOPortType.SENSOR_I2C,
        "sensor_spi": IOPortType.SENSOR_SPI,
        "sensor_gpio": IOPortType.SENSOR_GPIO,
        "analog": IOPortType.SENSOR_ANALOG,
        # 电机
        "motor": IOPortType.MOTOR, "servo": IOPortType.SERVO,
        "stepper": IOPortType.STEPPER, "dc_motor": IOPortType.DC_MOTOR,
        "brushless": IOPortType.BRUSHLESS,
        # 开发板
        "jetson_gpio": IOPortType.JETSON_GPIO, "jetson": IOPortType.JETSON_GPIO,
        "jetson_cam": IOPortType.JETSON_CAM,
        "orange_gpio": IOPortType.ORANGE_PI_GPIO, "orange_pi": IOPortType.ORANGE_PI_GPIO,
        "orange": IOPortType.ORANGE_PI_GPIO,
        "rockchip_gpio": IOPortType.ROCKCHIP_GPIO, "rockchip": IOPortType.ROCKCHIP_GPIO,
        "rk": IOPortType.ROCKCHIP_GPIO,
        "allwinner_gpio": IOPortType.ALLWINNER_GPIO, "allwinner": IOPortType.ALLWINNER_GPIO,
        "aw": IOPortType.ALLWINNER_GPIO,
        "banana_pi": IOPortType.BANANA_PI_GPIO, "banana": IOPortType.BANANA_PI_GPIO,
        # ESP32/Arduino
        "esp32": IOPortType.ESP32_UART, "esp32_uart": IOPortType.ESP32_UART,
        "esp32_spi": IOPortType.ESP32_SPI, "esp32_i2c": IOPortType.ESP32_I2C,
        "arduino": IOPortType.ARDUINO_UART, "arduino_uart": IOPortType.ARDUINO_UART,
        "arduino_i2c": IOPortType.ARDUINO_I2C, "arduino_spi": IOPortType.ARDUINO_SPI,
        # 虚拟
        "virtual": IOPortType.VIRTUAL, "sim": IOPortType.SIMULATOR,
        "debug": IOPortType.DEBUG,
    }

class _DeviceInfo:
    """设备信息"""
    def __init__(self, id, name, port_type, port_spec, driver, available=False, 
                 forced=False, aliases=None, metadata=None, error=None):
        self.id = id
        self.name = name
        self.port_type = port_type
        self.port_spec = port_spec
        self.driver = driver
        self.available = available
        self.forced = forced
        self.aliases = aliases or []
        self.metadata = metadata or {}
        self.error = error

class _PortBinder:
    """端口绑定器 - 支持 su 强制绑定"""
    @staticmethod
    def parse(port_spec):
        port_spec = port_spec.lower().strip()
        is_forced = port_spec.startswith('su')
        if is_forced:
            port_spec = port_spec[2:]
        port_type = _PortAlias.ALIASES.get(port_spec)
        if port_type is None:
            for alias, ptype in _PortAlias.ALIASES.items():
                if port_spec.startswith(alias):
                    rest = port_spec[len(alias):]
                    if rest == '' or rest.isdigit():
                        port_type = ptype
                        break
        return is_forced, port_spec, port_type
    
    @staticmethod
    def bind(port_spec, device_list):
        is_forced, port, port_type = _PortBinder.parse(port_spec)
        matched = None
        for dev in device_list:
            if dev.port_spec == port or port in dev.aliases:
                matched = dev
                break
        if matched:
            if not is_forced:
                if matched.port_type == port_type or port_type is None:
                    return matched
                matched.error = f"类型不匹配: 设备是 {matched.port_type.value}, 请求 {port_type.value if port_type else '未知'}"
                return None
            matched.forced = True
            return matched
        if is_forced:
            return _DeviceInfo(
                id=f"virtual_{port}",
                name=f"虚拟设备 ({port})",
                port_type=port_type or IOPortType.VIRTUAL,
                port_spec=port,
                driver="virtual",
                available=True,
                forced=True,
                aliases=[port],
                metadata={"is_virtual": True}
            )
        return None

class _SystemDetector:
    """系统检测器"""
    @staticmethod
    def detect():
        info = {
            "os": platform.system().lower(),
            "arch": platform.machine(),
            "processor": platform.processor(),
            "board": "pc",
            "board_model": "Unknown",
            "features": {}
        }
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                if 'Raspberry Pi' in model:
                    info["board"] = "raspberry_pi"
                elif 'Orange Pi' in model:
                    info["board"] = "orange_pi"
                elif 'NVIDIA Jetson' in model:
                    info["board"] = "jetson"
                elif 'Rockchip' in model:
                    info["board"] = "rockchip"
                elif 'Allwinner' in model:
                    info["board"] = "allwinner"
                elif 'Banana Pi' in model:
                    info["board"] = "banana_pi"
                info["board_model"] = model.strip()
        except:
            pass
        
        info["features"]["gpio"] = _HAS_RPI_GPIO
        info["features"]["i2c"] = _HAS_SMBUS
        info["features"]["spi"] = _HAS_SPIDEV
        info["features"]["uart"] = _HAS_SERIAL
        info["features"]["usb"] = _HAS_PYUSB
        info["features"]["camera"] = _HAS_PICAMERA
        info["features"]["opencv"] = _HAS_OPENCV
        info["features"]["ai"] = _HAS_TORCH
        return info

class _DeviceScanner:
    @staticmethod
    def scan(system_info):
        devices = []
        board = system_info.get("board", "pc")
        features = system_info.get("features", {})
        
        # GPIO
        if features.get("gpio", False):
            devices.append(_DeviceInfo(
                "gpio", "GPIO 控制器", IOPortType.GPIO,
                "gpio", "RPi.GPIO", True, aliases=["gpio0", "bcm"]
            ))
        
        # I2C
        if features.get("i2c", False):
            devices.append(_DeviceInfo(
                "i2c", "I2C 总线", IOPortType.I2C,
                "i2c", "smbus2", True, aliases=["i2c0", "i2c1", "smbus"]
            ))
        
        # SPI
        if features.get("spi", False):
            devices.append(_DeviceInfo(
                "spi", "SPI 总线", IOPortType.SPI,
                "spi", "spidev", True, aliases=["spi0", "spi1"]
            ))
        
        # UART
        if features.get("uart", False):
            devices.append(_DeviceInfo(
                "uart", "UART 串口", IOPortType.UART,
                "uart", "serial", True, aliases=["ttyS0", "ttyAMA0"]
            ))
        
        # 摄像头
        if features.get("camera", False):
            devices.append(_DeviceInfo(
                "csi_camera", "CSI 摄像头", IOPortType.CSI,
                "csi", "picamera", True, aliases=["csi0", "cam", "camera"]
            ))
        
        # USB 设备扫描
        if features.get("usb", False):
            try:
                import usb.core
                import usb.util
                for dev in usb.core.find(find_all=True):
                    try:
                        product = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else "USB 设备"
                        devices.append(_DeviceInfo(
                            f"usb_{dev.idVendor:04x}_{dev.idProduct:04x}",
                            product, IOPortType.USB,
                            f"usb{dev.address}", "pyusb", True,
                            aliases=[f"usb{dev.address}"],
                            metadata={"vid": dev.idVendor, "pid": dev.idProduct}
                        ))
                    except:
                        pass
            except:
                pass
        
        # OpenCV 摄像头
        if features.get("opencv", False):
            try:
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    devices.append(_DeviceInfo(
                        "usb_camera", "USB 摄像头 (OpenCV)", IOPortType.USB_CAM,
                        "usb_cam", "opencv", True, aliases=["cam0", "webcam"]
                    ))
                    cap.release()
            except:
                pass
        
        # PCIe 设备
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'NVIDIA' in line or 'AMD' in line:
                    if 'VGA' in line or '3D' in line:
                        devices.append(_DeviceInfo(
                            f"pcie_{line.split()[0]}", f"GPU: {line.strip()}",
                            IOPortType.PCIE, f"pcie_{line.split()[0]}",
                            "pcie", True, aliases=["gpu", "pcie"]
                        ))
                elif 'AI' in line or 'accelerator' in line.lower() or 'NPU' in line:
                    devices.append(_DeviceInfo(
                        f"pcie_ai_{line.split()[0]}", f"AI 加速: {line.strip()}",
                        IOPortType.AI_PCIE, f"pcie_ai_{line.split()[0]}",
                        "pcie_ai", True, aliases=["ai", "ai_pcie"]
                    ))
        except:
            pass
        
        # 开发板专用
        board_map = {
            "jetson": ("Jetson GPIO", IOPortType.JETSON_GPIO, "Jetson.GPIO", "jetson_gpio", ["jetson"]),
            "orange_pi": ("香橙派 GPIO", IOPortType.ORANGE_PI_GPIO, "OPi.GPIO", "orange_gpio", ["orange", "orange_pi"]),
            "rockchip": ("Rockchip GPIO", IOPortType.ROCKCHIP_GPIO, "rockchip_gpio", "rockchip_gpio", ["rockchip", "rk"]),
            "allwinner": ("全志 GPIO", IOPortType.ALLWINNER_GPIO, "allwinner_gpio", "allwinner_gpio", ["allwinner", "aw"]),
            "banana_pi": ("Banana Pi GPIO", IOPortType.BANANA_PI_GPIO, "banana_gpio", "banana_gpio", ["banana", "banana_pi"]),
        }
        if board in board_map:
            name, ptype, driver, port, aliases = board_map[board]
            devices.append(_DeviceInfo(
                port, name, ptype, port, driver, True, aliases=aliases
            ))
        
        return devices

class IOLib:
    """硬件控制库 - IO 子模块"""
    
    def __init__(self):
        self.system_info = _SystemDetector.detect()
        self._devices = _DeviceScanner.scan(self.system_info)
        self.available_devices = [d for d in self._devices if d.available]
        
        # 快捷访问
        self.gpio = self._get_device("gpio")
        self.i2c = self._get_device("i2c")
        self.spi = self._get_device("spi")
        self.uart = self._get_device("uart")
        self.camera = self._get_device("csi_camera") or self._get_device("usb_camera")
        self.gpu = self._get_device("gpu")
        self.ai = self._get_device("ai")
    
    def _get_device(self, name):
        for d in self.available_devices:
            if d.id == name or name in d.aliases:
                return d
        return None
    
    def bind(self, port_spec):
        """绑定设备 - 支持 su 强制绑定"""
        return _PortBinder.bind(port_spec, self.available_devices)
    
    def get(self, port_spec):
        """获取设备信息"""
        for d in self.available_devices:
            if d.port_spec == port_spec or port_spec in d.aliases:
                return d
        return None
    
    def list(self):
        """列出所有可用设备"""
        return self.available_devices.copy()
    
    def summary(self):
        """系统摘要"""
        return {
            "system": self.system_info,
            "device_count": len(self.available_devices),
            "devices": [{"name": d.name, "type": d.port_type, "port": d.port_spec} 
                       for d in self.available_devices]
        }

# ==================== StdLib 统一实例 ====================

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
        
        # 图论算法
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
        
        # ========== IO 硬件控制 ==========
        self.io_lib = IOLib()

# 创建全局实例
std = StdLib()
