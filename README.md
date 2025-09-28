# Titizz — 批量解压工具

这是一个面向 Windows 的小工具，用来批量解压 7z / 7zz 压缩包、收集图片并清理临时文件。项目包含一个图形化（PyQt）进度窗口以及控制台运行模式，支持打包为单个可执行文件并集成到资源管理器右键菜单。
## 主要特性
- 支持 `.7z` 和 `.7zz` 压缩包（默认密码：`momo.moe`）
- 自动将图片收集到 `all_images` 目录
- 自动清理中间解压目录
- 可选择 GUI（默认）或控制台运行（`--console`）
- 可打包为单文件 exe 并生成右键菜单注册表文件
---

## 快速开始（开发者）

1) 激活虚拟环境（PowerShell）

```powershell
. .\.venv\Scripts\Activate.ps1

2) 安装（可选）依赖（如果需要在开发环境运行 GUI / 生成图标）：

```powershell
# 批量解压工具使用说明

## 🔧 开发与构建

### 环境要求
- Python 3.8+
- Windows 系统（用于生成注册表文件）

### 项目结构
# 在 venv 中
pip install PyQt5 Pillow pyinstaller
```
3) 运行主脚本（默认 GUI）

```powershell
python titizz_extract.py <目标目录>
```
# 或不传目录则使用当前目录
python titizz_extract.py

4) 强制控制台模式（无 GUI）

```powershell
python titizz_extract.py --console <目标目录>
```
5) 打包（如果你需要生成 exe）：

```powershell
python build_tool.py
```
构建脚本会尝试检查虚拟环境、安装 PyInstaller（如缺失）、生成 icon 与使用 PyInstaller 打包。

---

## 使用（最终用户）

安装完毕后，你可以：
- 双击 `add_context_menu.reg` 将程序注册为资源管理器右键菜单项（请以管理员权限运行注册表导入）。
- 在目标文件夹右键选择“批量解压7z文件”开始处理。

处理流程简述：程序会解压压缩包、对内部嵌套压缩包做二次解压、把图片移动到 `all_images` 文件夹、然后清理临时目录。

---

## GUI 与控制台行为
- 默认会使用内建的 PyQt5 进度窗口（若未安装 PyQt5，会回退到控制台输出）。
- 在 GUI 模式下，进度窗口会在处理完成后自动关闭；控制台模式则会在结尾等待按键（Windows 下为“按任意键退出...”）。

---

## 常见问题（FAQ）

- Q: 右键菜单没有出现？
   - A: 确认已运行 `add_context_menu.reg`，必要时以管理员身份运行并重启资源管理器。

- Q: 解压失败或报错？
   - A: 检查压缩包是否损坏、密码是否为 `momo.moe`、磁盘空间和杀毒软件设置。

- Q: GUI 窗口闪烁或出现临时控制台窗口？
   - A: 打包后请确保 `dist\titizz_extract.exe` 的快捷方式或注册表项直接指向 exe（不要通过 cmd / powershell wrapper）。脚本已尽量使用 Windows 子进程标志隐藏 7z 控制台窗口。

---

## 高级说明（开发者）

- 源码入口：`titizz_extract.py`。
- 打包配置：`titizz_extract.spec`（如果你需要自定义 PyInstaller 行为可编辑）。
- 图标生成：项目内含脚本用于生成 multi-size ico（Pillow）。

### 构建：生成不包含 Qt 界面的 exe（仅控制台）

如果你需要构建一个不包含 PyQt GUI 的控制台版 exe（例如减小体积或避免打包 PyQt），有两种常用方式：

- 方法 A — 修改 spec 文件（推荐，可复现）：
   1. 打开 `titizz_extract.spec`，将 `console=True`（确保是控制台打包），并在 `EXCLUDES` 或 `excludedimports`/`excludes` 中加入 `PyQt5` 和 `qt_progress`（或移除与 PyQt 相关的 hiddenimports）。
   2. 保存后使用 PyInstaller 读取该 spec：

```powershell
pyinstaller .\titizz_extract.spec
```

   这样 PyInstaller 会按 spec 的配置生成一个不包含 Qt 的控制台 exe。

- 方法 B — 直接使用 PyInstaller 命令行（快速）：

   在 PowerShell 中运行下面命令（示例会把 `7z.exe` 嵌入到 exe 同级目录）：

```powershell
pyinstaller --onefile --noconfirm --console \
   --name titizz_extract \
   --add-data "7z.exe;." \
   --exclude-module PyQt5 \
   --exclude-module qt_progress \
   titizz_extract.py
```

   说明：
   - `--console` 会生成带控制台的 exe（非 windowed）。
   - `--exclude-module` 用来避免打包 PyQt5 和本地的 `qt_progress.py`（如果存在）。
   - 如果你的项目需要额外的数据文件或隐藏导入（hidden-import），请按需添加对应的 `--add-data` / `--hidden-import` 参数。

测试与回退：
- 构建完成后，在没有安装 PyQt5 的环境中运行生成的 exe，程序应该会自动使用控制台模式（脚本中已实现对 PyQt5 的 try/except 回退）。
- 如果仍然看到与 Qt 相关的错误，检查是否有其他模块间接引用 PyQt5（使用 `--exclude-module` 排查）。

---

## 贡献与许可

欢迎提交 issue 或 PR。项目用于学习与个人用途，请勿用于商业目的（若需商业许可请联系作者）。

---

构建时间: 2025-09-28
titizz/
├── build_tool.py          # 构建脚本
├── titizz_extract.py      # 主程序源码
├── 7z.exe                 # 7-Zip 命令行工具
├── .venv/                 # 虚拟环境目录
├── dist/                  # 构建输出目录
└── README.md              # 说明文档
```

