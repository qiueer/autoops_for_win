## 功能
```
实现Windows GUI应用启停及其他复杂操作的自动化功能
```

## 原理
```
通过配置xml文件的方式定义一系列动作、步骤，此工具会读取XML配置文件并解析获取配置信息，然后调用window API， 
以此实现捕获窗体、模拟鼠标移动、模拟鼠标点击、模拟输入等操作，从而实现GUI应用的启停及其他复杂的GUI操作
```

## 使用步骤
1）安装python/pywin32  
-> python 
点击下面的网址下载即可，本工具使用的版本是：2.7.9  
https://www.python.org/downloads/

-> pywin32  
在工具包tools\pywin32\目录下提供了pywin32 64bit安装程序（适用于python 2.7+），可以选择其中一个安装包来安装即可。 
如果提供的安装包都不兼容，则可访问以下网址找对应版本的安装包安装： 
https://sourceforge.net/projects/pywin32/files/pywin32/ 

2）配置XML文件 
XML配置文件，记录了GUI应用启停等复杂操作过程中涉及到的必要信息，通过配置这些必要信息，告诉本工具具体做什么。 
模拟对GUI应用实现复杂的操作，通常由一系列的原子操作构成，这里说的原子操作，在本工具中被定义为"步骤"。 
本工具实现的"步骤"及每个"步骤"所需要的数据各不相同（子节点）。  
每个"步骤"的定义中，action属性必填，func属性可选，action属性告诉本工具具体的操作，func属性告诉步骤的定义者具体做什么。 
具体来说：  

-> action="run"，运行，通常用来启动GUI应用，例如启动notepad，其中params参数可选  
 ```
<step action="run" func="启动应用">
		<binpath>C:\Windows\notepad.exe</binpath>
		<params></params>
</step>
 ```

-> action="getwin"，捕获窗体，其中titile是窗体标题，clsname是窗体的类名，id是该窗体标识，title/clsname只需要填一个即可，id必填  
 ```
<step action="getwin" func="确定主窗口">
		<title>无标题 - 记事本</title>
		<clsname></clsname>
		<id>main_win</id>
</step>
 ```

-> action="moveto"，移动鼠标，ref_win_id/point必须定义，ref_win_id指明参考的窗体是哪个，point指明鼠标移动到的相对与窗体的坐标 
 ```
<step action="moveto" func="移动到空白处">
		<point x="50" y="60"></point>
		<ref_win_id>main_win</ref_win_id>
</step>
 ```

-> action="lclick"，鼠标左键单击 
 ```
<step action="lclick" func="点击获取焦点">
</step>
 ```

-> action="settext"，输入文本，text属性必填，指明输入的内容 
 ```
<step action="settext" func="输入文件内容">
		<text>hello,world</text>
</step>
 ```

-> action="btnclick"，鼠标左键单击按钮，title/ref_win_id必须定义，其中title指明按钮上的文字，ref_win_id指明按钮位于哪个窗体之上 
 ```
<step action="btnclick" func="点击保存按钮，保存文件">
		<title>保存(&amp;S)</title>
		<ref_win_id>other_save_win</ref_win_id>
</step>
 ```

-> action="command"，执行命令行命令，cmdline必须定义，指明具体需要执行的命令行 
 ```
<step action="command" func="关闭应用">
		<cmdline>taskkill /F /IM notepad.exe</cmdline>
</step>
 ```

## 工具使用方法
1）帮助说明
```
>python win_app_ops.py -h 
Usage: win_app_ops.py [options] 

Options: 
  -h, --help            show this help message and exit 
  -c CONFFILE, --conffile=CONFFILE 
                        configure file 
  -a ACTION, --action=ACTION 
                        action: such as start/stop which action define in 
                        conffile 
  -d, --debug           if debug, default is false 
  ``` 
-c参数，指定要使用的xml配置文件，这个xml文件必须位于工具目录的etc目录下；  
-a参数，指定的操作，在xml中定义的action；  

2）用法示例  
-> 启动记事本，输入文字，保存 
```
python win_app_ops.py -a stop -c notepad.xml
```

-> 关闭记事本 
```
python win_app_ops.py -a start -c notepad.xml
```

## 辅助工具
tools目录下提供了几个辅助工具，简单介绍下其功能  
1）Spy++  
```
微软提供获取窗体标题名及类名的工具 
```
2）wintop  
```
窗口置顶工具，使用此工具，可以将指定的窗口置顶，在捕获鼠标位置，获取窗口位置时比较好用
```
3）实时鼠标位置  
```
用C#开发的winform GUI应用，用于获取实时鼠标坐标以及偏移量。  
其中参考鼠标坐标可以通过Ctrl+G快捷键获取，通过Ctrl+R快捷键重置。
```

