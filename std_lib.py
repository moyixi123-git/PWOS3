# ==================== std_lib.py - PWOS3 C++风格全能标准库 ====================

import os, sys, json, time, random, hashlib, datetime, shutil, zipfile, tarfile
import re, base64, csv, sqlite3, subprocess, socket, platform, math, textwrap
import io, glob, fnmatch, tempfile, configparser, logging, string, secrets
import getpass, threading, queue, struct, itertools, collections, enum
from typing import Any, Dict, List, Tuple, Optional, Union, Callable
from collections import OrderedDict, defaultdict, Counter, deque
from functools import wraps
from contextlib import contextmanager

# ==================== C++风格特性 ====================

# 1. 指针和引用模拟
class Ptr:
    """智能指针模拟（类似C++ unique_ptr/shared_ptr）"""
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
    """共享指针（引用计数）"""
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

class Ref:
    """引用包装（模拟C++引用）"""
    def __init__(self, obj):
        self._obj = obj
    def __getattr__(self, name):
        return getattr(self._obj, name)
    def __setattr__(self, name, value):
        if name == '_obj':
            super().__setattr__(name, value)
        else:
            setattr(self._obj, name, value)

# 2. 类型系统增强
class TypeInfo:
    """类型信息（类似C++ typeid）"""
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
    """std::any 模拟"""
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

# 3. 枚举类增强（C++ enum class）
class Enum:
    """强类型枚举"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def items(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}.items()

# 4. 命名空间模拟
class Namespace:
    """命名空间"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# 5. 结构体
