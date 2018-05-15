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

# Day 7 - 编写MVC

现在，ORM框架、Web框架和配置都已就绪，我们可以开始编写一个最简单的MVC，把它们全部启动起来。<br>
通过Web框架的@get和ORM框架的Model支持，可以很容易地编写一个处理首页URL的函数；<br>
'__template__'指定的模板文件是test.html，其他参数是传递给模板的数据，所以我们在模板的根目录templates下创建test.html；<br>
然后，在浏览器中访问http://localhost:9000/。<br>
如果数据库的users表什么内容也没有，你就无法在浏览器中看到循环输出的内容。可以自己在MySQL的命令行里给users表添加几条记录，然后再访问。<br>

# Day 8 - 构建前端

虽然我们跑通了一个最简单的MVC，但是页面效果肯定不会让人满意。

对于复杂的HTML前端页面来说，我们需要一套基础的CSS框架来完成页面布局和基本样式。另外，jQuery作为操作DOM的JavaScript库也必不可少。

从零开始写CSS不如直接从一个已有的功能完善的CSS框架开始。有很多CSS框架可供选择。我们这次选择uikit这个强大的CSS框架。它具备完善的响应式布局，漂亮的UI，以及丰富的HTML组件，让我们能轻松设计出美观而简洁的页面。

可以从uikit首页下载打包的资源文件。

所有的静态资源文件我们统一放到www/static目录下，并按照类别归类：

<pre>
static/
+- css/
|  +- addons/
|  |  +- uikit.addons.min.css
|  |  +- uikit.almost-flat.addons.min.css
|  |  +- uikit.gradient.addons.min.css
|  +- awesome.css
|  +- uikit.almost-flat.addons.min.css
|  +- uikit.gradient.addons.min.css
|  +- uikit.min.css
+- fonts/
|  +- fontawesome-webfont.eot
|  +- fontawesome-webfont.ttf
|  +- fontawesome-webfont.woff
|  +- FontAwesome.otf
+- js/
   +- awesome.js
   +- html5.js
   +- jquery.min.js
   +- uikit.min.js
</pre>

由于前端页面肯定不止首页一个页面，每个页面都有相同的页眉和页脚。如果每个页面都是独立的HTML模板，那么我们在修改页眉和页脚的时候，就需要把每个模板都改一遍，这显然是没有效率的。

常见的模板引擎已经考虑到了页面上重复的HTML部分的复用问题。有的模板通过include把页面拆成三部分：
```
<html>
    <% include file="inc_header.html" %>
    <% include file="index_body.html" %>
    <% include file="inc_footer.html" %>
</html>
```
这样，相同的部分inc_header.html和inc_footer.html就可以共享。

但是include方法不利于页面整体结构的维护。jinjia2的模板还有另一种“继承”方式，实现模板的复用更简单。

“继承”模板的方式是通过编写一个“父模板”，在父模板中定义一些可替换的block（块）。然后，编写多个“子模板”，每个子模板都可以只替换父模板定义的block。比如，定义一个最简单的父模板：
```
<!-- base.html -->
<html>
    <head>
        <title>{% block title%} 这里定义了一个名为title的block {% endblock %}</title>
    </head>
    <body>
        {% block content %} 这里定义了一个名为content的block {% endblock %}
    </body>
</html>
```

对于子模板a.html，只需要把父模板的title和content替换掉：
```
{% extends 'base.html' %}

{% block title %} A {% endblock %}

{% block content %}
    <h1>Chapter A</h1>
    <p>blablabla...</p>
{% endblock %}
```

对于子模板b.html，如法炮制：
```
{% extends 'base.html' %}

{% block title %} B {% endblock %}

{% block content %}
    <h1>Chapter B</h1>
    <ul>
       <li>list 1</li>
       <li>list 2</li>
    </ul>
{% endblock %}
```

这样，一旦定义好父模板的整体布局和CSS样式，编写子模板就会非常容易。

# Day 9 - 编写API

什么是Web API呢？

如果我们想要获取一篇Blog，输入http://localhost:9000/blog/123，就可以看到id为123的Blog页面，但这个结果是HTML页面，它同时混合包含了Blog的数据和Blog的展示两个部分。对于用户来说，阅读起来没有问题，但是，如果机器读取，就很难从HTML中解析出Blog的数据。

