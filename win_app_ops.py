# _*_ coding:UTF-8 _*_  
import os
import sys
import traceback
import json
import time
from optparse import OptionParser

from lib.helper.xmlparse import APPOpsXml
from lib.winutil.utils import ProcUtil,WinUtil,MouseUtil,CursorUtil,MsgUtil

reload(sys) 
sys.setdefaultencoding('utf8')

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]

def get_right_content(content):
    try:
        content = content.decode("utf8")
    except Exception:
        try:
            content = content.decode("gbk")
        except Exception:
            try:
                content = content.decode("GB2312")
            except Exception:
                pass
    return content
    
def actions(action_steps):
    try:
        hwds = []
        id_whds = {}
        for idx,action_conf in enumerate(action_steps):
            action = action_conf.get("action", "")
            data = action_conf.get("data", {})
            func = action_conf.get("func", "")
            func = get_right_content(func)
            
            print u"[STEP-%s]" % (idx+1)
            print u"Action: %s" % (action)
            print u"Func: %s" % (func)
            print u"Config: %s" % (json.dumps(data, encoding="UTF-8", ensure_ascii=False))
            print 
            
            ## GUI程序
            if action == "run":
                binpath = data.get("binpath", None)
                params = data.get("params", "")
                if binpath:
                    ProcUtil.CreateProc(binpath, paramstr=params)
                    time.sleep(0.5)
                    
            ## 执行命令行命令
            if action == "command":
                cmdline = data.get("cmdline", None)
                if cmdline:
                    os.system(cmdline)
                    time.sleep(0.5)
                
            if action == "getwin":
                title = data.get("title", None)
                clsname = data.get("clsname", None)
                wid = data.get("id", None)
                if not wid:
                    print "[ERROR] GetWin Must Contain ID."
                    sys.exit(1)
                if not title and not clsname:
                    print "[ERROR] GetWin Must Assign One of (clsname, win_title) Or Both"
                    sys.exit(1)
                whd = WinUtil.GetWinByTitle(clsname=clsname, win_title=title)
                if not whd:
                    print "[ERROR] GetWin Can't Find."
                    sys.exit(1)
                WinUtil.SetWinCenter(whd)
                hwds.append(whd)
                id_whds[wid] = whd
                
            if action == "moveto":
                point = data.get("point", {})
                ref_win_id = data.get("ref_win_id", None)
                whd = None
                if not ref_win_id:
                    whd = hwds[-1]
                else:
                    whd = id_whds.get(ref_win_id, None)
                if not whd:
                    print "[ERROR] MoveTo Can't Find Ref Win."
                    sys.exit(1)
                x = int(point.get("x", None))
                y = int(point.get("y", None))
                rect = WinUtil.GetCompRect(whd)
                point = (rect.left+x, rect.top+y)
                MouseUtil.MouseMove(point[0], point[1])
    
            if action == "lclick":
                MouseUtil.LClick()
            
            if action == "rclick":
                MouseUtil.RClick()
                
            if action == "settext":
                text = data.get("text", None)
                if text == None:continue
                focus = WinUtil.GetFocus()
                MsgUtil.SetText(focus, text)
                
            if action == "btnclick":
                title = data.get("title", None)
                ref_win_id = data.get("ref_win_id", None)
                if title == None:continue
                whd = None
                if not ref_win_id:
                    whd = hwds[-1]
                else:
                    whd = id_whds.get(ref_win_id, None)
                if not whd:
                    print "[ERROR] BtnClick Can't Find Ref Win."
                    sys.exit(1)
                WinUtil.SetForegroundWindow(whd)
                btn = WinUtil.GetComponent(whd, win_title=title)
                (x, y) = WinUtil.GetCompCenterPos(btn)
                CursorUtil.SetCursorPos(x, y)
                MouseUtil.LClick()
                
    except Exception:
            print traceback.format_exc()


def main():
    rp = get_realpath()
    try:
        parser = OptionParser()
        parser.add_option("-c", "--conffile",  
                  action="store", dest="conf", default=None,  
                  help="configure file", metavar="CONFFILE")
        parser.add_option("-a", "--action",  
                  action="store", dest="action", default=None,  
                  help="action: such as start/stop which action define in conffile", metavar="ACTION")
        parser.add_option("-d", "--debug", dest="debug", default=False,
                  action="store_true", help="if debug, default is false")

        (options, args) = parser.parse_args()
        conffile = options.conf
        actionstr = options.action
        debug = options.debug
        
        if not conffile:
            parser.print_help()
            sys.exit(1)

        #conffile = os.path.abspath(conffile)
        conffile = rp + "\\etc\\" + conffile
        if os.path.exists(conffile) == False:
            parser.print_help()
            sys.exit(0)

        px = APPOpsXml(conffile)
        actions_def = px.get_actions()

        actionstr = str(actionstr).strip().lower()
        if actionstr not in actions_def:
            parser.print_help()
            sys.exit(1)

        action_steps = px.get_action_steps(actionstr)
        if not action_steps:
            print "Can Not Find Action Defined, Exit..."
            sys.exit(1)

        actions(action_steps)
    except Exception as expt:
        print traceback.format_exc()
        
if __name__ == "__main__":
    main()

