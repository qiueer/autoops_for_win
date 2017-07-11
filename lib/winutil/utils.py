# _*_ coding:UTF-8 _*_  
import os
import win32gui  
import win32api
import win32con
import ctypes
import time
import win32process
import win32com.client

GLB_SLEEP_TIME = 0.2

class Point(ctypes.Structure):  
    _fields_ = [("x", ctypes.c_ulong),("y", ctypes.c_ulong)]  
    
    def __str__(self,):
        return "X %s, Y: %s" % (self.x, self.y)
    
#定义结构体，存储当前窗口坐标  
class Rect(ctypes.Structure):  
    _fields_ = [('left', ctypes.c_int),  
                ('top', ctypes.c_int),  
                ('right', ctypes.c_int),  
                ('bottom', ctypes.c_int)]
    
    def __str__(self,):
        return "Left: %s, Top: %s, Bottom: %s, Right: %s" % (self.left, self.top, self.bottom, self.right)
    
class ProcUtil(object):
    @classmethod
    def CreateProc(cls, exepath, paramstr="", cwd=None):
        exepath = u"%s" % (exepath)
        pos = exepath.rfind('\\')
        cwd = cwd if cwd else exepath[0:pos]
        (proc_hd, thread_hd,  proc_id, thread_id) =  win32process.CreateProcess(exepath, paramstr, None, None, 0, win32process.CREATE_NO_WINDOW,   
        None, cwd, win32process.STARTUPINFO())
        return (proc_hd, thread_hd,  proc_id, thread_id)
    
    @classmethod
    def TerminateProc(cls, whd):
        win32process.TerminateProcess(whd,0)
        
    @classmethod
    def TerminateProcByImageName(cls, image_name):
        cmdstr = 'taskkill /F /FI "IMAGENAME eq %s*"' % (image_name)
        os.system(cmdstr)