如果一个URL返回的不是HTML，而是机器能直接解析的数据，这个URL就可以看成是一个Web API。比如，读取http://localhost:9000/api/blogs/123，如果能直接返回Blog的数据，那么机器就可以直接读取。

REST就是一种设计API的模式。最常用的数据格式是JSON。由于JSON能直接被JavaScript读取，所以，以JSON格式编写的REST风格的API具有简单、易读、易用的特点。

编写API有什么好处呢？由于API就是把Web App的功能全部封装了，所以，通过API操作数据，可以极大地把前端和后端的代码隔离，使得后端代码易于测试，前端代码编写更简单。

一个API也是一个URL的处理函数，我们希望能直接通过一个@api来把函数变成JSON格式的REST API，这样，获取注册用户可以用一个API实现如下：
```
@get('/api/users')
def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = yield from User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = yield from User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)
```

只要返回一个dict，后续的response这个middleware就可以把结果序列化为JSON并返回。

我们需要对Error进行处理，因此定义一个APIError，这种Error是指API调用时发生了逻辑错误（比如用户不存在），其他的Error视为Bug，返回的错误代码为internalerror。

客户端调用API时，必须通过错误代码来区分API调用是否成功。错误代码是用来告诉调用者出错的原因。很多API用一个整数表示错误码，这种方式很难维护错误码，客户端拿到错误码还需要查表得知错误信息。更好的方式是用字符串表示错误代码，不需要看文档也能猜到错误原因。

可以在浏览器直接测试API，例如，输入http://localhost:9000/api/users，就可以看到返回的JSON：

# Day 10 - 用户注册和登录

用户管理是绝大部分Web网站都需要解决的问题。用户管理涉及到用户注册和登录。

> 用户注册

用户注册相对简单，我们可以先通过API把用户注册这个功能实现了；<br>
注意用户口令是客户端传递的经过SHA1计算后的40位Hash字符串，所以服务器端并不知道用户的原始口令。<br>
接下来可以创建一个注册页面，让用户填写注册表单，然后，提交数据到注册用户的API；<br>

> 用户登录

用户登录比用户注册复杂。由于HTTP协议是一种无状态协议，而服务器要跟踪用户状态，就只能通过cookie实现。大多数Web框架提供了Session功能来封装保存用户状态的cookie。<br>
Session的优点是简单易用，可以直接从Session中取出用户登录信息。<br>
Session的缺点是服务器需要在内存中维护一个映射表来存储用户登录信息，如果有两台以上服务器，就需要对Session做集群，因此，使用Session的Web App很难扩展。<br>
我们采用直接读取cookie的方式来验证用户登录，每次用户访问任意URL，都会对cookie进行验证，这种方式的好处是保证服务器处理任意的URL都是无状态的，可以扩展到多台服务器。<br>
由于登录成功后是由服务器生成一个cookie发送给浏览器，所以，要保证这个cookie不会被客户端伪造出来。<br>
实现防伪造cookie的关键是通过一个单向算法（例如SHA1），举例如下：<br>
当用户输入了正确的口令登录成功后，服务器可以从数据库取到用户的id，并按照如下方式计算出一个字符串：<br>
```
"用户id" + "过期时间" + SHA1("用户id" + "用户口令" + "过期时间" + "SecretKey")
```
当浏览器发送cookie到服务器端后，服务器可以拿到的信息包括：<br>
* 用户id
* 过期时间
* SHA1值

如果未到过期时间，服务器就根据用户id查找用户口令，并计算：<br>
```
SHA1("用户id" + "用户口令" + "过期时间" + "SecretKey")
```
并与浏览器cookie中的哈希进行比较，如果相等，则说明用户已登录，否则，cookie就是伪造的。<br>
<b>这个算法的关键在于SHA1是一种单向算法，即可以通过原始字符串计算出SHA1结果，但无法通过SHA1结果反推出原始字符串。</b><br>
利用middlewares在处理URL之前，把cookie解析出来，并将登录用户绑定到request对象上，这样，后续的URL处理函数就可以直接拿到登录用户；<br>

这样，我们就完成了用户注册和登录的功能。

# Day 11 - 编写日志创建页

