# Windows下安装自动化部署工具Fabric

> 部署应用程序用FTP还是SCP还是rsync复制文件？如果你需要手动复制，用一次两次还行，一天如果部署50次不但慢、效率低，而且容易出错。<br>
正确的部署方式是使用工具配合脚本完成自动化部署。Fabric就是一个自动化部署工具。由于Fabric是用Python 2.x开发的，所以，部署脚本要用Python 2.7来编写，本机还必须安装Python 2.7版本。<br>
要用Fabric部署，需要在本机（是开发机器，不是Linux服务器）安装Fabric。Linux服务器上不需要安装Fabric，Fabric使用SSH直接登录服务器并执行部署命令。<br>
下面介绍一下在Windows安装Fabric的方法：

## 安装Python

* 第一步：访问[Python官网](https://www.python.org/)，下载2.7.X版本；如：下载的版本为：python-2.7.15.amd64.msi；
* 第二步：安装完成后，设置系统变量；如：将`;C:\Python27;C:\Python27\Scripts`加入到环境变量path中；

## 安装openssh

* 访问
`http://tenet.dl.sourceforge.net/project/sshwindows/OpenSSH%20for%20Windows%20-%20Release/3.8p1-1%2020040709%20Build/setupssh381-20040709.zip`
* 下载类似软件包名称：`setupssh381-20040709.zip` 进行安装。

## 安装VCForPython27.msi

* 访问
 `https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi`

* 下载软件包名称：`VCForPython27.msi` 进行安装。

## 安装c++ 2008/2010

* VC++2008<br>
`https://download.microsoft.com/download/d/2/4/d242c3fb-da5a-4542-ad66-f9661d0a8d19/vcredist_x64.exe`
* VC++2010<br>
`https://download.microsoft.com/download/5/B/C/5BC5DBB3-652D-4DCE-B14A-475AB85EEF6E/vcredist_x86.exe`

* 这两个文件区别如下：Windows7用2008，Windows10用2010；当然，两个都安装也没问题。

## 安装fabric
```
在cmd下执行：

1、pip install pycrypto
2、pip install crypto
3、pip install ecdsa
4、pip install paramiko
5、pip install fabric==1.10.2    # 注意当前最高版本为2.0.1，版本太高内部会有不满足依赖，from fabric.api import * 时会报错：ImportError: No module named api
```

## 安装bsdtar/gzip for windows

> 特别说明：由于fabfile.py（在本文档最后附有）中由于tar for windows不支持.tar.gz/.gz/zip/.bz2等因此这里使用支持这些压缩格式的bsdtar来代替；

```
1、访问 http://gnuwin32.sourceforge.net/packages/libarchive.htm 下载bsdtar安装包：libarchive-2.4.12-1-setup.exe
2、访问 http://gnuwin32.sourceforge.net/packages/gzip.htm 下载gzip安装包：gzip-1.3.12-1-setup.exe
3、安装好后配置环境变量，比如这两个文件都会安装到：C:\Program Files (x86)\GnuWin32\ 目录下，将";C:\Program Files (x86)\GnuWin32\bin"加入到环境变量path中；
4、为了在cmd下使用bsdtar像使用tar命令一样，到目录： C:\Program Files (x86)\GnuWin32\bin 下将bsdtar.exe复制一份重命名为tar.exe，这样在cmd下就可以直接使用 tar -zcvf test.tar.gz test 命令进行打包了，和Linux下用法一致，这样fabfile.py中的build()函数就不会报错了（即执行 fab build 命令就可以正常构建部署包了）。

```

## 编写部署脚本fabfile.py

> Fabric的部署脚本叫fabfile.py，我们把它该文件放到项目的根目录下即可；比如项目目录叫awesome-python-webapp，直接将fabfile.py放到项目目录下即可；<br>
> 如果在开发环境更新了代码，只需要cd到项目目录在命令行执行：

```
$ fab build
$ fab deploy
```

> 自动部署完成！刷新浏览器就可以看到服务器代码更新后的效果。<br>
> fabfile.py该文件包含的功能有：获取当前路径，获取当前时间的字符串格式，应用备份，构建（打包）部署安装包，将安装包上传至服务器，进行（解压）部署安装并重启服务，回滚到前一个版本，将数据库数据备份恢复到本地库等；

## [下载fabfile.py文件](https://github.com/CowryGolden/awesome-python3-webapp/blob/master/fabfile.py)

