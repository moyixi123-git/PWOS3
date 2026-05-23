# ⚡ PWOS3 - Python 一体化学习平台

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![平台](https://img.shields.io/badge/平台-Windows%20%7C%20Linux%20%7C%20macOS-green)
![许可证](https://img.shields.io/badge/许可证-MIT-yellow)
![版本](https://img.shields.io/badge/版本-v3.1-red)

> 开源跨平台 Python 一体化学习平台，纯命令行界面，轻量高效

🌐 官方网站：[pwos.cpolar.top](https://pwos.cpolar.top)

📧 联系邮箱：youismoyixi@qq.com

📥 EXE版本请前往官方网站下载

---

## 🎯 项目简介

PWOS3 是一个开源的 Python 一体化学习平台。它运行在纯命令行界面上，集脚本引擎、用户管理系统、AI智能助手、网络工具、安全防护于一体，无需图形界面，资源占用极低，支持 Windows、Linux、macOS 跨平台运行。

---

## ✨ 核心功能

- 👥 **用户管理**：添加、查看、查找、删除用户，多文件分组管理，数据备份恢复，CSV/JSON 导入导出

- 🔐 **安全防护**：PBKDF2 密码加密存储，防火墙规则设置，IP 黑白名单，防暴力破解，安全审计日志

- 🌐 **网络工具**：端口扫描（快速/自定义/指定端口），DNS 查询，网络测速，网络接口信息查看

- 🤖 **AI 助手**：支持 DeepSeek API 和阿里云通义千问 API，可加载本地 GGUF 大模型，提供智能对话和系统分析

- 🖥️ **命令行模式**：提供原生、Windows、Linux 三种命令行风格切换，命令历史记录，文件管理，进程管理，磁盘/内存信息查看

- 📝 **PWOS 脚本引擎**：支持 .pwos 自定义脚本，可使用 #main、#func、#import 等标签编写自动化任务

- 📦 **标准库 std**：内置 C++ 风格 STL 容器（Vector、Map、Stack、Queue）、算法、智能指针、位操作等，让 Python 拥有 C++ 的强大特性

- 🔄 **系统更新**：智能集成更新、手动更新、安全补丁检查、紧急修复功能

- 📋 **库依赖管理**：自动检测缺失库，一键安装，选择性安装，适配 EXE 和源码环境

- 🔧 **开发者模式**：隐藏的高级功能，用于系统诊断、性能测试、批量操作等

---

## 🚀 快速开始

### EXE 版本（推荐普通用户）

1. 下载 PWOS3.exe
2. 双击运行

无需安装 Python 或任何依赖，开箱即用。部分功能（AI助手、更新检查、网络测速等）需要网络连接。

📥 EXE版本请前往官方网站下载：pwos.cpolar.top

### 源码版本（推荐开发者）

```bash
git clone https://github.com/moyixi123-git/PWOS3.git
cd PWOS3
python PWOS3.py
```

系统内置自动依赖安装功能。启动后若检测到缺少第三方库，会询问是否自动安装，选择"是"即可一键安装。即使不安装，系统也能正常运行，仅部分增强功能（如表格美化、系统资源监控等）暂不可用。

---

## 📥 下载

| 文件 | 说明 |
|------|------|
| PWOS3.py | Python 源代码，需要 Python 3.8 及以上版本 |
| std_lib.py | C++ 风格全能标准库，供 PWOS 脚本导入使用 |

📥 EXE版本请前往官方网站下载：pwos.cpolar.top

---

## 📖 PWOS 脚本编写教程

脚本文件以 .pwos 为后缀，放置在 `scripts/` 目录下，系统会自动加载并显示在主菜单中。

### 基本语法

| 标签 | 说明 |
|------|------|
| `#main 编号:` | 定义一个菜单脚本块，编号决定显示顺序 |
| `#main 编号 stop` | 结束该脚本块 |
| `#func 函数名:` | 定义一个函数 |
| `#func stop` | 结束函数定义 |
| `#import 库名` | 导入标准库（如 `#import std`） |

> 💡 **函数调用**：函数定义后，直接在代码中使用函数名即可调用，无需特殊指令。

### Hello World

```
#main 1:
print("Hello, PWOS3!")
print("这是我的第一个脚本")
#main 1 stop
```

### 文件操作

```
#main 2:
#import std

# 注意：文件会保存在 PWOS3 程序目录下，而不是 scripts/ 目录
std.file.write("hello.txt", "你好，PWOS3！")
content = std.file.read("hello.txt")
print(f"文件内容: {content}")

users = [{"name": "张三", "age": 25}, {"name": "李四", "age": 30}]
std.file.write_json("users.json", users)
data = std.file.read_json("users.json")
print(f"用户数量: {len(data)}")
#main 2 stop
```

### C++ 风格容器

```
#main 3:
#import std

v = std.vector([3, 1, 4, 1, 5])
v.push_back(9)
v.sort()
print(f"排序后: {v.data()}")

m = std.map()
m.insert("name", "张三")
m.insert("age", 25)
for key in m.keys():
    print(f"  {key}: {m.at(key)}")
#main 3 stop
```

### 数据处理

```
#main 4:
#import std

students = [
    {"name": "张三", "score": 85},
    {"name": "李四", "score": 92},
    {"name": "王五", "score": 78}
]
scores = [s["score"] for s in students]
print(f"平均分: {std.math.avg(scores):.1f}")
print(f"最高分: {std.math.max(scores)}")

sorted_students = std.algo.sort(students, key=lambda x: x["score"], reverse=True)
for i, s in enumerate(sorted_students, 1):
    print(f"  {i}. {s['name']}: {s['score']}分")
#main 4 stop
```

### 网络与系统信息

```
#main 5:
#import std
import socket

ip = socket.gethostbyname("www.baidu.com")
print(f"百度IP: {ip}")

info = std.system.info()
print(f"操作系统: {info['system']}")
print(f"当前时间: {std.timedate.now()}")
#main 5 stop
```

### 加密与随机

```
#main 6:
#import std

print(f"MD5: {std.crypto.md5('hello')}")
print(f"SHA256: {std.crypto.sha256('hello')}")
print(f"随机数: {std.random.int_range(1, 100)}")
print(f"UUID: {std.random.uuid()}")
#main 6 stop
```

### 自定义函数

```
#func calc_sum:
a = 10
b = 20
print(f"{a} + {b} = {a + b}")
#func stop

#func say_hello:
print("Hello from function!")
#func stop

#main 7:
print("调用自定义函数:")
calc_sum()
say_hello()
#main 7 stop
```

---

## 📂 项目结构

```
PWOS3/
├── PWOS3.py              # 主程序
├── std_lib.py            # 标准库
├── scripts/              # 用户脚本目录
│   └── *.pwos            # 脚本文件
├── update_packages/      # 更新包目录
└── user_system_data/     # 用户数据目录
```

---

## 🔧 开发者模式

在主菜单输入 `a1b2c3d4e5` 激活开发者模式，提供以下功能：

- 系统内部状态查看
- 数据库诊断
- 性能测试
- 调试日志级别调整
- 批量数据操作
- 进程管理
- 磁盘与内存详细信息
- 修改系统版本号
- 紧急系统修复

---

## 📊 系统要求

| | EXE 版本 | 源码版本 |
|------|----------|----------|
| 操作系统 | Windows 10/11 | Windows / Linux / macOS |
| Python | 不需要 | Python 3.8+ |
| 内存 | 512 MB 以上 | 512 MB 以上 |
| 磁盘 | 200 MB 以上 | 200 MB 以上 |
| 依赖 | 无需安装 | 可选（系统可自动安装） |

---

## ❓ 常见问题

**Q: EXE 打不开或被杀毒软件拦截？**

A: 因为 EXE 是 PyInstaller 打包的，某些杀毒软件可能误报。请添加信任或使用源码运行。

**Q: 如何配置 AI 助手？**

A: 进入主菜单 → 选择"AI智能助手" → 配置DeepSeek或阿里云，填入API Key并启用。

**Q: 脚本中的文件保存在哪里？**

A: 相对路径默认基于 PWOS3 程序所在目录，而非 `scripts/` 目录。如需保存到脚本目录，可使用 `os.path.dirname(__file__)` 获取脚本路径。

**Q: 源码运行时提示缺少库怎么办？**

A: 系统会自动提示安装，选择"是"即可。也可手动执行 `pip install requests psutil cryptography`。

**Q: 如何调用自定义函数？**

A: 函数定义后，直接使用函数名调用即可，如 `calc_sum()`，不需要 `#call` 指令。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request：

1. Fork 本仓库
2. 创建分支：`git checkout -b feature/xxx`
3. 提交修改：`git commit -m '添加xxx功能'`
4. 推送分支：`git push origin feature/xxx`
5. 提交 Pull Request

---

## 📜 许可证

本项目采用 MIT License 开源协议。

---

## 👨‍💻 作者

维护者：moyixi123-git

官方网站：pwos.cpolar.top

联系邮箱：youismoyixi@qq.com

---

⭐ 如果这个项目对你有帮助，请点个 Star 支持一下！

---

## English Version

> Since this project originates from China, there is currently no complete English version. Users who need it please use translation software. If you want to download the EXE version, please visit the official website.

# ⚡ PWOS3 - Python Integrated Learning Platform

> Open source cross-platform Python integrated learning platform, pure command line interface, lightweight and efficient

🌐 Official Website: pwos.cpolar.top

📧 Contact Email: youismoyixi@qq.com

📥 Download EXE version: Please visit the official website

---

## Project Introduction

PWOS3 is an open-source Python integrated learning platform running on a pure command-line interface. It integrates a script engine, user management system, AI assistant, network tools, and security protection. No GUI is required, resource usage is extremely low, and it supports cross-platform operation on Windows, Linux, and macOS.

---

## Core Features

- **User Management**: Add, view, search, delete users, multi-file group management, data backup and recovery, CSV/JSON import/export

- **Security Protection**: PBKDF2 password encryption, firewall rules, IP blacklist/whitelist, anti-brute force, security audit logs

- **Network Tools**: Port scanning (quick/custom/specific), DNS query, network speed test, network interface info

- **AI Assistant**: Supports DeepSeek API and Alibaba Cloud Tongyi Qianwen API, can load local GGUF models

- **Command Line Mode**: Native, Windows, Linux style switching, command history, file/process management, disk/memory info

- **PWOS Script Engine**: Custom .pwos scripts with #main, #func, #import tags

- **Standard Library std**: C++ style STL containers (Vector, Map, Stack, Queue), algorithms, smart pointers, bit operations

- **System Update**: Intelligent update, manual update, security patch check, emergency repair

- **Library Dependency Management**: Auto-detect missing libraries, one-click install, selective install

- **Developer Mode**: Hidden advanced features for system diagnosis, performance testing, batch operations

---

## Quick Start

### EXE Version (Recommended)

1. Download PWOS3.exe
2. Double-click to run

No Python or dependencies required. Some features need internet connection.

📥 Download EXE: Visit the official website pwos.cpolar.top

### Source Code Version (Developers)

```bash
git clone https://github.com/moyixi123-git/PWOS3.git
cd PWOS3
python PWOS3.py
```

Built-in auto dependency installation. Missing libraries will prompt for installation on startup.

---

## Download

| File | Description |
|------|------|
| PWOS3.py | Python source code, requires Python 3.8+ |
| std_lib.py | C++ style standard library |

📥 EXE version: Available on the official website

---

## PWOS Script Tutorial

Script files use .pwos extension, placed in scripts/ directory.

### Basic Syntax

| Tag | Description |
|------|------|
| `#main number:` | Define a menu script block |
| `#main number stop` | End script block |
| `#func name:` | Define a function |
| `#func stop` | End function |
| `#import lib` | Import standard library |

> 💡 **Function Call**: After defining a function, just use the function name directly to call it.

### Hello World

```
#main 1:
print("Hello, PWOS3!")
#main 1 stop
```

### File Operations

```
#main 2:
#import std
std.file.write("hello.txt", "Hello PWOS3!")
content = std.file.read("hello.txt")
print(f"Content: {content}")
#main 2 stop
```

### C++ Style Containers

```
#main 3:
#import std
v = std.vector([3, 1, 4, 1, 5])
v.push_back(9)
v.sort()
print(v.data())
#main 3 stop
```

### Data Processing

```
#main 4:
#import std
students = [{"name":"Zhang","score":85},{"name":"Li","score":92}]
scores = [s["score"] for s in students]
print(f"Average: {std.math.avg(scores):.1f}")
#main 4 stop
```

### Network Tools

```
#main 5:
#import std
import socket
ip = socket.gethostbyname("www.google.com")
print(f"IP: {ip}")
print(std.timedate.now())
#main 5 stop
```

### Encryption

```
#main 6:
#import std
print(std.crypto.md5("hello"))
print(std.random.uuid())
#main 6 stop
```

### Custom Functions

```
#func add:
print(10 + 20)
#func stop

#func say_hello:
print("Hello!")
#func stop

#main 7:
print("Calling functions:")
add()
say_hello()
#main 7 stop
```

---

## Project Structure

```
PWOS3/
├── PWOS3.py              # Main program
├── std_lib.py            # Standard library
├── scripts/              # User scripts directory
│   └── *.pwos            # Script files
├── update_packages/      # Update packages directory
└── user_system_data/     # User data directory
```

---

## Developer Mode

Enter `a1b2c3d4e5` in the main menu to activate developer mode.

---

## System Requirements

| | EXE Version | Source Version |
|------|----------|----------|
| OS | Windows 10/11 | Windows/Linux/macOS |
| Python | Not required | 3.8+ |
| Memory | 512 MB+ | 512 MB+ |
| Disk | 200 MB+ | 200 MB+ |
| Dependencies | Not required | Optional |

---

## FAQ

**Q: EXE blocked by antivirus?**

A: It's packaged by PyInstaller, may trigger false positives. Add to trust list or use source code.

**Q: How to configure AI Assistant?**

A: Main menu → AI Assistant → Configure API Key.

**Q: Where are files saved in scripts?**

A: Relative paths are based on the PWOS3 program directory, not the `scripts/` directory.

**Q: Missing libraries when running source code?**

A: System will prompt for auto-installation, or run `pip install requests psutil cryptography`.

**Q: How to call custom functions?**

A: After defining a function, use the function name directly to call it, e.g., `calc_sum()`.

---

## Contributing

1. Fork this repository
2. Create branch: `git checkout -b feature/xxx`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/xxx`
5. Submit Pull Request

---

## License

MIT License

---

## Author

Maintainer: moyixi123-git

Website: pwos.cpolar.top

Email: youismoyixi@qq.com

---

⭐ Star this project if you find it helpful!
```
