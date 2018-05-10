# awesome-python3-webapp
Python入门教程实战篇：网站+iOS App源码

# 项目结构
<pre>
awesome-python3-webapp/  <-- 根目录
|
+- backup/               <-- 备份目录
|
+- conf/                 <-- 配置文件
|
+- dist/                 <-- 打包目录
|
+- www/                  <-- Web目录，存放.py文件
|  |
|  +- static/            <-- 存放静态文件
|  |
|  +- templates/         <-- 存放模板文件
|
+- ios/                  <-- 存放iOS App工程
|
+- LICENSE               <-- 代码LICENSE
</pre>

## Day1-搭建开发环境
> 搭建开发环境

首先，确认系统安装的Python版本是3.5.x：
<pre>
E:\PythonWorkspace\test>python --version
Python 3.6.4
</pre>

然后，用pip安装开发Web App需要的第三方库：

异步框架aiohttp：
<pre>
$pip3 install aiohttp
</pre>

前端模板引擎jinja2：
<pre>
$ pip3 install jinja2
</pre>

MySQL 5.x数据库，从官方网站下载并安装，安装完毕后，请务必牢记root口令。为避免遗忘口令，建议直接把root口令设置为password；

MySQL的Python异步驱动程序aiomysql：
<pre>
$ pip3 install aiomysql
</pre>

> 项目结构

选择一个工作目录，然后，我们建立如下的目录结构：
<pre>
awesome-python3-webapp/  <-- 根目录
|
+- backup/               <-- 备份目录
|
+- conf/                 <-- 配置文件
|
+- dist/                 <-- 打包目录
|
+- www/                  <-- Web目录，存放.py文件
|  |
|  +- static/            <-- 存放静态文件
|  |
|  +- templates/         <-- 存放模板文件
|
+- ios/                  <-- 存放iOS App工程
|
+- LICENSE               <-- 代码LICENSE
</pre>

创建好项目的目录结构后，建议同时建立git仓库并同步至GitHub，保证代码修改的安全。

要了解git和GitHub的用法，请移步[Git教程](https://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000)。

> 开发工具

自备，推荐用Sublime Text，请参考[使用文本编辑器](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014316399410395f704750ee9440228135925a6ca1dad8000)。

# Day 2 - 编写Web App骨架

由于我们的Web App建立在asyncio的基础上，因此用aiohttp写一个基本的app.py；

运行python app.py，Web App将在9000端口监听HTTP请求，并且对首页/进行响应；

这里我们简单地返回一个Awesome字符串，在浏览器中可以看到效果；

这说明我们的Web App骨架已经搭好了，可以进一步往里面添加更多的东西。

# Day 3 - 编写ORM

在一个Web App中，所有数据，包括用户信息、发布的日志、评论等，都存储在数据库中。在awesome-python3-webapp中，我们选择MySQL作为数据库。

Web App里面有很多地方都要访问数据库。访问数据库需要创建数据库连接、游标对象，然后执行SQL语句，最后处理异常，清理资源。这些访问数据库的代码如果分散到各个函数中，势必无法维护，也不利于代码复用。

所以，我们要首先把常用的SELECT、INSERT、UPDATE和DELETE操作用函数封装起来。

由于Web框架使用了基于asyncio的aiohttp，这是基于协程的异步模型。在协程中，不能调用普通的同步IO操作，因为所有用户都是由一个线程服务的，协程的执行速度必须非常快，才能处理大量用户的请求。而耗时的IO操作不能在协程中以同步的方式调用，否则，等待一个IO操作时，系统无法响应任何其他用户。

这就是异步编程的一个原则：一旦决定使用异步，则系统每一层都必须是异步，“开弓没有回头箭”。

幸运的是aiomysql为MySQL数据库提供了异步IO的驱动。

具体操作步骤如下：
<pre>
创建连接池
编写执行查询语句的select函数
编写执行insert、update、delete的execute函数
设计ORM
定义Model

</pre>

# Day 4 - 编写Model

> 编写具体的Model

有了ORM，我们就可以把Web App需要的3个表用Model表示出来，具体有：User、Blog、Comment

> 初始化数据库表

如果表的数量很少，可以手写创建表的SQL脚本；
如果表的数量很多，可以从Model对象直接通过脚本自动生成SQL脚本，使用更简单。
把SQL脚本放到MySQL命令行里执行：
<pre>
$ mysql -u root -p < schema.sql
</pre>

> 编写数据访问代码

# Day 5 - 编写Web框架

> 把一个函数映射为一个URL处理函数，定义@get和@post装饰器函数

> 定义RequestHandler

URL处理函数不一定是一个coroutine，因此我们用RequestHandler()来封装一个URL处理函数。<br>
RequestHandler是一个类，由于定义了__call__()方法，因此可以将其实例视为函数。<br>
RequestHandler目的就是从URL函数中分析其需要接收的参数，从request中获取必要的参数，调用URL函数，然后把结果转换为web.Response对象，这样，就完全符合aiohttp框架的要求；<br>
再编写一个add_route函数，用来注册一个URL处理函数；<br>
最后一步，把很多次add_route()注册的调用，变成自动扫描；<br>
最后，在app.py中加入middleware、jinja2模板和自注册的支持。

> middleware

middleware是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的middleware的处理。<br>
一个middleware可以改变URL的输入、输出，甚至可以决定不继续处理而直接返回。middleware的用处就在于把通用的功能从每个URL处理函数中拿出来，集中放到一个地方。例如，一个记录URL日志的logger；<br>
而response这个middleware把返回值转换为web.Response对象再返回，以保证满足aiohttp的要求；<br>
有了这些基础设施，我们就可以专注地往handlers模块不断添加URL处理函数了，可以极大地提高开发效率。

# Day 6 - 编写配置文件

有了Web框架和ORM框架，我们就可以开始装配App了。<br>
通常，一个Web App在运行时都需要读取配置文件，比如数据库的用户名、口令等，在不同的环境中运行时，Web App可以通过读取不同的配置文件来获得正确的配置。<br>
由于Python本身语法简单，完全可以直接用Python源代码来实现配置，而不需要再解析一个单独的.properties或者.yaml等配置文件。<br>
默认的配置文件应该完全符合本地开发环境，这样，无需任何设置，就可以立刻启动服务器。<br>
如果要部署到服务器时，通常需要修改数据库的host等信息，直接修改config_default.py不是一个好办法，更好的方法是编写一个config_override.py，用来覆盖某些默认设置；<br>
把config_default.py作为开发环境的标准配置，把config_override.py作为生产环境的标准配置，我们就可以既方便地在本地开发，又可以随时把应用部署到服务器上。<br>
应用程序读取配置文件需要优先从config_override.py读取。为了简化读取配置文件，可以把所有配置读取到统一的config.py中。






