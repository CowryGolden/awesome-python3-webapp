#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    # 实现目标：为了提升开发效率，使用watchdog实现热部署，实现Debug模式的自动重新加载，不用每次修改Python代码后重启服务。
    # 实现原理：利用watchdog接收文件变化的通知，如果是.py文件，就自动重启app.py进程（服务器端主进程）；
               利用Python自带的subprocess实现进程的启动和终止，并把输入输出重定向到当前进程的输入输出中。

'''
__author__ = 'Cowry Golden'

# 导入依赖
import os, sys, time, subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 记录日志
def log(s):
    print('[Monitor] %s' %s)

# 文件系统控制器类
class MyFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, fn):
        super(MyFileSystemEventHandler, self).__init__()
        self.restart = fn

    # 当以`.py`结尾的文件内容有变动就重启
    def on_any_event(self, event):
        if event.src_path.endswith('.py'):
            log('Python source file changed: %s' % event.src_path)
            self.restart()

command = ['echo', 'ok']
process = None

# 杀掉进程
def kill_process():
    global process
    if process:
        log('Kill process [%s]...' % process.pid)
        process.kill()
        process.wait()
        log('Process ended with code %s.' % process.returncode)
        process = None

# 启动进程，重定向输入输出
def start_process():
    global process, command
    log('Start process %s...' % ' '.join(command))
    process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

# 重启进程
def restart_process():
    kill_process()
    start_process()

# 启动对文件系统监控
def start_watch(path, callback):
    observer = Observer()
    observer.schedule(MyFileSystemEventHandler(restart_process), path, recursive=True)
    observer.start()
    log('Watching directory %s...' % path)
    start_process()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt as ki:
        observer.stop()
    observer.join()

# 测试
if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        print('Usage: ./pymonitor.py your-script.py (Or: python pymonitor.py your-script.py)')
        exit(0)
    if argv[0] != 'python3':
        argv.insert(0, r'D:\ProgramFiles\Python364\python.exe')    # 注意这里要可执行Python的绝对路径，不然找不到Python可执行命令
    command = argv
    path = os.path.abspath('.')
    start_watch(path, None)


