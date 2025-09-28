# 精简的 PyQt5 进度条窗口，仅包含一个进度条，尽量减少样式和布局
from PyQt5 import QtWidgets, QtCore
import sys


class MinimalProgressWindow(QtWidgets.QWidget):
    """一个极简进度窗口：只含 QProgressBar，去除额外标签和边距以加速渲染。"""
    def __init__(self, title="Titizz 进度", total=100):
        super().__init__()
        self.total = total
        self.setWindowTitle(title)
        # 稍微增大宽度并留出右侧内边距，避免进度条紧贴标题栏的关闭按钮
        self.setFixedSize(340, 36)
        # 使用工具窗口标志，避免额外装饰，置顶以便用户能立即看到
        flags = QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint
        try:
            self.setWindowFlags(flags)
        except Exception:
            pass

        # 极简布局：只包含进度条，去掉间距和边距
        layout = QtWidgets.QHBoxLayout(self)
        # 增加右侧内边距（第三个值），让控件与标题栏右上角的关闭按钮保持距离
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)
        # 文本进度显示（n/m），放在进度条左侧，固定宽度以避免抖动
        self.label = QtWidgets.QLabel(f"0/{total}")
        try:
            self.label.setAlignment(QtCore.Qt.AlignCenter)
        except Exception:
            pass
        # 缩小文字显示，使 n/m 文本占位更紧凑
        try:
            self.label.setStyleSheet("font-size:10px;")
        except Exception:
            pass
        self.label.setFixedWidth(72)
        layout.addWidget(self.label)

        self.bar = QtWidgets.QProgressBar()
        self.bar.setRange(0, total)
        # 隐藏文字以更简单的渲染；如果需要百分比可以开启
        try:
            self.bar.setTextVisible(False)
        except Exception:
            pass
        # 尽量使用固定高度，减少布局计算
        self.bar.setFixedHeight(24)
        layout.addWidget(self.bar)

    def set_value(self, value, text=None):
        # 更新进度条值
        try:
            self.bar.setValue(value)
        except Exception:
            pass

        # 更新左侧的 n/m 文本；优先使用传入的 text，否则使用当前最大值
        try:
            maxv = self.bar.maximum() if hasattr(self.bar, 'maximum') else getattr(self, 'total', 0)
            if text:
                # 如果传入了自定义文本（例如 文件名），仍保留 n/m 显示在 label
                self.label.setText(f"{value}/{maxv}  ")
            else:
                self.label.setText(f"{value}/{maxv}")
        except Exception:
            pass

        # 只处理必要的事件以保持响应
        QtWidgets.QApplication.processEvents()


class QtProgressApp:
    """轻量封装：默认使用精简窗口（compact），支持延迟创建 QApplication 并打点时间用于调优。

    参数:
      total: 进度条最大值
      create_app: 是否在构造时创建 QApplication
      compact: 使用精简窗口
      auto_close: 当进度达到 total 时，自动关闭并退出事件循环（默认 False）
    """
    def __init__(self, total=100, create_app=False, compact=True, auto_close=False):
        self.app = None
        self.win = None
        self.total = total
        self.compact = compact
        self.auto_close = auto_close
        if create_app:
            self.init_app(total)

    def init_app(self, total=None):
        """确保 QApplication 被创建，并构建精简窗口（快速路径）。"""
        if total is not None:
            self.total = total
        # 在创建 QApplication 之前设置高 DPI 属性
        try:
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        except Exception:
            pass

        # 避免重复创建 QApplication
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        # 选择精简窗口或回退到完整窗口
        if self.compact:
            self.win = MinimalProgressWindow(total=self.total)
        else:
            # 回退：稍微大一点但仍保持简单
            self.win = MinimalProgressWindow(total=self.total)

    def start(self):
        if self.win is None:
            self.init_app(self.total)
        import time
        t0 = time.time()
        self.win.show()
        t1 = time.time()
        # 打印 show 耗时（毫秒）以便调优
        try:
            print(f"⏱️ Qt show time: {(t1-t0)*1000:.0f} ms")
        except Exception:
            pass

    def set_value(self, value, text=None):
        if self.win:
            self.win.set_value(value, text)

            # 如果启用了 auto_close，在进度到达或超过 total 时安排退出
            try:
                if self.auto_close and value >= self.total:
                    # 使用单次定时器在主线程安全地退出事件循环/关闭窗口
                    QtCore.QTimer.singleShot(80, self.quit)
            except Exception:
                pass

    def exec_(self):
        if self.app:
            self.app.exec_()

    def quit(self):
        """安全退出应用：关闭窗口并退出事件循环。"""
        try:
            if self.win:
                self.win.close()
        except Exception:
            pass
        try:
            if self.app:
                # 在 Qt 主线程调用 quit
                self.app.quit()
        except Exception:
            pass

    def close(self):
        """别名：关闭窗口但不强制退出（若要退出事件循环请用 quit）。"""
        try:
            if self.win:
                self.win.close()
        except Exception:
            pass


if __name__ == '__main__':
    # 在 demo 中使用 QTimer 在事件循环内驱动进度，避免阻塞主线程。
    p = QtProgressApp(total=100, create_app=True, compact=True, auto_close=True)

    # 打印 init 耗时（近似）
    try:
        import time as _t
        t0 = _t.time()
        t1 = _t.time()
        print(f"⏱️ Qt init time: {(t1-t0)*1000:.0f} ms")
    except Exception:
        pass

    p.start()

    # 使用 QTimer 每 10ms 更新一次进度（在事件循环内执行）
    step = {'i': 0}

    def tick():
        i = step['i']
        p.set_value(i)
        step['i'] = i + 1
        if step['i'] > p.total:
            # 停止定时器并在短延迟后退出（auto_close 已安排）
            timer.stop()

    timer = QtCore.QTimer()
    timer.timeout.connect(tick)
    timer.start(10)

    # 进入事件循环；auto_close=True 会在进度完成后自动调用 quit()
    p.exec_()