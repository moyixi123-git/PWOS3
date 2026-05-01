# PWOS3
请查看README文件。Please check the README file.
# ⚡ PWOS3 - Python 一体化学习平台

> 由于本项目出自于中国，暂时没有英语版本，需要的用户请自行用其他软件翻译。
> As this project originates from China, there is no English version available at the moment. Users who need it please translate it themselves using other software.

>如果需要下载EXE文件，请前往pwos.cpolar.top进行下载。If you need to download the EXE file, please go to pwos.cpolar. top to do so.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![平台](https://img.shields.io/badge/平台-Windows%20%7C%20Linux%20%7C%20macOS-green)
![许可证](https://img.shields.io/badge/许可证-MIT-yellow)
![版本](https://img.shields.io/badge/版本-v3.0-red)

> 开源跨平台 Python 一体化学习平台，纯命令行界面，轻量高效  
> Open source cross-platform Python integrated learning platform, pure command line interface, lightweight and efficient

> 官方网站 / Official Website：[pwos.cpolar.top](https://pwos.cpolar.top)  
> 联系邮箱 / Contact Email：youismoyixi@qq.com

---

## 🎯 项目简介
## Project Introduction

PWOS3 是一个开源的 Python 一体化学习平台。它运行在纯命令行界面上，集脚本引擎、用户管理系统、AI智能助手、网络工具、安全防护于一体，无需图形界面，资源占用极低，支持 Windows、Linux、macOS 跨平台运行。

PWOS3 is an open-source Python integrated learning platform. It runs on a pure command-line interface, integrating script engine, user management system, AI intelligent assistant, network tools, and security protection. No graphical interface is required, resource usage is extremely low, and it supports cross-platform operation on Windows, Linux, and macOS.

---

## ✨ 核心功能
## Core Features

- **👥 用户管理**：添加、查看、查找、删除用户，多文件分组管理，数据备份恢复，CSV/JSON 导入导出
- **👥 User Management**: Add, view, search, delete users, multi-file group management, data backup and recovery, CSV/JSON import and export

- **🔐 安全防护**：PBKDF2 密码加密存储，防火墙规则设置，IP 黑白名单，防暴力破解，安全审计日志
- **🔐 Security Protection**: PBKDF2 password encryption storage, firewall rule settings, IP blacklist and whitelist, anti-brute force cracking, security audit logs

- **🌐 网络工具**：端口扫描（快速/自定义/指定端口），DNS 查询，网络测速，网络接口信息查看
- **🌐 Network Tools**: Port scanning (quick/custom/specific port), DNS query, network speed test, network interface information viewing

- **🤖 AI 助手**：支持 DeepSeek API 和阿里云通义千问 API，可加载本地 GGUF 大模型，提供智能对话和系统分析
- **🤖 AI Assistant**: Supports DeepSeek API and Alibaba Cloud Tongyi Qianwen API, can load local GGUF large models, provides intelligent dialogue and system analysis

- **🖥️ 命令行模式**：提供原生、Windows、Linux 三种命令行风格切换，命令历史记录，文件管理，进程管理，磁盘/内存信息查看
- **🖥️ Command Line Mode**: Provides native, Windows, and Linux command line style switching, command history, file management, process management, disk/memory information viewing

- **📝 PWOS 脚本引擎**：支持 `.pwos` 自定义脚本，可使用 `#main`、`#func`、`#import` 等标签编写自动化任务
- **📝 PWOS Script Engine**: Supports `.pwos` custom scripts, can use `#main`, `#func`, `#import` tags to write automated tasks

- **📦 标准库 std**：内置 C++ 风格 STL 容器（Vector、Map、Stack、Queue）、算法、智能指针、位操作等，让 Python 拥有 C++ 的强大特性
- **📦 Standard Library std**: Built-in C++ style STL containers (Vector, Map, Stack, Queue), algorithms, smart pointers, bit operations, giving Python the powerful features of C++

- **🔄 系统更新**：智能集成更新、手动更新、安全补丁检查、紧急修复功能
- **🔄 System Update**: Intelligent integrated update, manual update, security patch check, emergency repair function

- **📋 库依赖管理**：自动检测缺失库，一键安装，选择性安装，适配 EXE 和源码环境
- **📋 Library Dependency Management**: Automatic detection of missing libraries, one-click installation, selective installation, compatible with EXE and source code environments

- **🔧 开发者模式**：隐藏的高级功能，用于系统诊断、性能测试、批量操作等
- **🔧 Developer Mode**: Hidden advanced features for system diagnosis, performance testing, batch operations, etc.

---

## 🚀 快速开始
## Quick Start

### 方式一：EXE 版本（推荐普通用户）
### Method 1: EXE Version (Recommended for Regular Users)

1. 下载 `PWOS3.exe`
2. 双击运行  
**无需安装 Python 或任何依赖，开箱即用。** 部分功能（AI助手、更新检查、网络测速等）需要网络连接。

1. Download `PWOS3.exe`
2. Double-click to run  
**No need to install Python or any dependencies, ready to use out of the box.** Some features (AI assistant, update check, network speed test, etc.) require an internet connection.

### 方式二：源码版本（推荐开发者）
### Method 2: Source Code Version (Recommended for Developers)

```bash
git clone https://github.com/moyixi123-git/PWOS3.git
cd PWOS3
python PWOS3.py
```

系统内置自动依赖安装功能。启动后若检测到缺少第三方库，会询问是否自动安装，选择"是"即可一键安装。即使不安装，系统也能正常运行，仅部分增强功能（如表格美化、系统资源监控等）暂不可用。

The system has a built-in automatic dependency installation feature. After startup, if missing third-party libraries are detected, it will ask whether to install them automatically. Select "Yes" to install with one click. Even without installation, the system can run normally, only some enhanced features (such as table beautification, system resource monitoring, etc.) are temporarily unavailable.

---

📥 下载

Download

文件 File 说明 Description

PWOS3.exe Windows 可执行文件，无需 Python 环境，下载即用 / Windows executable file, no Python environment required, ready to use

PWOS3.py Python 源代码，需要 Python 3.8 及以上版本 / Python source code, requires Python 3.8 or above

std_lib.py C++ 风格全能标准库，供 PWOS 脚本导入使用 / C++ style all-in-one standard library for PWOS script import

---

📖 PWOS 脚本编写教程

PWOS Script Writing Tutorial

脚本文件以 .pwos 为后缀，放置在 scripts/ 目录下，系统会自动加载并显示在主菜单中。

Script files use the .pwos extension and are placed in the scripts/ directory. The system will automatically load and display them in the main menu.

基本语法

Basic Syntax

标签 Tag 说明 Description
#main 编号: 定义一个菜单脚本块，编号决定显示顺序 / Define a menu script block, number determines display order
#main 编号 stop 结束该脚本块 / End the script block
#func 函数名: 定义一个函数 / Define a function
#func stop 结束函数定义 / End function definition
#import 库名 导入标准库（如 #import std） / Import standard library (e.g. #import std)

Hello World

```
#main 1:
print("Hello, PWOS3!")
print("这是我的第一个脚本")
#main 1 stop
```

文件操作 / File Operations

```
#main 2:
#import std

std.file.write("hello.txt", "你好，PWOS3！")
content = std.file.read("hello.txt")
print(f"文件内容: {content}")
print(f"File content: {content}")

users = [{"name": "张三", "age": 25}, {"name": "李四", "age": 30}]
std.file.write_json("users.json", users)
data = std.file.read_json("users.json")
print(f"用户数量: {len(data)}")
print(f"User count: {len(data)}")
#main 2 stop
```

C++ 风格容器 / C++ Style Containers

```
#main 3:
#import std

v = std.vector([3, 1, 4, 1, 5])
v.push_back(9)
v.sort()
print(f"排序后: {v.data()}")
print(f"After sorting: {v.data()}")

m = std.map()
m.insert("name", "张三")
m.insert("age", 25)
for key in m.keys():
    print(f"  {key}: {m.at(key)}")
#main 3 stop
```

数据处理 / Data Processing

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
print(f"Average score: {std.math.avg(scores):.1f}")
print(f"最高分: {std.math.max(scores)}")
print(f"Highest score: {std.math.max(scores)}")

sorted_students = std.algo.sort(students, key=lambda x: x["score"], reverse=True)
for i, s in enumerate(sorted_students, 1):
    print(f"  {i}. {s['name']}: {s['score']}分")
#main 4 stop
```

网络与系统信息 / Network and System Info

```
#main 5:
#import std
import socket

ip = socket.gethostbyname("www.baidu.com")
print(f"百度IP: {ip}")
print(f"Baidu IP: {ip}")

info = std.system.info()
print(f"操作系统: {info['system']}")
print(f"Operating system: {info['system']}")
print(f"当前时间: {std.timedate.now()}")
print(f"Current time: {std.timedate.now()}")
#main 5 stop
```

加密与随机 / Encryption and Random

```
#main 6:
#import std

print(f"MD5: {std.crypto.md5('hello')}")
print(f"SHA256: {std.crypto.sha256('hello')}")
print(f"随机数: {std.random.int_range(1, 100)}")
print(f"Random number: {std.random.int_range(1, 100)}")
print(f"UUID: {std.random.uuid()}")
#main 6 stop
```

自定义函数 / Custom Functions

```
#func calc_sum:
a = 10
b = 20
print(f"{a} + {b} = {a + b}")
#func stop

#main 7:
print("调用自定义函数:")
print("Call custom function:")
#call calc_sum
#main 7 stop
```

---

📂 项目结构

Project Structure

```
PWOS3/
├── PWOS3.exe                # Windows 可执行文件 / Windows executable file
├── PWOS3.py                 # 主程序源码 / Main program source code
├── std_lib.py               # C++ 风格标准库 / C++ style standard library
├── scripts/                 # 存放 .pwos 脚本 / Store .pwos scripts
└── user_system_data/        # 用户数据（自动生成） / User data (auto-generated)
```

---

🔧 开发者模式

Developer Mode

在主菜单的选项输入框中输入 a1b2c3d4e5，即可激活开发者模式。该模式提供：

Enter a1b2c3d4e5 in the main menu option input box to activate developer mode. This mode provides:

· 系统内部状态查看 / System internal status viewing
· 数据库诊断 / Database diagnosis
· 性能测试 / Performance testing
· 调试日志级别调整 / Debug log level adjustment
· 批量数据操作（添加测试用户、清理测试数据） / Batch data operations (add test users, clean test data)
· 进程管理 / Process management
· 磁盘与内存详细信息 / Disk and memory detailed information
· 修改系统版本号 / Modify system version number
· 紧急系统修复 / Emergency system repair

---

📊 系统要求

System Requirements

项目 Item EXE 版本 EXE Version 源码版本 Source Version
操作系统 / OS Windows 10/11 Windows / Linux / macOS
Python 版本 / Python Version 不需要 / Not required Python 3.8+
内存 / Memory 512 MB 以上 / 512 MB+ 512 MB 以上 / 512 MB+
磁盘空间 / Disk Space 200 MB 以上 / 200 MB+ 200 MB 以上 / 200 MB+
依赖项 / Dependencies 无需安装 / Not required 可选（系统可自动安装） / Optional (system can auto-install)

---

❓ 常见问题

FAQ

Q: EXE 打不开或被杀毒软件拦截？
A: 因为 EXE 是 PyInstaller 打包的，某些杀毒软件可能误报。请添加信任或使用源码运行。

Q: EXE won't open or blocked by antivirus?
A: Because the EXE is packaged by PyInstaller, some antivirus software may falsely report it. Please add trust or use the source code to run.

Q: 如何配置 AI 助手？
A: 进入主菜单 → 选择"AI智能助手" → 选择"配置DeepSeek"或"配置阿里云"，填入从官方获取的 API Key 并启用即可。

Q: How to configure AI Assistant?
A: Go to main menu → Select "AI智能助手" → Select "配置DeepSeek" or "配置阿里云", fill in the API Key obtained from the official website and enable it.

Q: 脚本中的文件保存在哪里？
A: 脚本中的相对路径默认基于 PWOS3 程序所在目录。建议使用绝对路径或先调用 std.file.get_abs_path() 确认位置。

Q: Where are the files in the script saved?
A: The relative paths in the script are based on the directory where the PWOS3 program is located by default. It is recommended to use absolute paths or call std.file.get_abs_path() to confirm the location first.

Q: 源码运行时提示缺少库怎么办？
A: 系统会自动提示安装，选择"是"即可。也可手动执行 pip install requests psutil cryptography。

Q: What to do if it prompts missing libraries when running source code?
A: The system will automatically prompt for installation, select "Yes". You can also manually execute pip install requests psutil cryptography.

---

🤝 贡献

Contributing

欢迎提交 Issue 和 Pull Request！参与步骤：

Welcome to submit Issues and Pull Requests! Steps to participate:

1. Fork 本仓库 / Fork this repository
2. 创建特性分支 / Create feature branch (git checkout -b feature/xxx)
3. 提交修改 / Commit changes (git commit -m '添加xxx功能')
4. 推送分支 / Push branch (git push origin feature/xxx)
5. 提交 Pull Request / Submit Pull Request

---

📜 许可证

License

本项目采用 MIT License 开源协议。您可以自由使用、修改和分发代码。

This project is licensed under the MIT License. You are free to use, modify, and distribute the code.

---

👨‍💻 作者

Author

维护者 / Maintainer：moyixi123-git
官方网站 / Official Website：pwos.cpolar.top
联系邮箱 / Contact Email：youismoyixi@qq.com

---

如果这个项目对你有帮助，请点个 ⭐ Star 支持一下！
If this project is helpful to you, please give it a ⭐ Star!

```