ASP、JSP、PHP等都是用模板方式生成前端页面。<br>
如果在页面上大量使用JavaScript（事实上大部分页面都会），模板方式仍然会导致JavaScript代码与后端代码绑得非常紧密，以至于难以维护。其根本原因在于负责显示的HTML DOM模型与负责数据和交互的JavaScript代码没有分割清楚。<br>
要编写可维护的前端代码绝非易事。和后端结合的MVC模式已经无法满足复杂页面逻辑的需要了，所以，新的MVVM：Model View ViewModel模式应运而生。<br>
MVVM最早由微软提出来，它借鉴了桌面应用程序的MVC思想，在前端页面中，把Model用纯JavaScript对象表示：<br>
```
<script>
    var blog = {
        name: 'hello',
        summary: 'this is summary',
        content: 'this is content...'
    };
</script>
```
View是纯HTML：
```
<form action="/api/blogs" method="post">
    <input name="name">
    <input name="summary">
    <textarea name="content"></textarea>
    <button type="submit">OK</button>
</form>
```
由于Model表示数据，View负责显示，两者做到了最大限度的分离。<br>
把Model和View关联起来的就是ViewModel。ViewModel负责把Model的数据同步到View显示出来，还负责把View的修改同步回Model。<br>
ViewModel如何编写？需要用JavaScript编写一个通用的ViewModel，这样，就可以复用整个MVVM模型了。<br>
好消息是已有许多成熟的MVVM框架，例如AngularJS，KnockoutJS等。我们选择Vue这个简单易用的MVVM框架来实现创建Blog的页面templates/manage_blog_edit.html。<br>
```
function initVM(blog) {
    var vm = new Vue({
        el: '#vm',
        data: blog,
        methods: {
            submit: function (event) {
                event.preventDefault();
                var $form = $('#vm').find('form');
                $form.postJSON(action, this.$data, function (err, r) {
                    if (err) {
                        $form.showFormError(err);
                    }
                    else {
                        return location.assign('/api/blogs/' + r.id);
                    }
                });
            }
        }
    });
    $('#vm').show();
}
```
初始化Vue时，我们指定3个参数：
1. el：根据选择器查找绑定的View，这里是#vm，就是id为vm的DOM，对应的是一个<div>标签；
2. data：JavaScript对象表示的Model，我们初始化为{ name: '', summary: '', content: ''}；
3. methods：View可以触发的JavaScript函数，submit就是提交表单时触发的函数。

接下来，我们在`<form>`标签中，用几个简单的v-model，就可以让Vue把Model和View关联起来：
```
<!-- input的value和Model的name关联起来了 -->
<input v-model="name" class="uk-width-1-1">
```
Form表单通过`<form v-on="submit: submit">`把提交表单的事件关联到submit方法。<br>
需要特别注意的是，在MVVM中，Model和View是双向绑定的。如果我们在Form中修改了文本框的值，可以在Model中立刻拿到新的值。试试在表单中输入文本，然后在Chrome浏览器中打开JavaScript控制台，可以通过vm.name访问单个属性，或者通过vm.$data访问整个Model：<br>
如果我们在JavaScript逻辑中修改了Model，这个修改会立刻反映到View上。试试在JavaScript控制台输入vm.name = 'MVVM简介'，可以看到文本框的内容自动被同步了：<br>
双向绑定是MVVM框架最大的作用。借助于MVVM，我们把复杂的显示逻辑交给框架完成。由于后端编写了独立的REST API，所以，前端用AJAX提交表单非常容易，前后端分离得非常彻底。<br>

# Day 12 - 编写日志列表页

MVVM模式不但可用于Form表单，在复杂的管理页面中也能大显身手。例如，分页显示Blog的功能，我们先把后端代码写出来：

在apis.py中定义一个Page类用于存储分页信息：`class Page(object):...`