class WinUtil(object):
    # Add this to __ini__
    shell = win32com.client.Dispatch("WScript.Shell")

    @classmethod
    def SetAsForegroundWindow(cls, hwnd):
        #发送ALT键，ALT键使用%号表示
        cls.shell.SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)
    
    @classmethod
    def GetWinByTitle(cls, clsname=None, win_title=None, is_foreground=True):
        """
        FindWindow： 查找窗口
        """
        whd = 0
        if clsname and win_title:
            whd=win32gui.FindWindow(clsname, win_title)
        elif clsname:
            whd=win32gui.FindWindow(clsname, None)
        elif win_title:
            whd=win32gui.FindWindow(None, win_title)
        if whd and is_foreground == True:
            cls.SetAsForegroundWindow(whd)
        return whd
    
    @classmethod
    def GetComponent(cls, parent_whd=0, win_title=None, comp_cls_name=None, is_foreground=True):
        """
        FindWindowEx： 查找窗口或窗口中的控件
        取得取消按钮的句柄： GetComponent(u"取消", parent_whd=whd)
        取得取消按钮的句柄： GetComponent(comp_cls_name=u"Label", parent_whd=whd), 其中Label为组件的类名，可以通过spy++查找出来，此方法不常用
        """
        whd=win32gui.FindWindowEx(parent_whd, None, comp_cls_name, win_title)
        if whd and is_foreground == True:
            cls.SetAsForegroundWindow(whd)
        return whd
    
    @classmethod
    def GetCompRect(cls, whd):
        rect = Rect()  
        ctypes.windll.user32.GetWindowRect(whd, ctypes.byref(rect))#获取当前窗口坐标
        return rect
    
    @classmethod
    def GetCompCenterPos(cls, whd):
        rect = Rect()  
        ctypes.windll.user32.GetWindowRect(whd, ctypes.byref(rect))#获取当前窗口坐标
        return rect.left+int((rect.right-rect.left)/2), rect.top+int((rect.bottom-rect.top)/2), 
    
    @classmethod
    def SetForegroundWindow(cls, whd):
        cls.SetAsForegroundWindow(whd)
    
    @classmethod
    def SetWinCenter(cls, whd):
        rect = WinUtil.GetCompRect(whd)
        left = (win32api.GetSystemMetrics(win32con.SM_CXFULLSCREEN)-(rect.right-rect.left))/2;  
        top = (win32api.GetSystemMetrics(win32con.SM_CYFULLSCREEN)-(rect.bottom-rect.top))/2;  
        #Move the window to the correct coordinates with SetWindowPos()  
        cls.SetAsForegroundWindow(whd)
        win32gui.SetWindowPos(whd, win32con.HWND_TOPMOST, left, top,-1,-1, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER);  
        win32gui.SetWindowPos(whd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE);  
        
    @classmethod
    def EnumChildWindows(cls, parent_whd):
        if not parent_whd:  
            return  
        whd_child_list = []  
        win32gui.EnumChildWindows(parent_whd, lambda hWnd, param: param.append(hWnd),  whd_child_list)  
        return whd_child_list
    
    @classmethod
    def GetHWndByProcId(cls, procid):
        def callback(hwnd, procinfo):
            pid = procinfo.get("procid", None)
            t, pid_2 = win32process.GetWindowThreadProcessId(hwnd)
            #print pid,"==", find_pid
            if pid == pid_2:
                p_hwnd = win32gui.GetParent(hwnd)
                if  p_hwnd == 0: # top window
                    procinfo["hwnd"] = hwnd
                    return True
        procinfo = {
            "procid": procid,
            "hwnd": None,
        }
        win32gui.EnumWindows(callback, procinfo)
        return procinfo["hwnd"]

    @classmethod
    def GetClassName(cls, whd):
        return win32gui.GetClassName(whd)
    
    @classmethod
    def GetChildWinFromPoint(cls, parent_whd, point):
        return win32gui.ChildWindowFromPoint(parent_whd, point)

    @classmethod
    def GetFocus(cls):
        curtid = win32api.GetCurrentThreadId()
        whd = win32gui.GetForegroundWindow()
        (tid, pid) = win32process.GetWindowThreadProcessId(whd)
        win32process.AttachThreadInput(curtid, tid,True)
        focus_whd = win32gui.GetFocus()
        win32process.AttachThreadInput(curtid, tid, False)
        return focus_whd

class CursorUtil(object):
    @classmethod
    def GetCursorPos(cls):
        point = Point()  
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))  
        return point
    
    @classmethod
    def SetCursorPos(cls, x, y):
        if x >=0 and y >= 0:
            ctypes.windll.user32.SetCursorPos(x, y)
            time.sleep(GLB_SLEEP_TIME)

class MouseUtil(object):
    @classmethod
    def MouseLDown(cls):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(GLB_SLEEP_TIME)
        
    @classmethod
    def MouseLUp(cls):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(GLB_SLEEP_TIME)
        
    @classmethod 
    def MouseRDown(cls):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(GLB_SLEEP_TIME)
        
    @classmethod 
    def MouseRUp(cls):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        time.sleep(GLB_SLEEP_TIME)

    @classmethod 
    def MouseMove(cls, x, y):
        sw = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        sh = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        nx = int(x * 65535 / sw)
        ny = int(y * 65535 / sh)
        win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE|win32con.MOUSEEVENTF_MOVE, nx, ny, 0, 0)
        time.sleep(GLB_SLEEP_TIME)
        
    @classmethod
    def LClick(cls):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN|win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(GLB_SLEEP_TIME)
        
    @classmethod
    def RClick(cls):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN|win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        time.sleep(GLB_SLEEP_TIME)
        
    @classmethod
    def LDClick(cls):
        cls.LClick()
        cls.LClick()
        time.sleep(GLB_SLEEP_TIME)
        
class MsgUtil(object):
    @classmethod
    def  SetText(cls, whd, text):
        win32api.SendMessage(whd,win32con.WM_SETTEXT,None, text)
