#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量解压工具构建脚本
自动打包exe并生成注册表文件
"""

import os
import sys
import subprocess
import shutil

def check_virtual_environment():
    """
    检查虚拟环境状态
    返回: (is_in_venv, venv_path, python_path, pip_path, activate_script)
    """
    print("\n🔍 检查虚拟环境...")
    
    # 检查是否在虚拟环境中
    is_in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if is_in_venv:
        venv_path = sys.prefix
        print(f"✅ 当前在虚拟环境中: {venv_path}")
        activate_script = None  # 已经激活，不需要激活脚本
    else:
        # 检查是否存在 .venv 目录
        venv_path = os.path.join(os.getcwd(), ".venv")
        if os.path.exists(venv_path):
            print(f"📁 发现虚拟环境目录: {venv_path}")
            print("⚠️  当前未激活虚拟环境，将自动激活")
            if os.name == 'nt':  # Windows
                activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
            else:  # Linux/Mac
                activate_script = os.path.join(venv_path, "bin", "activate")
        else:
            print("❌ 未找到虚拟环境！")
            print("💡 正在自动创建虚拟环境...")
            try:
                # 自动创建虚拟环境
                subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
                print("✅ 虚拟环境创建成功！")
                venv_path = os.path.join(os.getcwd(), ".venv")
                if os.name == 'nt':  # Windows
                    activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
                else:  # Linux/Mac
                    activate_script = os.path.join(venv_path, "bin", "activate")
            except subprocess.CalledProcessError as e:
                print(f"❌ 创建虚拟环境失败: {e}")
                print("💡 请手动创建虚拟环境:")
                print("   python -m venv .venv")
                print("   .venv\\Scripts\\activate")
                return False, None, None, None, None
    
    # 确定 Python 和 pip 路径
    if os.name == 'nt':  # Windows
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
    else:  # Linux/Mac
        python_path = os.path.join(venv_path, "bin", "python")
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    # 检查 Python 是否存在
    if not os.path.exists(python_path):
        print(f"❌ 未找到 Python 执行文件: {python_path}")
        return False, venv_path, None, None, activate_script
    
    print(f"✅ Python 路径: {python_path}")
    
    # 检查 pip 是否存在
    if not os.path.exists(pip_path):
        print(f"❌ 未找到 pip 执行文件: {pip_path}")
        return False, venv_path, python_path, None, activate_script
    
    print(f"✅ pip 路径: {pip_path}")
    
    return True, venv_path, python_path, pip_path, activate_script

def run_command_in_venv(cmd, activate_script=None, timeout=300):
    """
    在虚拟环境中执行命令
    """
    if os.name == 'nt' and activate_script:  # Windows 需要激活虚拟环境
        # 构建激活虚拟环境并执行命令的批处理命令
        if isinstance(cmd, list):
            cmd_str = ' '.join([f'"{c}"' if ' ' in c else c for c in cmd])
        else:
            cmd_str = cmd
        
        # 使用 & 连接激活命令和目标命令
        full_cmd = f'"{activate_script}" && {cmd_str}'
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', timeout=timeout)
    else:
        # 如果已经在虚拟环境中或Linux系统，直接执行
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=timeout)
    
    return result

def check_pyinstaller(venv_path, pip_path, activate_script=None):
    """
    检查 PyInstaller 是否安装，如果没有则自动安装
    """
    print("\n🔍 检查 PyInstaller...")
    
    if os.name == 'nt':  # Windows
        pyinstaller_path = os.path.join(venv_path, "Scripts", "pyinstaller.exe")
    else:  # Linux/Mac
        pyinstaller_path = os.path.join(venv_path, "bin", "pyinstaller")
    
    if os.path.exists(pyinstaller_path):
        print(f"✅ PyInstaller 已安装: {pyinstaller_path}")
        return pyinstaller_path
    else:
        print("❌ 未找到 PyInstaller")
        print("� 正在自动安装 PyInstaller...")
        
        # 检查 Python 版本兼容性
        try:
            python_cmd = [pip_path.replace("pip.exe", "python.exe"), "--version"]
            result = run_command_in_venv(python_cmd, activate_script)
            if result.returncode == 0:
                print(f"🐍 Python 版本: {result.stdout.strip()}")
        except:
            pass
        
        # 尝试多个镜像源安装 PyInstaller
        mirrors = [
            ("官方源", [pip_path, "install", "pyinstaller"]),
            ("阿里云镜像", [pip_path, "install", "pyinstaller", "-i", "https://mirrors.aliyun.com/pypi/simple/"]),
            ("豆瓣镜像", [pip_path, "install", "pyinstaller", "-i", "https://pypi.douban.com/simple/"]),
            ("清华镜像", [pip_path, "install", "pyinstaller", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]),
            ("中科大镜像", [pip_path, "install", "pyinstaller", "-i", "https://pypi.mirrors.ustc.edu.cn/simple/"])
        ]
        
        for mirror_name, cmd in mirrors:
            try:
                print(f"📡 尝试使用 {mirror_name} 安装 PyInstaller...")
                print(f"执行命令: {' '.join(cmd)}")
                print("⏳ 正在下载并安装，请稍等...")
                
                result = run_command_in_venv(cmd, activate_script, timeout=300)
                
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
                # 显示安装输出的最后几行
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    print("安装输出:")
                    for line in lines[-3:]:  # 显示最后3行
                        if line.strip():
                            print(f"  {line}")
                
                print(f"✅ 使用 {mirror_name} 安装 PyInstaller 成功！")
                
                # 再次检查是否安装成功
                if os.path.exists(pyinstaller_path):
                    print(f"✅ PyInstaller 路径: {pyinstaller_path}")
                    return pyinstaller_path
                else:
                    print("❌ PyInstaller 安装后仍未找到执行文件")
                    print(f"预期路径: {pyinstaller_path}")
                    continue
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ {mirror_name} 安装超时，尝试下一个镜像源...")
                continue
            except subprocess.CalledProcessError as e:
                print(f"❌ {mirror_name} 安装失败 (退出码: {e.returncode})")
                if "No matching distribution found" in str(e.stderr):
                    print("  原因: 找不到匹配的 PyInstaller 版本")
                elif "Could not find a version that satisfies" in str(e.stderr):
                    print("  原因: Python 版本可能不兼容")
                print(f"  尝试下一个镜像源...")
                continue
        
        # 所有镜像源都失败了
        print("\n❌ 所有镜像源安装 PyInstaller 都失败了")
        print("\n� 可能的解决方案:")
        print("1. 检查网络连接是否正常")
        print("2. 检查 Python 版本是否兼容 (建议 Python 3.8+)")
        print("3. 尝试升级 pip: python -m pip install --upgrade pip")
        print("4. 手动安装: pip install pyinstaller")
        print("5. 如果是公司网络，可能需要配置代理")
        return None

def download_7zip():
    """
    自动下载 7z.exe
    """
    print("📦 正在下载 7-Zip 命令行工具...")
    
    try:
        import urllib.request
        import urllib.error
        
        # 进度回调函数
        def show_progress(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\r⏳ 下载进度: {percent}%", end="", flush=True)
        
        # 多个下载源
        download_sources = [
            {
                "name": "7-Zip 官网",
                "url": "https://www.7-zip.org/a/7zr.exe",
                "filename": "7z.exe",
                "min_size": 400000  # 至少400KB
            },
            {
                "name": "GitHub 镜像",
                "url": "https://github.com/mcmilk/7-Zip/releases/download/23.01/7z2301-extra.7z",
                "filename": "7z_extra.7z",
                "min_size": 1000000,  # 至少1MB
                "extract": True
            }
        ]
        
        for source in download_sources:
            try:
                print(f"📡 尝试从 {source['name']} 下载...")
                
                # 下载文件
                urllib.request.urlretrieve(
                    source['url'], 
                    source['filename'], 
                    reporthook=show_progress
                )
                print()  # 换行
                
                # 验证文件大小
                if not os.path.exists(source['filename']):
                    raise Exception(f"下载的文件不存在: {source['filename']}")
                
                file_size = os.path.getsize(source['filename'])
                if file_size < source['min_size']:
                    raise Exception(f"文件大小异常: {file_size} bytes")
                
                # 如果需要解压
                if source.get('extract'):
                    print("📂 正在解压文件...")
                    try:
                        # 这里需要已经有7z.exe才能解压，所以跳过这个方案
                        os.remove(source['filename'])
                        continue
                    except Exception as e:
                        print(f"解压失败: {e}")
                        os.remove(source['filename']) if os.path.exists(source['filename']) else None
                        continue
                else:
                    # 直接重命名为 7z.exe
                    if source['filename'] != "7z.exe":
                        if os.path.exists("7z.exe"):
                            os.remove("7z.exe")
                        os.rename(source['filename'], "7z.exe")
                
                print("✅ 7z.exe 下载成功！")
                return True
                
            except urllib.error.URLError as e:
                print(f"\n⚠️ {source['name']} 网络错误: {e}")
                # 清理部分下载的文件
                if os.path.exists(source['filename']):
                    os.remove(source['filename'])
                continue
            except Exception as e:
                print(f"\n⚠️ {source['name']} 下载失败: {e}")
                # 清理部分下载的文件
                if os.path.exists(source['filename']):
                    os.remove(source['filename'])
                continue
        
        # 所有下载源都失败，提示手动下载
        print("\n❌ 所有自动下载尝试都失败了")
        print("\n💡 请手动下载 7z.exe:")
        print("1. 访问 https://www.7-zip.org/download.html")
        print("2. 下载 '7-Zip Extra: standalone console version'")
        print("3. 解压后将 7z.exe 复制到当前目录")
        print("4. 或者搜索下载任意 7z.exe 文件到当前目录")
        
        # 询问是否等待用户手动下载
        while True:
            choice = input("\n是否已完成手动下载？(y/n/skip): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                if os.path.exists("7z.exe") and os.path.getsize("7z.exe") > 50000:
                    print("✅ 检测到 7z.exe 文件！")
                    return True
                else:
                    print("❌ 未检测到有效的 7z.exe 文件，请重新下载")
                    continue
            elif choice in ['n', 'no', '否']:
                print("⏳ 请下载完成后重新运行构建脚本")
                return False
            elif choice in ['skip', '跳过']:
                print("⚠️ 跳过 7z.exe 下载，构建可能会失败")
                return False
            else:
                print("请输入 y(是) 或 n(否) 或 skip(跳过)")
        
    except ImportError:
        print("❌ urllib 模块不可用")
        print("💡 请手动下载 7z.exe 到当前目录")
        return False
    except Exception as e:
        print(f"❌ 下载过程发生错误: {e}")
        print("💡 请手动下载 7z.exe 到当前目录")
        return False

def check_7zip_file():
    """
    检查 7z.exe 文件是否存在，如果不存在则尝试下载
    """
    print("📋 检查 7z.exe 文件...")
    
    if os.path.exists("7z.exe"):
        # 检查文件大小，确保不是空文件
        file_size = os.path.getsize("7z.exe")
        if file_size > 50000:  # 大于50KB
            print("✅ 找到 7z.exe")
            return True
        else:
            print("⚠️ 7z.exe 文件似乎损坏或不完整")
            os.remove("7z.exe")
    
    print("❌ 未找到 7z.exe 文件")
    print("🔄 正在尝试自动下载...")
    
    if download_7zip():
        return True
    else:
        print("❌ 自动下载失败，请手动下载 7z.exe")
        return False

def create_ti_icon():
    """
    创建一个带有 Ti 字母的粉色图标
    """
    icon_path = "titizz_icon.ico"
    
    # 检查是否已经存在合适的图标文件
    if os.path.exists(icon_path) and os.path.getsize(icon_path) > 300:
        file_size = os.path.getsize(icon_path)
        print(f"✅ 使用已有图标: {icon_path} ({file_size} bytes)")
        return icon_path
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        print("🎨 正在创建 Ti 图标...")
        
        # 创建多个尺寸的图标 (16x16, 32x32, 48x48, 64x64)
        sizes = [16, 32, 48, 64]
        images = []
        
        for size in sizes:
            # B站粉色 #FB7299
            bilibili_pink = (251, 114, 153, 255)
            white = (255, 255, 255, 255)
            
            # 创建图像
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 绘制圆形背景
            margin = max(1, size // 16)
            draw.ellipse([margin, margin, size-margin, size-margin], fill=bilibili_pink)
            
            # 根据图标大小调整字体
            font_size = max(8, size // 2)
            
            # 尝试使用系统字体绘制 Ti
            try:
                # 尝试几种常见字体
                font_names = ['arial.ttf', 'calibri.ttf', 'segoeui.ttf', 'tahoma.ttf']
                font = None
                
                for font_name in font_names:
                    try:
                        font_path = f"C:/Windows/Fonts/{font_name}"
                        if os.path.exists(font_path):
                            font = ImageFont.truetype(font_path, font_size)
                            break
                    except:
                        continue
                
                if font is None:
                    # 如果找不到TrueType字体，使用默认字体
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # 绘制文字 "Ti"
            text = "Ti"
            
            # 获取文字尺寸并居中
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                # 兼容旧版本PIL
                text_width, text_height = draw.textsize(text, font=font)
            
            # 计算居中位置
            x = (size - text_width) // 2
            y = (size - text_height) // 2 - 1  # 稍微向上偏移
            
            # 绘制文字
            draw.text((x, y), text, font=font, fill=white)
            
            images.append(img)
        
        # 保存为 ICO 文件，包含多个尺寸
        images[0].save(
            icon_path, 
            format='ICO', 
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )
        
        # 检查文件是否成功创建且大小合理（降低要求到300字节）
        if os.path.exists(icon_path) and os.path.getsize(icon_path) > 300:
            print(f"✅ 图标创建成功: {icon_path} ({os.path.getsize(icon_path)} bytes)")
            return icon_path
        else:
            print("❌ 图标文件创建失败或文件过小")
            return None
        
    except ImportError:
        print("⚠️ 未安装 Pillow 库，创建简单的ICO文件...")
        return create_simple_icon()
    except Exception as e:
        print(f"⚠️ 创建图标失败: {e}，尝试创建简单图标...")
        return create_simple_icon()

def create_simple_icon():
    """创建一个简单的ICO文件"""
    try:
        # 创建一个简单的16x16像素ICO文件头
        icon_data = bytearray([
            # ICO header
            0x00, 0x00,  # Reserved
            0x01, 0x00,  # Type (1 = ICO)
            0x01, 0x00,  # Number of images
            
            # Image entry
            0x10,  # Width (16)
            0x10,  # Height (16)
            0x00,  # Color palette (0 = no palette)
            0x00,  # Reserved
            0x01, 0x00,  # Color planes
            0x20, 0x00,  # Bits per pixel (32)
            0x00, 0x04, 0x00, 0x00,  # Image data size (1024 bytes)
            0x16, 0x00, 0x00, 0x00,  # Image data offset (22 bytes)
        ])
        
        # 添加位图头
        bitmap_header = bytearray([
            0x28, 0x00, 0x00, 0x00,  # Header size (40)
            0x10, 0x00, 0x00, 0x00,  # Width (16)
            0x20, 0x00, 0x00, 0x00,  # Height (32, doubled for ICO)
            0x01, 0x00,              # Planes (1)
            0x20, 0x00,              # Bits per pixel (32)
            0x00, 0x00, 0x00, 0x00,  # Compression (0 = none)
            0x00, 0x04, 0x00, 0x00,  # Image size (1024)
            0x00, 0x00, 0x00, 0x00,  # X pixels per meter
            0x00, 0x00, 0x00, 0x00,  # Y pixels per meter
            0x00, 0x00, 0x00, 0x00,  # Colors used
            0x00, 0x00, 0x00, 0x00,  # Important colors
        ])
        
        # 创建16x16粉色图标像素数据 (BGRA格式)
        pink = [0x99, 0x72, 0xFB, 0xFF]  # B站粉色 #FB7299
        transparent = [0x00, 0x00, 0x00, 0x00]
        
        pixels = []
        # ICO格式图像数据是从下到上存储的
        for y in range(15, -1, -1):  # 从下往上
            for x in range(16):
                # 创建一个圆形图标
                center_x, center_y = 7.5, 7.5
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if distance <= 7:
                    pixels.extend(pink)
                else:
                    pixels.extend(transparent)
        
        # 添加AND掩码 (全透明)
        and_mask = [0x00] * 32  # 16*16/8 = 32 bytes
        
        # 组合完整的ICO数据
        icon_data.extend(bitmap_header)
        icon_data.extend(pixels)
        icon_data.extend(and_mask)
        
        # 写入文件
        icon_path = "titizz_icon.ico"
        with open(icon_path, 'wb') as f:
            f.write(icon_data)
        
        if os.path.exists(icon_path) and os.path.getsize(icon_path) > 200:
            print(f"✅ 简单图标创建成功: {icon_path} ({os.path.getsize(icon_path)} bytes)")
            return icon_path
        else:
            print("❌ 简单图标创建失败")
            return None
            
    except Exception as e:
        print(f"❌ 创建简单图标失败: {e}")
        return None

def main():
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=== 批量解压工具构建脚本 ===")
    print(f"当前目录: {script_dir}")
    
    # 1. 检查虚拟环境
    venv_ok, venv_path, python_path, pip_path, activate_script = check_virtual_environment()
    if not venv_ok:
        return False
    
    # 2. 检查并安装必要的包
    print("\n📦 检查必要的 Python 包...")
    
    # 检查并安装 Pillow（用于创建图标）
    try:
        import PIL
        print("✅ Pillow 已安装")
    except ImportError:
        print("📦 正在安装 Pillow...")
        try:
            cmd = [pip_path, "install", "Pillow"]
            result = run_command_in_venv(cmd, activate_script, timeout=300)
            if result.returncode == 0:
                print("✅ Pillow 安装成功")
            else:
                print("⚠️ Pillow 安装失败，将使用 exe 文件作为图标")
        except Exception as e:
            print(f"⚠️ Pillow 安装失败: {e}，将使用 exe 文件作为图标")
    
    # 3. 检查并安装 PyInstaller
    pyinstaller_path = check_pyinstaller(venv_path, pip_path, activate_script)
    if not pyinstaller_path:
        return False
    
    # 4. 检查必要文件
    print("\n📋 检查必要文件...")
    
    # 检查主程序源码
    if not os.path.exists("titizz_extract.py"):
        print("❌ 未找到 titizz_extract.py 文件！")
        return False
    else:
        print("✅ 找到 titizz_extract.py")
    
    # 检查并下载 7z.exe
    if not check_7zip_file():
        return False
    
    # 5. 打包exe
    print("\n🔨 开始打包 exe 文件...")
    
    # 清理之前的构建
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    cmd = [
        pyinstaller_path,
        "--clean",  # 清理缓存
        "titizz_extract.spec"  # 使用 spec 文件构建
    ]
    
    try:
        print(f"执行命令: {' '.join(cmd)}")
        result = run_command_in_venv(cmd, activate_script, timeout=600)  # 10分钟超时
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        print("✅ exe 文件打包成功！")
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        return False
    
    # 6. 创建图标文件
    print("\n🎨 创建图标文件...")
    icon_path = create_ti_icon()
    
    # 确保图标文件存在用于exe打包
    if not icon_path or not os.path.exists(icon_path):
        print("⚠️ 图标创建失败，exe将使用默认图标")
    else:
        print(f"✅ 图标文件准备完成，将应用到exe文件")
    
    # 7. 生成注册表文件
    exe_path = os.path.join(script_dir, "dist", "titizz_extract.exe")
    exe_path_escaped = exe_path.replace("\\", "\\\\")
    
    # 决定使用哪个图标
    if icon_path and os.path.exists(icon_path):
        icon_full_path = os.path.join(script_dir, icon_path)
        icon_path_escaped = icon_full_path.replace("\\", "\\\\")
        print(f"✅ 将使用自定义图标: {icon_path}")
    else:
        icon_path_escaped = exe_path_escaped
        print("✅ 将使用 exe 文件图标")
    
    print("\n📝 生成注册表文件...")
    
    # 添加右键菜单的注册表内容
    add_reg_content = f'''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\TitizzExtract]
@="titizz一键提取"
"Icon"="{icon_path_escaped}"

[HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\TitizzExtract\\command]
@="\\"{exe_path_escaped}\\" \\"%V\\""
'''
    
    # 移除右键菜单的注册表内容
    remove_reg_content = '''Windows Registry Editor Version 5.00

[-HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\TitizzExtract]
'''
    
    # 写入注册表文件
    with open("add_context_menu.reg", "w", encoding="utf-8") as f:
        f.write(add_reg_content)
    
    with open("remove_context_menu.reg", "w", encoding="utf-8") as f:
        f.write(remove_reg_content)
    
    print("✅ 注册表文件生成成功！")
    
    print(f"\n🎉 构建完成！")
    print(f"📁 exe 文件位置: {exe_path}")
    print(f"📄 注册表文件: add_context_menu.reg / remove_context_menu.reg")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ 构建成功！可以开始使用了。")
    else:
        print("\n❌ 构建失败，请检查错误信息。")
    
    # 更可靠的"按任意键退出"实现
    try:
        if os.name == 'nt':  # Windows
            print("\n按任意键退出...")
            import msvcrt
            msvcrt.getch()
        else:  # Linux/Mac
            input("\n按任意键退出...")
    except ImportError:
        # 如果 msvcrt 不可用，使用传统方式
        try:
            input("\n按任意键退出...")
        except (KeyboardInterrupt, EOFError):
            pass
    except (KeyboardInterrupt, EOFError):
        pass
    except Exception:
        # 如果所有方法都失败，至少暂停一下
        import time
        print("\n程序将在 3 秒后退出...")
        time.sleep(3)