#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    # 正确的部署方式是使用工具配合脚本完成自动化部署。
    # Fabric就是一个自动化部署工具。由于Fabric是用Python 2.x开发的，所以，部署脚本要用Python 2.7来编写，本机（开发机）还必须安装Python 2.7版本。
        Fabric的部署脚本叫fabfile.py，我们把它放到awesome-python-webapp的目录下，与www目录平级：
            awesome-python-webapp/
            +- fabfile.py
            +- www/
            +- ...
'''
__author__ = 'Cowry Golden'

# 导入依赖
import os, re

from datetime import datetime
from fabric.api import *

# 如下配置根据开发机器和远程服务器的具体情况来修改
env.user = 'CowryGolden'
env.sudo_user = 'root'
env.hosts = ['192.168.56.70']

db_user = 'www-data'
db_password = 'www-data'

_TAR_FILE = 'dist-awesome.tar.gz'

_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE

_REMOTE_BASE_DIR = '/srv/awesome'

# 获取当前路径
def _current_path():
    return os.path.abspath('.')

# 获取当前时间字符串格式
def _now():
    return datetime.now().strftime('%y-%m-%d_%H.%M.%S')

# 应用备份
def backup():
    '''
    Dump entire database on server and backup to local.
    '''
    dt = _now()
    f = 'backup-awesome-%s.sql' % dt
    with cd('/tmp'):
        run('mysqldump --user=%s --password=%s --skip-opt --add-drop-table --default-character-set=utf8 --quick awesome > %s' % (db_user, db_password, f))
        run('tar -czvf %s.tar.gz %s' % (f, f))
        get('%s.tar.gz' % f, '%s/backup/' % _current_path())
        run('rm -f %s' % f)
        run('rm -f %s.tar.gz' % f)

# 构建（打包）部署安装包
def build():
    '''
    Build dist package.
    '''
    includes = ['static', 'templates', 'transwarp', 'favicon.ico', '*.py']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    local('rm -f dist/%s' % _TAR_FILE)
    with lcd(os.path.join(_current_path(), 'www')):
        cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))

# 将安装包上传至服务器，进行（解压）部署安装并重启服务
def deploy():
    newdir = 'www-%s' % _now()
    run('rm -f %s' % _REMOTE_TMP_TAR)
    put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    with cd(_REMOTE_BASE_DIR):
        sudo('mkdir %s' % newdir)
    with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -f www')
        sudo('ln -s %s www' % newdir)
        sudo('chown www-data:www-data www')
        sudo('chown -R www-data:www-data %s' % newdir)
    with settings(warn_only=True):
        sudo('supervisorctl stop awesome')
        sudo('supervisorctl start awesome')
        sudo('/etc/init.d/nginx reload')

RE_FILES = re.compile('\r?\n')

# 回滚到前一个版本
def rollback():
    '''
    rollback to previous version
    '''
    with cd(_REMOTE_BASE_DIR):
        r = run('ls -p -1')
        files = [s[:-1] for s in RE_FILES.split(r) if s.startswith('www-') and s.endswith('/')]
        files.sort(cmp=lambda s1, s2: 1 if s1 < s2 else -1)
        r = run('ls -l www')
        ss = r.split(' -> ')
        if len(ss) != 2:
            print ('ERROR: \'www\' is not a symbol link.')
            return
        current = ss[1]
        print ('Found current symbol link points to: %s\n' % current)
        try:
            index = files.index(current)
        except ValueError, e:
            print ('ERROR: symbol link is invalid.')
            return
        if len(files) == index + 1:
            print ('ERROR: already the oldest version.')
        old = files[index + 1]
        print ('==================================================')
        for f in files:
            if f == current:
                print ('      Current ---> %s' % current)
            elif f == old:
                print ('  Rollback to ---> %s' % old)
            else:
                print ('                   %s' % f)
        print ('==================================================')
        print ('')
        yn = raw_input ('continue? y/N ')
        if yn != 'y' and yn != 'Y':
            print ('Rollback cancelled.')
            return
        print ('Start rollback...')
        sudo('rm -f www')
        sudo('ln -s %s www' % old)
        sudo('chown www-data:www-data www')
        with settings(warn_only=True):
            sudo('supervisorctl stop awesome')
            sudo('supervisorctl start awesome')
            sudo('/etc/init.d/nginx reload')
        print ('ROLLBACKED OK.')

# 将数据库数据备份到本地
def restore2local():
    '''
    Restore db to local
    '''
    backup_dir = os.path.join(_current_path(), 'backup')
    fs = os.listdir(backup_dir)
    files = [f for f in fs if f.startswith('backup-') and f.endswith('.sql.tar.gz')]
    files.sort(cmp=lambda s1, s2: 1 if s1 < s2 else -1)
    if len(files)==0:
        print 'No backup files found.'
        return
    print ('Found %s backup files:' % len(files))
    print ('==================================================')
    n = 0
    for f in files:
        print ('%s: %s' % (n, f))
        n = n + 1
    print ('==================================================')
    print ('')
    try:
        num = int(raw_input ('Restore file: '))
    except ValueError:
        print ('Invalid file number.')
        return
    restore_file = files[num]
    yn = raw_input('Restore file %s: %s? y/N ' % (num, restore_file))
    if yn != 'y' and yn != 'Y':
        print ('Restore cancelled.')
        return
    print ('Start restore to local database...')
    p = raw_input('Input mysql root password: ')
    sqls = [
        'drop database if exists awesome;',
        'create database awesome;',
        'grant select, insert, update, delete on awesome.* to \'%s\'@\'localhost\' identified by \'%s\';' % (db_user, db_password)
    ]
    for sql in sqls:
        local(r'mysql -uroot -p%s -e "%s"' % (p, sql))
    with lcd(backup_dir):
        local('tar zxvf %s' % restore_file)
    local(r'mysql -uroot -p%s awesome < backup/%s' % (p, restore_file[:-7]))
    with lcd(backup_dir):
        local('rm -f %s' % restore_file[:-7])