class Struct:
    """C++风格结构体"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}
    def __repr__(self):
        items = ', '.join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"Struct({items})"

# ==================== C++ STL容器模拟 ====================

# 6. 动态数组（std::vector）
class Vector:
    """动态数组（类似std::vector）"""
    def __init__(self, data=None, capacity=10):
        self._data = list(data) if data else []
        self._capacity = max(len(self._data), capacity)
    
    def push_back(self, value):
        self._data.append(value)
    
    def pop_back(self):
        return self._data.pop()
    
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

# 7. 链表（std::list）
class ListNode:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

class List:
    """双向链表（类似std::list）"""
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

# 8. 栈（std::stack）
class Stack:
    """栈（类似std::stack）"""
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

# 9. 队列（std::queue）
class Queue:
    """队列（类似std::queue）"""
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

# 10. 优先队列（std::priority_queue）
class PriorityQueue:
    """优先队列"""
    def __init__(self, max_heap=True):
        self._data = []
        self._max_heap = max_heap
    
    def push(self, value, priority=0):
        heapq.heappush(self._data, (-priority if self._max_heap else priority, value))
    
    def pop(self):
        return heapq.heappop(self._data)[1] if self._data else None
    
    def top(self):
        return self._data[0][1] if self._data else None
    
    def size(self) -> int:
        return len(self._data)
    
    def empty(self) -> bool:
        return len(self._data) == 0

# 11. 集合（std::set - 有序集合）
class Set:
    """有序集合"""
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

# 12. 映射（std::map - 有序映射）
class Map:
    """有序映射"""
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

# 13. 对组（std::pair）
class Pair:
    """键值对"""
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def __repr__(self):
        return f"Pair({self.first}, {self.second})"

# 14. 元组增强（std::tuple）
class Tuple:
    """元组增强"""
    def __init__(self, *args):
        self._data = args
    def get(self, index):
        return self._data[index]
    def size(self) -> int:
        return len(self._data)
    def __iter__(self):
        return iter(self._data)

# ==================== C++ 算法库模拟 ====================

# 15. 算法
class Algo:
    """C++算法库（std::algorithm）"""
    
    @staticmethod
    def sort(data: list, reverse=False):
        """排序（std::sort）"""
        return sorted(data, reverse=reverse)
    
    @staticmethod
    def stable_sort(data: list, key=None):
        """稳定排序"""
        return sorted(data, key=key)
    
    @staticmethod
    def sort_partial(data: list, n: int):
        """部分排序（std::partial_sort）"""
        data.sort()
        return data[:n]
    
    @staticmethod
    def find(data: list, value):
        """查找（std::find）"""
        try:
            return data.index(value)
        except ValueError:
            return -1
    
    @staticmethod
    def find_if(data: list, predicate):
        """条件查找（std::find_if）"""
        for i, item in enumerate(data):
            if predicate(item):
                return i
        return -1
    
    @staticmethod
    def count(data: list, value) -> int:
        """计数（std::count）"""
        return data.count(value)
    
    @staticmethod
    def count_if(data: list, predicate) -> int:
        """条件计数（std::count_if）"""
        return sum(1 for item in data if predicate(item))
    
    @staticmethod
    def reverse(data: list) -> list:
        """反转（std::reverse）"""
        return data[::-1]
    
    @staticmethod
    def rotate(data: list, n: int) -> list:
        """旋转（std::rotate）"""
        n = n % len(data)
        return data[n:] + data[:n]
    
    @staticmethod
    def shuffle(data: list) -> list:
        """随机重排（std::shuffle）"""
        result = data.copy()
        random.shuffle(result)
        return result
    
    @staticmethod
    def unique(data: list) -> list:
        """去重（std::unique）"""
        return list(dict.fromkeys(data))
    
    @staticmethod
    def replace(data: list, old, new) -> list:
        """替换（std::replace）"""
        return [new if x == old else x for x in data]
    
    @staticmethod
    def remove_if(data: list, predicate) -> list:
        """条件删除（std::remove_if）"""
        return [x for x in data if not predicate(x)]
    
    @staticmethod
    def transform(data: list, func) -> list:
        """转换（std::transform）"""
        return list(map(func, data))
    
    @staticmethod
    def for_each(data: list, func):
        """遍历（std::for_each）"""
        for item in data:
            func(item)
    
    @staticmethod
    def fill(data: list, value) -> list:
        """填充（std::fill）"""
        return [value] * len(data)
    
    @staticmethod
    def generate(n: int, func) -> list:
        """生成（std::generate）"""
        return [func() for _ in range(n)]
    
    @staticmethod
    def min_element(data: list):
        """最小元素（std::min_element）"""
        return min(data) if data else None
    
    @staticmethod
    def max_element(data: list):
        """最大元素（std::max_element）"""
        return max(data) if data else None
    
    @staticmethod
    def min_max(data: list):
        """最小最大值（std::minmax）"""
        return (min(data), max(data)) if data else (None, None)
    
    @staticmethod
    def binary_search(data: list, value) -> bool:
        """二分查找（std::binary_search）"""
        import bisect
        data = sorted(data)
        i = bisect.bisect_left(data, value)
        return i < len(data) and data[i] == value
    
    @staticmethod
    def lower_bound(data: list, value) -> int:
        """下界（std::lower_bound）"""
        import bisect
        return bisect.bisect_left(sorted(data), value)
    
    @staticmethod
    def upper_bound(data: list, value) -> int:
        """上界（std::upper_bound）"""
        import bisect
        return bisect.bisect_right(sorted(data), value)
    
    @staticmethod
    def next_permutation(data: list) -> list:
        """下一个排列（std::next_permutation）"""
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
    def merge(a: list, b: list) -> list:
        """合并有序序列（std::merge）"""
        result = []
        i = j = 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                result.append(a[i])
                i += 1
            else:
                result.append(b[j])
                j += 1
        result.extend(a[i:])
        result.extend(b[j:])
        return result
    
    @staticmethod
    def set_union(a: list, b: list) -> list:
        """并集（std::set_union）"""
        return list(set(a) | set(b))
    
    @staticmethod
    def set_intersection(a: list, b: list) -> list:
        """交集（std::set_intersection）"""
        return list(set(a) & set(b))
    
    @staticmethod
    def set_difference(a: list, b: list) -> list:
        """差集（std::set_difference）"""
        return list(set(a) - set(b))

# ==================== 内存管理模拟 ====================

class Memory:
    """内存管理（C++风格）"""
    
    @staticmethod
    def alloc(size: int) -> bytearray:
        """分配内存（类似malloc）"""
        return bytearray(size)
    
    @staticmethod
    def memset(data: bytearray, value: int, count: int = None):
        """设置内存（memset）"""
        if count is None:
            count = len(data)
        for i in range(count):
            data[i] = value & 0xFF
    
    @staticmethod
    def memcpy(dst: bytearray, src: bytearray, count: int):
        """内存拷贝（memcpy）"""
        dst[:count] = src[:count]
    
    @staticmethod
    def memcmp(a: bytearray, b: bytearray) -> int:
        """内存比较（memcmp）"""
        return 1 if a > b else (-1 if a < b else 0)
    
    @staticmethod
    def size_of(obj) -> int:
        """获取对象大小（sizeof）"""
        return sys.getsizeof(obj)

# ==================== 输入输出流（iostream） ====================

class IOStream:
    """输入输出流模拟"""
    
    @staticmethod
    def read_line(prompt: str = "") -> str:
        """读取一行（std::cin）"""
        return input(prompt)
    
    @staticmethod
    def read_int(prompt: str = "") -> int:
        """读取整数"""
        return int(input(prompt))
    
    @staticmethod
    def read_float(prompt: str = "") -> float:
        """读取浮点数"""
        return float(input(prompt))
    
    @staticmethod
    def write(*args, **kwargs):
        """写入（std::cout）"""
        print(*args, **kwargs)
    
    @staticmethod
    def error(*args):
        """错误输出（std::cerr）"""
        print(*args, file=sys.stderr)
    
    @staticmethod
    def format(fmt: str, *args) -> str:
        """格式化字符串（sprintf）"""
        return fmt % args if args else fmt
    
    @staticmethod
    def printf(fmt: str, *args):
        """C风格打印"""
        print(fmt % args if args else fmt, end='')

# ==================== 字符串流（stringstream） ====================

class StringStream:
    """字符串流"""
    def __init__(self, s: str = ""):
        self._buffer = io.StringIO(s)
    
    def write(self, s: str):
        self._buffer.write(s)
    
    def read(self) -> str:
        return self._buffer.read()
    
    def str(self) -> str:
        return self._buffer.getvalue()
    
    def __lshift__(self, value):
        """重载 << 运算符"""
        self.write(str(value))
        return self
    
    def __rshift__(self, var):
        """重载 >> 运算符（模拟）"""
        return self.read()

# ==================== 函数对象（functor） ====================

class Functor:
    """函数对象包装"""
    def __init__(self, func=None):
        self._func = func
    
    def __call__(self, *args, **kwargs):
        if self._func:
            return self._func(*args, **kwargs)
    
    @staticmethod
    def create(func):
        return Functor(func)

class Lambda:
    """Lambda包装"""
    def __init__(self, code_str: str, parameters: list = None):
        self._code = compile(code_str, '<lambda>', 'eval')
        self._params = parameters or []
    
    def __call__(self, *args):
        env = dict(zip(self._params, args))
        return eval(self._code, env)

# ==================== 迭代器增强 ====================

class Iterator:
    """增强迭代器"""
    def __init__(self, data):
        self._data = data
        self._index = 0
    
    def has_next(self) -> bool:
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

class Range:
    """增强范围（C++20 ranges）"""
    def __init__(self, start, end=None, step=1):
        if end is None:
            self._start = 0
            self._end = start
        else:
            self._start = start
            self._end = end
        self._step = step
    
    def to_vector(self) -> Vector:
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
    
    def __iter__(self):
        return iter(range(self._start, self._end, self._step))

# ==================== 文件流（fstream） ====================

class FileStream:
    """文件流"""
    def __init__(self, filepath: str, mode: str = 'r'):
        self._filepath = filepath
        self._mode = mode
        self._handle = None
    
    def open(self, filepath: str = None, mode: str = None):
        if filepath:
            self._filepath = filepath
        if mode:
            self._mode = mode
        self._handle = open(self._filepath, self._mode)
        return self
    
    def close(self):
        if self._handle:
            self._handle.close()
    
    def read(self, size: int = -1) -> str:
        return self._handle.read(size) if self._handle else ''
    
    def read_line(self) -> str:
        return self._handle.readline() if self._handle else ''
    
    def read_lines(self) -> list:
        return self._handle.readlines() if self._handle else []
    
    def write(self, data: str):
        if self._handle:
            self._handle.write(data)
    
    def seek(self, pos: int):
        if self._handle:
            self._handle.seek(pos)
    
    def tell(self) -> int:
        return self._handle.tell() if self._handle else 0
    
    def eof(self) -> bool:
        if not self._handle:
            return True
        pos = self._handle.tell()
        data = self._handle.read(1)
        self._handle.seek(pos)
        return not data
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args):
        self.close()

# ==================== 时间库（chrono） ====================

class Chrono:
    """计时器（std::chrono）"""
    def __init__(self):
        self._start = time.time()
    
    def reset(self):
        self._start = time.time()
    
    def elapsed(self) -> float:
        return time.time() - self._start
    
    def elapsed_ms(self) -> int:
        return int((time.time() - self._start) * 1000)
    
    def elapsed_us(self) -> int:
        return int((time.time() - self._start) * 1000000)
    
    @staticmethod
    def now():
        return time.time()
    
    @staticmethod
    def sleep_for(seconds: float):
        time.sleep(seconds)

# ==================== 位操作（bitset） ====================

class Bitset:
    """位集（std::bitset）"""
    def __init__(self, size_or_value, size=None):
        if size is not None:
            self._size = size
            self._value = int(size_or_value)
        else:
            self._value = int(size_or_value) if isinstance(size_or_value, (int, str)) else 0
            self._size = max(8, self._value.bit_length())
    
    def set(self, pos: int, value: bool = True):
        if 0 <= pos < self._size:
            if value:
                self._value |= (1 << pos)
            else:
                self._value &= ~(1 << pos)
    
    def get(self, pos: int) -> bool:
        return bool(self._value & (1 << pos)) if 0 <= pos < self._size else False
    
    def flip(self, pos: int = None):
        if pos is not None:
            self._value ^= (1 << pos)
        else:
            self._value = ~self._value
    
    def count(self) -> int:
        return bin(self._value).count('1')
    
    def size(self) -> int:
        return self._size
    
    def to_int(self) -> int:
        return self._value
    
    def to_binary(self) -> str:
        return bin(self._value)[2:].zfill(self._size)
    
    def to_hex(self) -> str:
        return hex(self._value)[2:].upper()
    
    def __and__(self, other):
        result = Bitset(self._value & other._value, max(self._size, other._size))
        return result
    
    def __or__(self, other):
        result = Bitset(self._value | other._value, max(self._size, other._size))
        return result
    
    def __xor__(self, other):
        result = Bitset(self._value ^ other._value, max(self._size, other._size))
        return result
    
    def __lshift__(self, n):
        return Bitset(self._value << n, self._size)
    
    def __rshift__(self, n):
        return Bitset(self._value >> n, self._size)

# ==================== 常量表达式（constexpr） ====================

class Const:
    """编译时常量模拟"""
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
    """常量表达式装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return Const(func(*args, **kwargs))
    return wrapper

