"""
Windows 桌面程序操作工具
- 按标题模糊查找窗口
- 激活/置顶窗口
- 向焦点窗口发送文本（模拟键盘输入）
- 关闭窗口

扩展方式: 新增程序只需在调用侧传对应的 name 即可,无需改动本文件。
"""
import ctypes
import time
import win32gui
import win32con


class AppCtrl:

    def __init__(self):
        self._user32 = ctypes.windll.user32
        self._title = None
        self._hwnd = None


    def _find_windows(self, name):
        """按标题模糊匹配,返回 [(hwnd, title), ...]"""
        def cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if name.lower() in title.lower():
                    self._hwnd, self._title = hwnd, title
        win32gui.EnumWindows(cb, None)
        if self._hwnd is None:
            raise Exception("no window found")

    def _focus_window(self):

        if win32gui.IsIconic(self._hwnd):
            win32gui.ShowWindow(self._hwnd, win32con.SW_RESTORE)
        # ponytail: AllowSetForegroundWindow + SetForegroundWindow 两步确保前台
        self._user32.AllowSetForegroundWindow(-1)
        win32gui.SetForegroundWindow(self._hwnd)

    def send_keys(self, text):
        """向当前焦点窗口发送文本(VkKeyScan + keybd_event,支持大小写)"""
        for ch in text:
            vk_scan = self._user32.VkKeyScanW(ord(ch))
            vk = vk_scan & 0xFF
            shift = (vk_scan >> 8) & 0xFF
            mods = []
            if shift & 1:
                mods.append(0x10)  # VK_SHIFT
            if shift & 2:
                mods.append(0x11)  # VK_CTRL
            if shift & 4:
                mods.append(0x12)  # VK_ALT (ponytail: 极少用到,但保留)
            for m in mods:
                self._user32.keybd_event(m, 0, 0, 0)
            self._user32.keybd_event(vk, 0, 0, 0)
            self._user32.keybd_event(vk, 0, 2, 0)  # KEYEVENTF_KEYUP
            for m in reversed(mods):
                self._user32.keybd_event(m, 0, 2, 0)
            time.sleep(0.02)
        return self


    def press_enter(self):
        """发送 Enter 键(VK_RETURN + scancode 0x1C)"""
        self._user32.keybd_event(0x0D, 0x1C, 0, 0)
        time.sleep(0.05)
        self._user32.keybd_event(0x0D, 0x1C, 2, 0)
        time.sleep(0.05)
        return self


    def _get_window_rect(self):
        """获取窗口位置和大小, 返回 {left, top, right, bottom, width, height}"""
        left, top, right, bottom = win32gui.GetWindowRect(self._hwnd)
        return {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
            "width": right - left,
            "height": bottom - top,
        }

    def _click(self, x, y):
        """在屏幕坐标 (x, y) 处执行鼠标左键点击"""
        self._user32.SetCursorPos(x, y)
        time.sleep(0.02)
        self._user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        time.sleep(0.02)
        self._user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
        return self


    def close_window(self):
        """发送 WM_CLOSE 关闭窗口"""
        win32gui.PostMessage(self._hwnd, win32con.WM_CLOSE, 0, 0)
        time.sleep(0.05)
        self._user32.keybd_event(0x0D, 0x1C, 0, 0)




class XShell(AppCtrl):

    def __init__(self):
        super().__init__()
        self._find_windows("Xshell")
        time.sleep(0.05)
        self._before_hooks()


    def _before_hooks(self):
        """开始运维之前需要先输入yes 回车"""
        print("执行Xshell 确认操作...")
        self._focus_window()
        time.sleep(0.05)
        self.send_keys("yes").press_enter()
        time.sleep(0.05)



class MobaXterm(AppCtrl):

    def __init__(self):
        super().__init__()
        self._find_windows("MobaXterm")
        time.sleep(0.05)
        self._before_hooks()

    def _before_hooks(self):
        self._focus_window()
        time.sleep(0.05)


class XFtp(AppCtrl):

    def __init__(self):
        super().__init__()
        self._find_windows("Xftp")
        print(self._get_window_rect())

    def pull_left_path(self, path):
        """窗口右上角相对位置172，182"""
        pass

    def pull_right_path(self, path):
        """窗口右上角相对位置740,182"""
        pass





if __name__ == '__main__':
    x = XFtp()
    # x.send_keys("ls").press_enter()