在handlers.py中实现API：
```
@get('/api/blogs')
def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)
```
管理页面：
```
@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }
```
模板页面首先通过API：`GET /api/blogs?page=?`拿到Model：
```
{
    "page": {
        "has_next": true,
        "page_index": 1,
        "page_count": 2,
        "has_previous": false,
        "item_count": 12
    },
    "blogs": [...]
}
```
然后，通过Vue初始化MVVM：
```
<script>
function initVM(data) {
    var vm = new Vue({
        el: '#vm',
        data: {
            blogs: data.blogs,
            page: data.page
        },
        methods: {
            edit_blog: function (blog) {
                location.assign('/manage/blogs/edit?id=' + blog.id);
            },
            delete_blog: function (blog) {
                if (confirm('确认要删除“' + blog.name + '”？删除后不可恢复！')) {
                    postJSON('/api/blogs/' + blog.id + '/delete', function (err, r) {
                        if (err) {
                            return alert(err.message || err.error || err);
                        }
                        refresh();
                    });
                }
            }
        }
    });
    $('#vm').show();
}
$(function() {
    getJSON('/api/blogs', {
        page: {{ page_index }}
    }, function (err, results) {
        if (err) {
            return fatal(err);
        }
        $('#loading').hide();
        initVM(results);
    });
});
</script>
```
View的容器是#vm，包含一个table，我们用v-repeat可以把Model的数组blogs直接变成多行的<tr>：
```
<div id="vm" class="uk-width-1-1">
    <a href="/manage/blogs/create" class="uk-button uk-button-primary"><i class="uk-icon-plus"></i> 新日志</a>

    <table class="uk-table uk-table-hover">
        <thead>
            <tr>
                <th class="uk-width-5-10">标题 / 摘要</th>
                <th class="uk-width-2-10">作者</th>
                <th class="uk-width-2-10">创建时间</th>
                <th class="uk-width-1-10">操作</th>
            </tr>
        </thead>
        <tbody>
            <tr v-repeat="blog: blogs" >
                <td>
                    <a target="_blank" v-attr="href: '/blog/'+blog.id" v-text="blog.name"></a>
                </td>
                <td>
                    <a target="_blank" v-attr="href: '/user/'+blog.user_id" v-text="blog.user_name"></a>
                </td>
                <td>
                    <span v-text="blog.created_at.toDateTime()"></span>
                </td>
                <td>
                    <a href="#0" v-on="click: edit_blog(blog)"><i class="uk-icon-edit"></i>
                    <a href="#0" v-on="click: delete_blog(blog)"><i class="uk-icon-trash-o"></i>
                </td>
            </tr>
        </tbody>
    </table>

    <div v-component="pagination" v-with="page"></div>
</div>
```
往Model的blogs数组中增加一个Blog元素，table就神奇地增加了一行；把blogs数组的某个元素删除，table就神奇地减少了一行。所有复杂的Model-View的映射逻辑全部由MVVM框架完成，我们只需要在HTML中写上v-repeat指令，就什么都不用管了。

可以把v-repeat="blog: blogs"看成循环代码，所以，可以在一个`<tr>`内部引用循环变量blog。v-text和v-attr指令分别用于生成文本和DOM节点属性。


# Day 13 - 提升开发效率-使用watchdog实现热部署，不用每次修改Python代码后重启服务

现在，我们已经把一个Web App的框架完全搭建好了，从后端的API到前端的MVVM，流程已经跑通了。<br>
在继续工作前，注意到每次修改Python代码，都必须在命令行先Ctrl-C停止服务器，再重启，改动才能生效。<br>
在开发阶段，每天都要修改、保存几十次代码，每次保存都手动来这么一下非常麻烦，严重地降低了我们的开发效率。有没有办法让服务器检测到代码修改后自动重新加载呢？<br>
Django的开发环境在Debug模式下就可以做到自动重新加载，如果我们编写的服务器也能实现这个功能，就能大大提升开发效率。<br>
可惜的是，Django没把这个功能独立出来，不用Django就享受不到，怎么办？<br>
其实Python本身提供了重新载入模块的功能，但不是所有模块都能被重新载入。另一种思路是检测www目录下的代码改动，一旦有改动，就自动重启服务器。<br>
按照这个思路，我们可以编写一个辅助程序pymonitor.py，让它启动wsgiapp.py，并时刻监控www目录下的代码改动，有改动时，先把当前wsgiapp.py进程杀掉，再重启，就完成了服务器进程的自动重启。<br>
要监控目录文件的变化，我们也无需自己手动定时扫描，Python的第三方库watchdog可以利用操作系统的API来监控目录文件的变化，并发送通知。我们先用pip安装：
```
$ pip3 install watchdog
```
利用watchdog接收文件变化的通知，如果是.py文件，就自动重启wsgiapp.py进程。<br>
利用Python自带的subprocess实现进程的启动和终止，并把输入输出重定向到当前进程的输入输出中。<br>
通过`pymonitor.py`中大约70行代码实现了Debug模式的自动重新加载。用下面的命令启动服务器：
```
$ python3 pymonitor.py wsgiapp.py
```
或者给pymonitor.py加上可执行权限，启动服务器：
```
$ ./pymonitor.py app.py
```
现在，只要一保存代码，就可以刷新浏览器看到效果，大大提升了开发效率。<br>


