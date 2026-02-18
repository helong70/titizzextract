# 批量解压 7z 和 7zz 文件脚本
# 使用方法：在虚拟环境中运行此脚本
import os
import subprocess
import sys

# 可选的 Qt 进度条支持（如果安装了 PyQt5）
try:
    from qt_progress import QtProgressApp
    QT_AVAILABLE = True
except Exception:
    QtProgressApp = None
    QT_AVAILABLE = False

def extract_7z_with_7zexe(file_path, out_dir, password=None):
    # 7z.exe 路径，支持打包后的相对路径
    import sys
    # 计算基目录：优先使用 _MEIPASS（PyInstaller），其次使用模块 __file__，最后回退到当前工作目录
    if getattr(sys, 'frozen', False):
        seven_zip = os.path.join(sys._MEIPASS, '7z.exe')
    else:
        try:
            module_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            module_dir = os.getcwd()
        seven_zip = os.path.join(module_dir, '7z.exe')
    cmd = [seven_zip, 'x', file_path, f'-o{out_dir}']
    if password:
        cmd.append(f'-p{password}')
    # 覆盖同名文件
    cmd.append('-y')
    try:
        # 在 Windows 上运行外部 7z.exe 时避免弹出额外的控制台窗口
        if os.name == 'nt':
            # 使用 CREATE_NO_WINDOW 避免创建新的控制台
            creationflags = subprocess.CREATE_NO_WINDOW
            # 也可以设置 STARTUPINFO 以隐藏窗口
            try:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = subprocess.SW_HIDE
            except Exception:
                si = None
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', creationflags=creationflags, startupinfo=si)
        else:
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
║                    🎯 Titizz 批量解压工具                     ║
║                      v1.0.0 - 2025.9.28                      ║
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
    # 默认启用 GUI（如果安装了 PyQt5），除非显式传入 --console
    use_gui = ('--console' not in sys.argv)

    # 解析目标目录（第一个非选项参数）
    root_dir = None
    for a in sys.argv[1:]:
        if a.startswith('-'):
            continue
        root_dir = a
        break
    if not root_dir:
        root_dir = os.getcwd()
    
    password = "momo.moe"
    
    # 在控制台模式下清屏并显示横幅；GUI 模式不清屏以避免创建临时控制台窗口
    if not use_gui:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception:
            pass
        print_banner()
        print(f"📁 目标目录: {root_dir}")
        print(f"🔑 解压密码: {password}")
        print("═" * 65)
    
    # 设置全局变量为None（可能会被 batch_extract_console 覆盖为 QtProgressApp 实例）
    global progress_window
    progress_window = None
    
    # 如果要求 GUI 并且可用：在主线程运行 Qt 事件循环，处理放后台线程
    if use_gui and QT_AVAILABLE:
        from threading import Thread
        import time

        # 共享状态，以线程安全的方式在 worker 和主线程之间通信
        global progress_state
        progress_state = {'value': 0, 'total': 1, 'text': '', 'done': False}

        import importlib, time
        # 预热 PyQt 子模块，尽量把导入开销放到现在（在创建 QApplication 之前）
        try:
            importlib.import_module('PyQt5.QtCore')
            importlib.import_module('PyQt5.QtGui')
            importlib.import_module('PyQt5.QtWidgets')
        except Exception:
            pass

        # 预先创建 QApplication（和一个最小窗口）以缩短后续显示延迟，并记录耗时
        t0 = time.time()
        # create_app=True 会创建 QApplication 和窗口；我们先创建一个最小的窗口
        qt_app = QtProgressApp(total=1, create_app=True, compact=True, auto_close=False)
        t1 = time.time()
        print(f"⏱️ Qt init time: {(t1-t0)*1000:.0f} ms")

        # 启动后台工作线程，传入 None 为 qt_app（worker 不直接操作 GUI）
        worker = Thread(target=batch_extract_console, args=(root_dir, password, True, None), daemon=True)
        worker.start()

        # 主线程轮询共享状态并更新 GUI（主线程安全）
        try:
            # 等待 worker 初始化 total
            import importlib
            # 等待 worker 初始化 total
            while not progress_state.get('total', 1):
                QtWidgets = importlib.import_module('PyQt5.QtWidgets')
                QtWidgets.QApplication.processEvents()
                time.sleep(0.01)

            total = max(1, progress_state.get('total', 1))
            # 更新进度条范围并启用 auto_close（完成时自动关闭并退出事件循环）
            try:
                qt_app.win.bar.setRange(0, total)
                qt_app.total = total
                qt_app.auto_close = True
            except Exception:
                pass
            qt_app.start()
            last_total = qt_app.total

            while worker.is_alive():
                val = progress_state.get('value', 0)
                txt = progress_state.get('text', '')
                try:
                    qt_app.set_value(val, txt)
                except Exception:
                    pass
                # 动态检测 total 变化（例如清理阶段把额外项加入 total），并更新进度条范围
                try:
                    current_total = progress_state.get('total', last_total)
                    if current_total != last_total:
                        qt_app.win.bar.setRange(0, max(1, current_total))
                        qt_app.total = current_total
                        last_total = current_total
                except Exception:
                    pass
                import importlib
                QtWidgets = importlib.import_module('PyQt5.QtWidgets')
                QtWidgets.QApplication.processEvents()
                time.sleep(0.05)

            # 最终刷新一次，确保进度达到 total 以触发 auto_close
            try:
                qt_app.set_value(progress_state.get('value', 0), progress_state.get('text', ''))
                # 确保到达 total
                qt_app.set_value(total, f"{total}/{total} 完成")
            except Exception:
                pass

        finally:
            # 关闭窗口并退出应用（如果还在运行）
            try:
                if qt_app:
                    try:
                        qt_app.close()
                    except Exception:
                        pass
                app = __import__('PyQt5.QtWidgets').QApplication.instance()
                if app:
                    try:
                        app.quit()
                    except Exception:
                        pass
            except Exception:
                pass
        # 等待 worker 结束（已经结束时瞬间返回）
        worker.join()
    else:
        batch_extract_console(root_dir, password, use_gui=use_gui)
    
    print("\n" + "=" * 60)
    print("✨ 处理完成！")
    print("=" * 60)
    
    # 仅在控制台模式下等待用户按键，GUI 模式直接退出避免弹出临时控制台窗口
    if not use_gui:
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

