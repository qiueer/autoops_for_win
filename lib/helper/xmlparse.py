#-*- encoding:utf-8 -*-
import time
import sys
import traceback
  
try:                                           # 导入模块  
    import xml.etree.cElementTree as ET  
except ImportError:  
    import xml.etree.ElementTree as ET  

class APPOpsXml(object):
    def __init__(self, xmlpath):
        try:
            self._xml_path = xmlpath
            self._root = ET.parse(self._xml_path)
        except Exception:
            print traceback.format_exc()
            
    def get_appname(self):
        root = self._root
        return root.find("app").text
    
    def get_actions(self):
        try:
            root = self._root
            xpath = "./actions"
            actions = root.findall(xpath)
            act_list = list()
            for act in actions:
                for subnd in act:
                    act_list.append(str(subnd.tag).strip())
            return act_list
        except Exception:
            print traceback.format_exc()
            return list()
            
    def get_action_steps(self, action):
        try:
            root = self._root
            xpath = "./actions/%s/steps/step" % (action)
            action_steps = root.findall(xpath)
            action_step_list = list()
            for step1 in action_steps:
                ## node attribute，这儿的属性是确定的，action/func
                action = step1.get("action")
                func = step1.get("func")
                stepconf = {
                    "action": action,
                    "func": func,
                    "data":{},
                }
    
                for subnd in step1:
                    ## value
                    stepconf["data"][subnd.tag] = subnd.text
                    ## attribute，这儿设定属性的优先级比value的高，如果该标签存在属性，也存在值，则只取属性，忽略值
                    attrs = subnd.items()
                    if not attrs:continue
                    stepconf["data"][subnd.tag] = {}
                    for (att,val) in attrs:
                        stepconf["data"][subnd.tag][att] = val
                action_step_list.append(stepconf)
            return action_step_list
        except Exception:
            print traceback.format_exc()
        