### 构建步骤
1. **运行构建脚本**
   ```bash
   python build_tool.py
   ```

2. **构建脚本会自动完成以下操作**
   - 🔍 检查并创建虚拟环境（如果不存在）
   - 📦 自动安装 PyInstaller（如果未安装）
   - 📋 验证必要文件存在
   - 🔨 使用 PyInstaller 打包 exe 文件
   - 📝 生成注册表文件
   - 📖 更新使用说明

3. **构建完成后的文件**
   - `dist/titizz_extract.exe` - 可执行文件
   - `add_context_menu.reg` - 添加右键菜单
   - `remove_context_menu.reg` - 移除右键菜单
   - `README.md` - 使用说明（本文件）

### 构建特性
- ✅ **智能环境检测**: 自动检测虚拟环境状态
- ✅ **自动依赖安装**: 缺失 PyInstaller 时自动安装
- ✅ **多镜像源支持**: 自动尝试多个 PyPI 镜像源
- ✅ **错误恢复**: 提供详细的错误信息和解决建议
- ✅ **跨平台兼容**: 支持 Windows/Linux/Mac 开发环境

### 故障排除
如果构建失败，请检查：
1. Python 版本是否为 3.8 或更高
2. 网络连接是否正常
3. 是否有足够的磁盘空间
4. 杀毒软件是否阻止了文件操作

## 📁 文件说明
- `titizz_extract.exe` - 批量解压主程序
- `add_context_menu.reg` - 添加右键菜单的注册表文件
- `remove_context_menu.reg` - 移除右键菜单的注册表文件
- `7z.exe` - 7-Zip 命令行工具（内嵌在 exe 中）

## 🚀 快速开始

### 安装步骤
1. **添加右键菜单**
   - 双击 `add_context_menu.reg` 文件
   - 在弹出的确认对话框中点击"是"
   - 看到"成功添加到注册表"的提示即可

2. **验证安装**
   - 在任意文件夹空白处右键
   - 查看是否出现"批量解压7z文件"选项

### 使用方法
1. **定位到目标文件夹**
   - 进入包含 7z/7zz 压缩文件的文件夹
   - 确保文件夹中有需要解压的压缩包

2. **执行批量解压**
   - 在文件夹空白处右键
   - 选择"批量解压7z文件"
   - 程序会自动开始处理

3. **处理过程**
   - 🔓 自动解压所有 7z 和 7zz 文件（密码: momo.moe）
   - 📁 将所有图片文件收集到 `all_images` 目录
   - 🗑️ 自动清理临时解压文件夹
   - ✅ 显示处理完成信息

### 支持的文件格式
- `.7z` - 7-Zip 压缩文件
- `.7zz` - 7-Zip 压缩文件（新格式）

### 注意事项
- 程序会自动使用密码 `momo.moe` 进行解压
- 解压过程中会创建临时文件夹，完成后会自动删除
- 建议在处理大量文件前备份重要数据

## 🛠️ 高级使用

### 命令行方式
```bash
# 直接在命令行中使用
titizz_extract.exe "C:\目标文件夹路径"

# 或者将 exe 文件拖拽到目标文件夹后执行
```

### 自定义配置
程序目前使用固定密码 `momo.moe`，如需修改请联系开发者或查看源码。

## 🔧 卸载
- 双击 `remove_context_menu.reg` 文件
- 在确认对话框中点击"是"
- 右键菜单中的"批量解压7z文件"选项将被移除

## 📍 安装路径
- 可执行文件: `./dist/titizz_extract.exe`
- 注册表文件: `./add_context_menu.reg` 和 `./remove_context_menu.reg`

## 📋 常见问题

### Q: 右键菜单没有出现怎么办？
A: 
1. 确认已经双击运行了 `add_context_menu.reg`
2. 重启资源管理器：任务管理器 → 结束 `explorer.exe` → 重新运行
3. 检查是否有管理员权限

### Q: 解压失败怎么办？
A:
1. 确认压缩包密码是否为 `momo.moe`
2. 检查压缩包是否损坏
3. 确认有足够的磁盘空间

### Q: 程序运行时出现错误？
A:
1. 确保 Windows 系统版本支持
2. 检查杀毒软件是否拦截
3. 尝试以管理员身份运行

### Q: 如何批量处理多个文件夹？
A: 目前版本需要逐个文件夹处理，未来版本会支持递归处理。

## 🔄 更新日志

### v1.0.0 (2025-09-28)
- ✨ 初始版本发布
- ✅ 支持 7z/7zz 格式批量解压
- ✅ 自动收集图片到 all_images 文件夹
- ✅ 右键菜单集成
- ✅ 自动清理临时文件
- ✅ 智能构建脚本

## 🤝 贡献与反馈

### 问题反馈
如遇到问题或有改进建议，请：
1. 检查本文档的常见问题部分
2. 确保使用最新版本
3. 提供详细的错误信息和复现步骤

### 开发贡献
欢迎提交 Pull Request 或提出改进建议：
- 代码规范：请遵循 PEP 8
- 提交信息：使用清晰的中文描述
- 测试：确保新功能经过充分测试

## 📄 许可证

本项目仅供学习和个人使用，请勿用于商业用途。

---

**构建时间**: 2025年9月28日  
**Python 版本**: 3.8+  
**支持平台**: Windows 10/11
