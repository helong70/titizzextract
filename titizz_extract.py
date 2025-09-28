# 批量解压 7z 和 7zz 文件脚本
# 使用方法：在虚拟环境中运行此脚本
import os
import subprocess
import sys

def extract_7z_with_7zexe(file_path, out_dir, password=None):
    # 7z.exe 路径，支持打包后的相对路径
    import sys
    if getattr(sys, 'frozen', False):
        # 打包后的exe环境
        seven_zip = os.path.join(sys._MEIPASS, '7z.exe')
    else:
        # 开发环境
        seven_zip = os.path.join(os.path.dirname(__file__), '7z.exe')
    cmd = [seven_zip, 'x', file_path, f'-o{out_dir}']
    if password:
        cmd.append(f'-p{password}')
    # 覆盖同名文件
    cmd.append('-y')
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        if result.returncode == 0:
            return True
        else:
            error_msg = f"解压失败: {os.path.basename(file_path)}, 错误: {result.stderr}"
            print(error_msg)
            return False
    except Exception as e:
        error_msg = f"解压异常: {os.path.basename(file_path)}, 错误: {e}"
        print(error_msg)
        return False



def force_remove_directory(path):
    """强制删除目录，包括只读文件"""
    import shutil
    import stat
    
    def remove_readonly(func, path, exc):
        """删除只读文件的错误处理函数"""
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)
            func(path)
    
    shutil.rmtree(path, onerror=remove_readonly)







def print_banner():
    """打印漂亮的横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎯 Titizz 批量解压工具                      ║
║                      v1.0.0 - 2025.9.28                     ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_progress_bar(current, total, length=50):
    """打印进度条"""
    if total == 0:
        return ""
    
    progress = current / total
    filled = int(length * progress)
    bar = "█" * filled + "░" * (length - filled)
    percentage = progress * 100
    
    return f"[{bar}] {current}/{total} ({percentage:.1f}%)"

def run_with_console_progress():
    """使用控制台进度条模式运行"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.getcwd()
    
    password = "momo.moe"
    
    # 清屏并显示横幅
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    print(f"📁 目标目录: {root_dir}")
    print(f"🔑 解压密码: {password}")
    print("═" * 65)
    
    # 设置全局变量为None，使用控制台输出
    global progress_window
    progress_window = None
    
    batch_extract_console(root_dir, password)
    
    print("\n" + "=" * 60)
    print("✨ 处理完成！")
    print("=" * 60)
    
    # 退出处理
    try:
        if os.name == 'nt':  # Windows
            print("\n按任意键退出...")
            import msvcrt
            msvcrt.getch()
        else:  # Linux/Mac
            input("\n按任意键退出...")
    except ImportError:
        try:
            input("\n按任意键退出...")
        except (KeyboardInterrupt, EOFError):
            pass
    except (KeyboardInterrupt, EOFError):
        pass
    except Exception:
        import time
        print("\n程序将在 3 秒后退出...")
        time.sleep(3)

def batch_extract_console(root_dir, password):
    """控制台模式的批量解压函数"""
    # 统计需要处理的文件
    files_to_process = []
    for foldername, subfolders, filenames in os.walk(root_dir):
        if '.venv' in foldername or 'all_images' in foldername:
            continue
            
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            name, ext = os.path.splitext(filename)
            if ext == '' and filename.startswith('NO') and foldername == root_dir:
                files_to_process.append((file_path, filename))
    
    total_files = len(files_to_process)
    print(f"\n📋 发现 {total_files} 个需要处理的文件")
    
    if total_files == 0:
        print("❌ 未找到符合条件的文件（根目录下以NO开头的无扩展名文件）")
        return
    
    # 只有在有文件需要处理时才创建 all_images 目录
    all_images_dir = os.path.join(root_dir, 'all_images')
    if not os.path.exists(all_images_dir):
        os.makedirs(all_images_dir)
        print(f"📁 创建图片收集目录: {all_images_dir}")
    
    to_delete = []
    processed = 0
    
    for file_path, filename in files_to_process:
        processed += 1
        
        # 显示进度条和当前文件
        progress_bar = print_progress_bar(processed, total_files)
        print(f"\n{progress_bar}")
        print(f"🔄 正在处理: {filename}")
        
        out_dir = file_path + '_extracted'
        
        if extract_7z_with_7zexe(file_path, out_dir, password):
            print(f"  ✅ 解压成功: {filename}")
            
            # 处理子文件
            try:
                for subfile in os.listdir(out_dir):
                    subfile_path = os.path.join(out_dir, subfile)
                    sub_name, sub_ext = os.path.splitext(subfile)
                    if sub_ext == '.7zz' or sub_ext == '' or subfile.lower().endswith('.7zz'):
                        sub_out_dir = subfile_path + '_extracted'
                        print(f"  🔄 二次解压: {subfile}")
                        
                        if extract_7z_with_7zexe(subfile_path, sub_out_dir, password):
                            print(f"    ✅ 二次解压成功")
                            move_images_console(sub_out_dir, all_images_dir)
                            to_delete.append(sub_out_dir)
                        
                move_images_console(out_dir, all_images_dir)
                to_delete.append(out_dir)
            except Exception as e:
                print(f"  ⚠️ 处理子文件时出错: {e}")
    
    # 清理临时文件夹
    # 清理阶段
    print(f"\n🗑️ 开始清理 {len(to_delete)} 个临时文件夹...")
    cleaned = 0
    for i, d in enumerate(to_delete, 1):
        try:
            # 显示清理进度
            clean_progress = print_progress_bar(i, len(to_delete), 30)
            print(f"\r{clean_progress} 清理中...", end="", flush=True)
            
            force_remove_directory(d)
            cleaned += 1
        except Exception as e:
            print(f"\n  ❌ 清理失败: {os.path.basename(d)}, 错误: {e}")
    
    print(f"\n\n{'='*65}")
    print("🎉 处理完成！")
    print("═" * 65)
    print(f"📊 统计信息:")
    print(f"  ├─ 📁 处理文件: {processed} 个")
    print(f"  ├─ 🗑️ 清理文件夹: {cleaned} 个") 
    print(f"  └─ 📂 图片目录: {os.path.basename(all_images_dir)}")
    print("═" * 65)

def move_images_console(src_dir, dest_dir):
    """控制台模式的图片移动函数"""
    import shutil
    
    moved_count = 0
    for item in os.listdir(src_dir):
        item_path = os.path.join(src_dir, item)
        if os.path.isdir(item_path):
            # 检查文件夹是否包含图片
            imgs = [f for f in os.listdir(item_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
            if imgs:
                new_folder = os.path.join(dest_dir, os.path.basename(item_path))
                if not os.path.exists(new_folder):
                    shutil.move(item_path, new_folder)
                    moved_count += 1
                    print(f"    📁 收集文件夹: {os.path.basename(item_path)} ({len(imgs)} 张图片)")
        elif item.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            try:
                shutil.move(item_path, os.path.join(dest_dir, item))
                moved_count += 1
                print(f"    🖼️ 收集图片: {item}")
            except Exception as e:
                print(f"    ⚠️ 移动失败: {item}, 错误: {e}")

if __name__ == "__main__":
    run_with_console_progress()
