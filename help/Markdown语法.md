# 标题1 #
## 标题2 ##
### 标题3 ###
#### 标题4 ####
##### 标题5 ######
####### 标题6 #######

标题1
==
标题2
--

[TOC]

> hello world!
> hello world!
> > hello world!

[TOC]

> hello world!
hello world!
> hello world!

[TOC]
> aaaaaa
>> bbbbbb
>>> cccccc
>>>> dddddd 



标记之外`hello world`标记之外

 标记之外 ` 
< div>   
    < div></div>
    < div></div>
    < div></div>
< /div>
`标记之外



# fadsf
	<div>   
	    <div></div>
	    <div></div>
	    <div></div>
	</div>

#
```javascript
var num = 0;
for (var i = 0; i < 5; i++) {
    num+=i;
}
console.log(num);
```

[百度1](https://www.baidu.com/ "百度一下"){:target="_blank"} 
[百度2][2]{:target="_blank"}
[2]: https://www.baidu.com/   "百度二下"

![](./01.png '描述')

![name][01]
[01]: ./01.png '描述'


[![](./01.png '百度')](https://www.baidu.com){:target="_blank"}        // 内链式

[![](./01.png '百度')][5]{:target="_blank"}                       // 引用式
[5]: https://www.baidu.com



1. one
2. two
3. three

#

* one
* two
* three

# 
1. one
    1. one-1
    2. two-2
2. two 
    * two-1
    * two-2

#

* one

	var a = 10;     // 与上行保持空行并 递进缩进

#
这是文字……

- [x] 选项一
- [ ] 选项二  
- [ ]  [选项3]

#

|    a    |       b       |      c     |
|:-------:|:------------- | ----------:|
|   居中  |     左对齐    |   右对齐   |
|=========|===============|============|


#
a  | b | c  
:-:|:- |-:
    居中    |     左对齐      |   右对齐    
============|=================|=============

#
<p style="color: #AD5D0F;font-size: 30px; font-family: '宋体';">内联样式</p>

#
<pre>
hello world 
         hi
hello world 
</pre>

#
<pre>
    < div>   
        < div>< /div>
        < div>< /div>
        < div>< /div>
    < /div>
</pre>

#
```
<div>   
    <div></div>
    <div></div>
    <div></div>
</div>
```

#
$$ x \href{why-equal.html}{=} y^2 + 1 $$
$ x = {-b \pm \sqrt{b^2-4ac} \over 2a}. $

#
***
---
* * *

#
Markdown[^1]
[^1]: Markdown是一种纯文本标记语言

[公式标题锚点](#1)

### [需要跳转的目录] {#1}    // 方括号后保持空格

#

Markdown 
:   轻量级文本标记语言，可以转换成html，pdf等格式  //  开头一个`:` + `Tab` 或 四个空格

代码块定义
:   代码块定义……

        var a = 10;         // 保持空一行与 递进缩进

#
<xxx@outlook.com>

#
```flow                     // 流程
st=>start: 开始|past:> http://www.baidu.com // 开始
e=>end: 结束              // 结束
c1=>condition: 条件1:>http://www.baidu.com[_parent]   // 判断条件
c2=>condition: 条件2      // 判断条件
c3=>condition: 条件3      // 判断条件
io=>inputoutput: 输出     // 输出
//----------------以上为定义参数-------------------------

//----------------以下为连接参数-------------------------
// 开始->判断条件1为no->判断条件2为no->判断条件3为no->输出->结束
st->c1(yes,right)->c2(yes,right)->c3(yes,right)->io->e
c1(no)->e                   // 条件1不满足->结束
c2(no)->e                   // 条件2不满足->结束
c3(no)->e                   // 条件3不满足->结束
```