# ==================== 模板元编程模拟 ====================

class Template:
    """模板模拟"""
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
    def forward(value):
        return value
    
    @staticmethod
    def move(value):
        result = value
        del value
        return result

# ==================== 原有实用功能 ====================

class File:
    """文件操作 - 完全修复版"""
    
    @staticmethod
    def _get_base_dir() -> str:
        """获取基础目录（兼容所有模式）"""
        # 先尝试获取调用脚本的目录
        try:
            # 获取主程序所在目录
            import __main__
            if hasattr(__main__, '__file__'):
                return os.path.dirname(os.path.abspath(__main__.__file__))
        except:
            pass
        
        # EXE 模式
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        
        # 备用：当前工作目录（但排除 system32）
        cwd = os.getcwd()
        if 'system32' in cwd.lower():
            # 如果在 system32，就用用户目录
            return os.path.expanduser('~')
        return cwd
    
    @staticmethod
    def get_abs_path(filepath: str) -> str:
        """转换为绝对路径"""
        if os.path.isabs(filepath):
            return filepath
        base_dir = File._get_base_dir()
        return os.path.join(base_dir, filepath)
    
    @staticmethod
    def read(filepath: str, encoding: str = 'utf-8') -> str:
        full_path = File.get_abs_path(filepath)
        try:
            with open(full_path, 'r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            return f"[文件不存在: {full_path}]"
        except Exception as e:
            return f"[错误: {e}]"
    
    @staticmethod
    def write(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
        full_path = File.get_abs_path(filepath)
        try:
            os.makedirs(os.path.dirname(full_path) or '.', exist_ok=True)
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def read_json(filepath: str):
        full_path = File.get_abs_path(filepath)
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(filepath: str, data, indent: int = 2) -> bool:
        full_path = File.get_abs_path(filepath)
        os.makedirs(os.path.dirname(full_path) or '.', exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    
    @staticmethod
    def exists(filepath: str) -> bool:
        return os.path.exists(File.get_abs_path(filepath))
    
    @staticmethod
    def list_dir(directory: str = '.', pattern: str = '*') -> list:
        full_path = File.get_abs_path(directory)
        return glob.glob(os.path.join(full_path, pattern))
    
    @staticmethod
    def mkdir(directory: str) -> bool:
        os.makedirs(File.get_abs_path(directory), exist_ok=True)
        return True
    
    @staticmethod
    def copy(src: str, dst: str) -> bool:
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            return True
        except:
            return False
    
    @staticmethod
    def delete(filepath: str) -> bool:
        try:
            full_path = File.get_abs_path(filepath)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            return True
        except:
            return False

class String:
    @staticmethod
    def md5(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def sha256(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def random(length: int = 8) -> str:
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    @staticmethod
    def truncate(s: str, length: int) -> str:
        return s[:length] + '...' if len(s) > length else s

class Network:
    @staticmethod
    def get(url: str, timeout: int = 30) -> str:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PWOS3/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode('utf-8')
        except:
            return ''
    
    @staticmethod
    def download(url: str, save_path: str) -> bool:
        try:
            urllib.request.urlretrieve(url, save_path)
            return True
        except:
            return False

class Math:
    @staticmethod
    def sum(data: list) -> float:
        return sum(data)
    
    @staticmethod
    def avg(data: list) -> float:
        return sum(data) / len(data) if data else 0
    
    @staticmethod
    def max(data: list):
        return max(data) if data else None
    
    @staticmethod
    def min(data: list):
        return min(data) if data else None

class TimeDate:
    @staticmethod
    def now(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.datetime.now().strftime(fmt)
    
    @staticmethod
    def timestamp() -> int:
        return int(time.time())

class Random:
    @staticmethod
    def int_range(min_val: int, max_val: int) -> int:
        return random.randint(min_val, max_val)
    
    @staticmethod
    def float_range(min_val: float, max_val: float) -> float:
        return random.uniform(min_val, max_val)
    
    @staticmethod
    def choice(data: list):
        return random.choice(data) if data else None

class Color:
    @staticmethod
    def red(text: str) -> str:
        return f"\033[91m{text}\033[0m"
    
    @staticmethod
    def green(text: str) -> str:
        return f"\033[92m{text}\033[0m"
    
    @staticmethod
    def yellow(text: str) -> str:
        return f"\033[93m{text}\033[0m"
    
    @staticmethod
    def blue(text: str) -> str:
        return f"\033[94m{text}\033[0m"
    
    @staticmethod
    def cyan(text: str) -> str:
        return f"\033[96m{text}\033[0m"

# ==================== 标准库实例 ====================

class StdLib:
    """PWOS3 C++风格全能标准库"""
    
    def __init__(self):
        # C++风格容器
        self.vector = Vector
        self.list = List
        self.stack = Stack
        self.queue = Queue
        self.priority_queue = PriorityQueue
        self.set = Set
        self.map = Map
        self.pair = Pair
        self.tuple = Tuple
        
        # C++风格算法
        self.algo = Algo()
        
        # C++风格特性
        self.ptr = Ptr
        self.shared_ptr = SharedPtr
        self.ref = Ref
        self.any = AnyType
        self.enum = Enum
        self.struct = Struct
        self.namespace = Namespace
        self.type_info = TypeInfo()
        
        # 内存管理
        self.memory = Memory()
        
        # IO流
        self.io = IOStream()
        self.string_stream = StringStream
        self.file_stream = FileStream
        
        # 函数对象
        self.functor = Functor
        self.lambda_ = Lambda
        
        # 迭代器
        self.iterator = Iterator
        self.range = Range
        
        # 计时器
        self.chrono = Chrono
        
        # 位操作
        self.bitset = Bitset
        
        # 常量
        self.const = Const
        self.constexpr = constexpr
        
        # 模板
        self.template = Template()
        
        # 原有实用功能
        self.file = File()
        self.string = String()
        self.network = Network()
        self.math = Math()
        self.timedate = TimeDate()
        self.random = Random()
        self.color = Color()

std = StdLib()

# ==================== 使用示例 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("PWOS3 C++风格标准库测试")
    print("=" * 60)
    
    # 1. Vector测试
    print("\n📦 Vector（动态数组）测试:")
    v = Vector([1, 2, 3])
    v.push_back(4)
    v.push_back(5)
    print(f"  大小: {v.size()}, 容量: {v.capacity()}")
    print(f"  内容: {v.data()}")
    v.sort()
    print(f"  排序后: {v.data()}")
    
    # 2. Map测试
    print("\n🗺️ Map（有序映射）测试:")
    m = Map()
    m.insert("name", "张三")
    m.insert("age", 25)
    m.insert("city", "北京")
    for key in m.keys():
        print(f"  {key}: {m.at(key)}")
    
    # 3. 算法测试
    print("\n🔍 算法测试:")
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    sorted_data = Algo.sort(data)
    print(f"  排序: {sorted_data}")
    print(f"  最小值: {Algo.min_element(data)}")
    print(f"  最大值: {Algo.max_element(data)}")
    unique_data = Algo.unique(data)
    print(f"  去重: {unique_data}")
    
    # 4. 位操作测试
    print("\n💻 位操作测试:")
    bits = Bitset(0b1010)
    print(f"  二进制: {bits.to_binary()}")
    print(f"  第1位: {bits.get(1)}")
    print(f"  1的个数: {bits.count()}")
    
    # 5. 计时器测试
    print("\n⏱️ 计时器测试:")
    timer = Chrono()
    time.sleep(0.5)
    print(f"  耗时: {timer.elapsed():.3f}秒")
    
    print("\n✅ 测试完成！")