def batch_extract_console(root_dir, password, use_gui=False, qt_app=None):
    """控制台模式的批量解压函数"""
    # 统计需要处理的文件（仅根目录，不遍历子目录）
    files_to_process = []
    root_dir_abs = os.path.abspath(root_dir)
    try:
        for filename in os.listdir(root_dir_abs):
            file_path = os.path.join(root_dir_abs, filename)
            # 仅处理根目录下的普通文件
            if not os.path.isfile(file_path):
                continue
            # 跳过不应处理的目录或其内容（防护）
            if '.venv' in file_path or 'all_images' in file_path:
                continue
            name, ext = os.path.splitext(filename)
            if ext == '' and filename.startswith('NO'):
                files_to_process.append((file_path, filename))
    except FileNotFoundError:
        print(f"❌ 目录不存在: {root_dir}")
        return
    
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
    # 收集所有移动日志，避免被清屏覆盖
    move_logs = []

    # 启动 Qt 进度窗口（如果请求并且可用）
    created_qt_app = False
    global progress_state
    if use_gui:
        # 初始化进度状态，主线程会轮询它以显示 GUI
        progress_state = {'value': 0, 'total': max(1, total_files), 'text': '', 'done': False}
        if not QT_AVAILABLE:
            print("⚠️ 未安装或无法使用 PyQt5，回退到控制台进度")
    
    import concurrent.futures
    import threading
    import time
    import sys as _sys
    cpu_count = os.cpu_count() or 4
    task_states = []  # [{id, filename, status, progress, total, msg}]
    state_lock = threading.Lock()

    # 初始化任务状态
    for idx, (file_path, filename) in enumerate(files_to_process):
        task_states.append({'id': idx, 'filename': filename, 'status': '等待', 'progress': 0, 'total': 1, 'msg': ''})

    def extract_task(args):
        idx, (file_path, filename) = args
        out_dir = file_path + '_extracted'
        # 更新状态为进行中
        with state_lock:
            task_states[idx]['status'] = '解压中'
            task_states[idx]['progress'] = 0
            task_states[idx]['total'] = 1
            task_states[idx]['msg'] = ''
        # 实际解压
        result = extract_7z_with_7zexe(file_path, out_dir, password)
        # 处理子文件
        sub_count = 0
        sub_done = 0
        if result:
            try:
                subfiles = [subfile for subfile in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, subfile)) or os.path.isdir(os.path.join(out_dir, subfile))]
                sub_count = len(subfiles)
                for subfile in subfiles:
                    subfile_path = os.path.join(out_dir, subfile)
                    sub_name, sub_ext = os.path.splitext(subfile)
                    if sub_ext == '.7zz' or sub_ext == '' or subfile.lower().endswith('.7zz'):
                        sub_out_dir = subfile_path + '_extracted'
                        with state_lock:
                            task_states[idx]['status'] = '二次解压'
                            task_states[idx]['total'] = sub_count
                            task_states[idx]['progress'] = sub_done
                            task_states[idx]['msg'] = f"{subfile}"
                        # 只有二次解压成功才移动
                        if extract_7z_with_7zexe(subfile_path, sub_out_dir, password):
                            logs = move_images_console(sub_out_dir, all_images_dir, collect_logs=True)
                            if logs:
                                with state_lock:
                                    move_logs.extend(logs)
                        else:
                            with state_lock:
                                move_logs.append(f"    ⚠️ 二次解压失败，未移动: {sub_out_dir}")
                        sub_done += 1
                        with state_lock:
                            task_states[idx]['progress'] = sub_done
                # 仅移动二次解压生成的目录，第一次解压的产物直接清理
                # 清理 out_dir
                force_remove_directory(out_dir)
                with state_lock:
                    task_states[idx]['status'] = '完成'
                    task_states[idx]['progress'] = sub_count
                    task_states[idx]['msg'] = '全部完成'
            except Exception as e:
                with state_lock:
                    task_states[idx]['status'] = '错误'
                    task_states[idx]['msg'] = f"处理子文件时出错: {e}"
        else:
            with state_lock:
                task_states[idx]['status'] = '失败'
                task_states[idx]['msg'] = '解压失败'
        return result

    def render_all_progress():
        with state_lock:
            lines = []
            for t in task_states:
                bar = print_progress_bar(t['progress'], t['total'], 30)
                # 每行末尾加\033[K，清除行尾残留
                lines.append(f"{t['filename'][:30]:<30} {bar} [{t['status']}] {t['msg']}\033[K")
            return lines

    # 启动线程池
    with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count) as executor:
        futures = [executor.submit(extract_task, (idx, files_to_process[idx])) for idx in range(len(files_to_process))]
        # 主线程定时刷新进度
        progress_lines = len(task_states)  # 进度条行数（不含标题）
        is_windows = os.name == 'nt'
        # 首次输出标题和进度条
        print("批量解压进度：")
        for l in render_all_progress():
            print(l)
        _sys.stdout.flush()
        while True:
            all_done = all(f.done() for f in futures)
            lines = render_all_progress()
            if is_windows:
                # Windows 终端降级：每次清屏重绘
                os.system('cls')
                print("批量解压进度：")
                for l in lines:
                    print(l)
            else:
                # 尝试用ANSI上移光标
                print(f"\033[{progress_lines}F", end="")
                for l in lines:
                    print(l)
            _sys.stdout.flush()
            if all_done:
                break
            time.sleep(0.2)
    # 进度条结束后统一打印所有移动日志
    if move_logs:
        print("\n图片/文件收集日志：")
        for log in move_logs:
            print(log)
    
    # 清理阶段已由各线程自行完成
    print(f"\n\n{'='*65}")
    print("🎉 处理完成！")
    print("═" * 65)
    # 多线程统计
    total = len(task_states)
    finished = sum(1 for t in task_states if t['status'] == '完成')
    failed = sum(1 for t in task_states if t['status'] == '失败' or t['status'] == '错误')
    print(f"📊 统计信息:")
    print(f"  ├─ 📁 处理文件: {total} 个")
    print(f"  ├─ ✅ 成功: {finished} 个")
    print(f"  ├─ ❌ 失败: {failed} 个")
    print(f"  └─ 📂 图片目录: {os.path.basename(all_images_dir)}")
    print("═" * 65)


    # 处理完成后，如果我们在此函数内创建了 qt_app，退出事件循环
    if use_gui and QT_AVAILABLE and created_qt_app and qt_app:
        try:
            # 关闭窗口并退出 Qt loop
            qt_app.win.close()
            # 如果 QApplication 有 exec_ 在运行，退出
            try:
                QtWidgets = __import__('PyQt5.QtWidgets')
                app = QtWidgets.QApplication.instance()
                if app:
                    app.quit()
            except Exception:
                pass
        except Exception:
            pass

def move_images_console(src_dir, dest_dir, collect_logs=False):
    """控制台模式的图片移动函数：不再仅在包含图片时移动文件夹，而是把 src_dir 下的所有内容都转移到 dest_dir。
    collect_logs: True 时返回日志列表，False 时直接打印。"""
    import shutil

    moved_count = 0
    logs = []
    # 确保目标目录存在
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 遍历 src_dir 的直接子项，决定是否移动
    for item in os.listdir(src_dir):
        item_path = os.path.join(src_dir, item)
        # 目录：无论是否包含图片都要移动（如果目标已存在则合并）
        if os.path.isdir(item_path):
            # 先检查该目录下是否包含任何文件（递归），如果完全没有文件则跳过移动
            contains_file = False
            image_count = 0
            for root, dirs, files in os.walk(item_path):
                if files:
                    contains_file = True
                    for f in files:
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                            image_count += 1
                # 如果已经发现文件且图片数也大于0，可提前结束遍历
                if contains_file and image_count > 0:
                    break

            # 如果目录内部完全没有文件（只是嵌套空文件夹），则跳过移动
            if not contains_file:
                # 尝试删除空目录（如果为空且可删除），并跳过
                try:
                    os.rmdir(item_path)
                except Exception:
                    pass
                continue
            new_folder = os.path.join(dest_dir, os.path.basename(item_path))
            try:
                def dir_content_equal(dir1, dir2):
                    # 递归判断两个文件夹内容是否完全一致
                    import filecmp
                    cmp = filecmp.dircmp(dir1, dir2)
                    if cmp.left_only or cmp.right_only or cmp.funny_files:
                        return False
                    for fname in cmp.common_files:
                        f1 = os.path.join(dir1, fname)
                        f2 = os.path.join(dir2, fname)
                        try:
                            with open(f1, 'rb') as ff1, open(f2, 'rb') as ff2:
                                if ff1.read() != ff2.read():
                                    return False
                        except Exception:
                            return False
                    for subdir in cmp.common_dirs:
                        if not dir_content_equal(os.path.join(dir1, subdir), os.path.join(dir2, subdir)):
                            return False
                    return True

                if not os.path.exists(new_folder):
                    shutil.move(item_path, new_folder)
                else:
                    # 如果两个文件夹内容完全一致，跳过整个移动
                    if dir_content_equal(item_path, new_folder):
                        try:
                            force_remove_directory(item_path)
                        except Exception:
                            pass
                        continue
                    # 目标已存在，移动子项到目标目录以实现合并
                    for child in os.listdir(item_path):
                        child_src = os.path.join(item_path, child)
                        child_dst = os.path.join(new_folder, child)
                        # 如果目标子项已存在，判断内容是否一致
                        if os.path.exists(child_dst):
                            try:
                                # 只对文件做内容比对，文件夹递归比对
                                if os.path.isfile(child_src) and os.path.isfile(child_dst):
                                    with open(child_src, 'rb') as f1, open(child_dst, 'rb') as f2:
                                        if f1.read() == f2.read():
                                            continue
                                elif os.path.isdir(child_src) and os.path.isdir(child_dst):
                                    if dir_content_equal(child_src, child_dst):
                                        try:
                                            force_remove_directory(child_src)
                                        except Exception:
                                            pass
                                        continue
                                # 内容不同才重命名
                            except Exception:
                                pass
                            base, ext = os.path.splitext(child)
                            i = 1
                            new_name = f"{base}_{i}{ext}"
                            while os.path.exists(os.path.join(new_folder, new_name)):
                                i += 1
                                new_name = f"{base}_{i}{ext}"
                            child_dst = os.path.join(new_folder, new_name)
                        shutil.move(child_src, child_dst)

                # 尝试删除已空的原目录
                try:
                    os.rmdir(item_path)
                except Exception:
                    # 如果无法删除（可能包含锁定文件），使用强制删除
                    try:
                        force_remove_directory(item_path)
                    except Exception:
                        pass

                moved_count += 1
                # 递归统计目标文件夹中的图片数量并收集日志（更准确）
                try:
                    total_imgs = 0
                    for r, dlist, flist in os.walk(new_folder):
                        for fname in flist:
                            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                                total_imgs += 1
                    if total_imgs:
                        logs.append(f"    📁 收集文件夹: {os.path.basename(new_folder)} ({total_imgs} 张图片)")
                    else:
                        logs.append(f"    📁 收集文件夹: {os.path.basename(new_folder)} (无图片，已转移)")
                except Exception:
                    logs.append(f"    📁 收集文件夹: {os.path.basename(new_folder)} (已转移)")
            except Exception as e:
                logs.append(f"    ⚠️ 移动失败: {item}, 错误: {e}")
        else:
            # 文件：无论是否为图片都移动到目标目录，遇到重名则加后缀避免覆盖
            try:
                target = os.path.join(dest_dir, item)
                if os.path.exists(target):
                    # 如果目标已存在且内容完全一致则跳过移动
                    try:
                        if os.path.isfile(item_path) and os.path.isfile(target):
                            with open(item_path, 'rb') as f1, open(target, 'rb') as f2:
                                if f1.read() == f2.read():
                                    continue
                    except Exception:
                        pass
                    base, ext = os.path.splitext(item)
                    i = 1
                    new_name = f"{base}_{i}{ext}"
                    while os.path.exists(os.path.join(dest_dir, new_name)):
                        i += 1
                        new_name = f"{base}_{i}{ext}"
                    target = os.path.join(dest_dir, new_name)
                shutil.move(item_path, target)
                moved_count += 1
                if item.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    logs.append(f"    🖼️ 收集图片: {os.path.basename(target)}")
                else:
                    logs.append(f"    📄 收集文件: {os.path.basename(target)} (非图片)")
            except Exception as e:
                logs.append(f"    ⚠️ 移动失败: {item}, 错误: {e}")

    if collect_logs:
        return logs
    else:
        for log in logs:
            print(log)
        return moved_count

if __name__ == "__main__":
    run_with_console_progress()
