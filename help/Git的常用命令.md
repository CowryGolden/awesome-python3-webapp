# Git常用命令

* 创建版本库：
	<pre>
	# 第一步：选择一个合适的地方，创建一个空目录：
	$ mkdir learngit
	$ cd learngit
	$ pwd
	/Users/michael/learngit

	# 第二步：通过git init命令把这个目录变成Git可以管理的仓库：
	$ git init
	Initialized empty Git repository in /Users/michael/learngit/.git/
	</pre>

* 关联并推送到远程库：
	<pre>
	（1）要关联一个远程库，使用命令git remote add origin git@server-name:path/repo-name.git；
		例如：git remote add origin git@github.com:zhoujincheng/learngit.git
	（2）关联后，使用命令 git push -u origin master 第一次推送master分支的所有内容；
	（3）此后，每次本地提交后，只要有必要，就可以使用命令 git push origin master 推送最新修改；
	</pre>

* 从远程库clone：
	<pre>
	git clone git@github.com:zhoujincheng/gitskills.git
	
	要克隆一个仓库，首先必须知道仓库的地址，然后使用git clone命令克隆。
	Git支持多种协议，包括https，但通过ssh支持的原生git协议速度最快。
	</pre>

* 创建dev分支，然后切换到dev分支：
	<pre>
	$ git checkout -b dev
	Switched to a new branch 'dev'
	</pre>

* git checkout命令加上-b参数表示创建并切换，相当于以下两条命令：
	<pre>
	$ git branch dev    # 创建dev分支
	$ git checkout dev  # 切换到dev分支
	Switched to branch 'dev'
	</pre>

* 查看当前分支：
	<pre>
	$ git branch    # git branch命令会列出所有分支，当前分支前面会标一个*号。
	* dev
	  master
	</pre>

* 把文件从工作区（Working Directory）增加到暂存区（Stage(Index)）：
	<pre>
	git add readme.txt
	</pre>

* 把暂存区（Stage(Index)）的所有修改提交到（本地）分支（版本库-History）：
	<pre>
	$ git commit -m "understand how stage works"
	[master 27c9860] understand how stage works
	 2 files changed, 675 insertions(+)
	 create mode 100644 LICENSE	
	</pre>

* 查看git状态：
	<pre>
	$ git status
	</pre>

* 首先使用git checkout master切换回master分支，再把dev分支的工作成果合并到master分支上(要想远程仓库同步合并分支信息，请使用：git push -u origin master 推到远程库)：
	<pre>
	$ git checkout master
	......
	$ git merge dev
	Updating d17efd8..fec145a
	Fast-forward
	 readme.txt |    1 +
	 1 file changed, 1 insertion(+)
	</pre>

* git checkout master切换回master分支，准备合并dev分支，请注意--no-ff参数，表示禁用Fast forward(要想远程仓库同步合并分支信息，请使用：git push -u origin master 推到远程库)：
	<pre>
	$ git merge --no-ff -m "merge with no-ff" dev
	Merge made by the 'recursive' strategy.
	 readme.txt |    1 +
	 1 file changed, 1 insertion(+)
	</pre>

* 合并后，我们用git log看看分支历史：
	<pre>
	$ git log --graph --pretty=oneline --abbrev-commit
	*   7825a50 merge with no-ff
	|\
	| * 6224937 add merge
	|/
	*   59bc1cb conflict fixed
	...
	</pre>

* 使用git log查看历史记录

	<pre>
	$ git log --pretty=oneline
	3628164fb26d48395383f8f31179f24e0882e1e0 append GPL
	ea34578d5496d7dd233c827ed32a8cd576c5ee85 add distributed
	cb926e7ea50ad11b8f9e909c05226233bf755030 wrote a readme file
	......
	</pre>

* 删除feature1分支：
	<pre>
	$ git branch -d feature1
	Deleted branch feature1 (was 75a857c).
	</pre>

* Git还提供了一个stash功能，可以把当前工作现场“储藏”起来，等以后恢复现场后继续工作：
	<pre>
	git stash
	</pre>

* 现在假定需要在master分支上修复，就从master创建临时分支，具体操作步骤如下：
	<pre>
	1. $ git checkout master
	2. $ git checkout -b issue-101
	3. $ git add fixed-bug.txt
	4. $ git commit -m "fix bug 101"
	5. $ git checkout master
	6. $ git merge --no-ff -m "merged bug fix 101" issue-101
	7. $ git branch -d issue-101
	</pre>

* 修复完bug后，重新回到dev工作（git checkout dev、git status发现工作区是干净的，找不到刚才的工作现场），恢复现场：
	<pre>
	$ git stash list    # 用git stash list命令看看
	stash@{0}: WIP on dev: 6224937 add merge

	# 工作现场还在，Git把stash内容存在某个地方了，但是需要恢复一下，有两个办法：
		（1）一是用git stash apply恢复，但是恢复后，stash内容并不删除，你需要用git stash drop来删除；
		（2）另一种方式是用git stash pop，恢复的同时把stash内容也删了：
	# 我们使用第二种方式：
	$ git stash pop
	......
	Dropped refs/stash@{0} (f624f8e5f082f2df2bed8a4e09c12fd2943bdd40)

	# 再用git stash list查看，就看不到任何stash内容了：
	$ git stash list

	# 你可以多次stash，恢复的时候，先用git stash list查看，然后恢复指定的stash，用命令：
	$ git stash apply stash@{0}
	</pre>

* 命令git tag <name>就可以打一个新标签：

	<pre>
	$ git tag v1.0
	
	# 创建带有说明的标签
	$ git tag -a v0.1 -m "version 0.1 released" 3628164    # 用-a指定标签名，-m指定说明文字 3628164指commit hash ID
	</pre>

* 用命令git tag查看所有标签：

	<pre>
	$ git tag
	v1.0
	</pre>

* 对历史提交打标签：

	<pre>
	# 默认标签是打在最新提交的commit上的。有时候，如果忘了打标签，比如，现在已经是周五了，但应该在周一打的标签没有打，怎么办？
	# 方法是找到历史提交的commit id，然后打上就可以了：
	$ git log --pretty=oneline --abbrev-commit
	6a5819e merged bug fix 101
	cc17032 fix bug 101
	7825a50 merge with no-ff
	6224937 add merge
	59bc1cb conflict fixed
	400b400 & simple
	75a857c AND simple
	fec145a branch test
	d17efd8 remove test.txt
	...
	# 比方说要对add merge这次提交打标签，它对应的commit id是6224937，敲入命令：
	$ git tag v0.9 6224937
	$ git tag
	v0.9
	v1.0
	</pre>

* 用git show <tagname>查看标签信息（注意，标签不是按时间顺序列出，而是按字母排序的。）：

	<pre>
	$ git show v0.9
	commit 622493706ab447b6bb37e4e2a2f276a20fed2ab4
	Author: zhoujincheng <zhoujincheng777@gmail.com>
	Date:   Thu Aug 22 11:22:08 2013 +0800
	
	    add merge
	...
	</pre>

* 删除本地库标签：

	<pre>
	$ git tag -d v0.1
	Deleted tag 'v0.1' (was e078af9)
	</pre>

* 推送某个标签到远程，使用命令`git push origin <tagname>`：

	<pre>
	$ git push origin v1.0
	Total 0 (delta 0), reused 0 (delta 0)
	To git@github.com:zhoujincheng/learngit.git
	 * [new tag]         v1.0 -> v1.0


	# 或者，一次性推送全部尚未推送到远程的本地标签：
	$ git push origin --tags
	Counting objects: 1, done.
	Writing objects: 100% (1/1), 554 bytes, done.
	Total 1 (delta 0), reused 0 (delta 0)
	To git@github.com:zhoujincheng/learngit.git
	 * [new tag]         v0.2 -> v0.2
	 * [new tag]         v0.9 -> v0.9
	</pre>

* 删除远程库标签（先删除本地库标签，再将本地修改push到远程即可）：

	<pre>
	# 如果标签已经推送到远程，要删除远程标签就麻烦一点，先从本地删除：
	$ git tag -d v0.9
	Deleted tag 'v0.9' (was 6224937)
	
	# 然后，从远程删除。删除命令也是push，但是格式如下：
	$ git push origin :refs/tags/v0.9
	To git@github.com:zhoujincheng/learngit.git
	 - [deleted]         v0.9
	</pre>

* 一个本地库同时关联多个远程库；如：既关联GitHub，又关联码云：

	<pre>
	# 使用多个远程库时，我们要注意，git给远程库起的默认名称是origin，如果有多个远程库，我们需要用不同的名称来标识不同的远程库。
	# 仍然以learngit本地库为例，我们先删除已关联的名为origin的远程库：
	$ git remote rm origin
	# 然后，先关联GitHub的远程库：
	$ git remote add github git@github.com:zhoujincheng/learngit.git
	# 注意，远程库的名称叫github，不叫origin了。
	# 接着，再关联码云的远程库：
	$ git remote add gitee git@gitee.com:zhoujincheng/learngit.git
	# 同样注意，远程库的名称叫gitee，不叫origin。
	# 现在，我们用git remote -v查看远程库信息，可以看到两个远程库：
	$ git remote -v
	gitee    git@gitee.com:zhoujincheng/learngit.git (fetch)
	gitee    git@gitee.com:zhoujincheng/learngit.git (push)
	github    git@github.com:zhoujincheng/learngit.git (fetch)
	github    git@github.com:zhoujincheng/learngit.git (push)
	
	# 如果要推送到GitHub，使用命令：
	$ git push github master
	# 如果要推送到码云，使用命令
	$ git push gitee master
	# 这样一来，我们的本地库就可以同时与多个远程库互相同步
	┌─────────┐ ┌─────────┐
	│ GitHub  │ │  Gitee  │
	└─────────┘ └─────────┘
	     ▲           ▲
	     └─────┬─────┘
	           │
	    ┌─────────────┐
	    │ Local Repo  │
	    └─────────────┘
	</pre>


## checkout和reset进行版本回退

![Checkout和Reset的关系图解](https://i.imgur.com/kXL6LHq.jpg)

##### 文件层面操作
- git add files 把当前文件放入暂存区域。
- git commit 给暂存区域生成快照并提交。
- git reset -- files 用来撤销最后一次git add files，你也可以用git reset 撤销所有暂存区域文件。
- git checkout -- files 把文件从暂存区域复制到工作目录，用来丢弃本地修改。

![利用checkout将当期节点父节点的内容拷贝到暂存区](https://i.imgur.com/j3ob1jB.jpg)

- checkout命令用于从<b>历史提交（或者暂存区域）</b>中拷贝文件到工作目录，也可用于<b>切换分支</b>。当给定某个文件名时，git会从指定的提交中拷贝文件到暂存区域和工作目录。比如，git checkout HEAD~ foo.c会将提交节点HEAD~(即当前提交节点的父节点)中的foo.c复制到工作目录并且加到暂存区域中。（如果命令中没有指定提交节点，则会从暂存区域中拷贝内容。）<b>注意当前分支不会发生变化</b>。

![使用checkout切换分支](https://i.imgur.com/sFJlncQ.jpg)

- 当不指定文件名，而是给出一个（本地）分支时，那么HEAD标识会移动到那个分支（也就是说，我们“切换”到那个分支了），然后暂存区域和工作目录中的内容会和HEAD对应的提交节点一致。新提交节点（下图中的a47c3）中的所有文件都会被复制（到暂存区域和工作目录中）；只存在于老的提交节点（ed489）中的文件会被删除；不属于上述两者的文件会被忽略，不受影响。

![利用checkout将HEAD与分支分离（危险不建议使用）](https://i.imgur.com/sNpc8a1.jpg)

- 如果既没有指定文件, 也没有指定分枝. 而是只给出一段提交的历史Hash, 只有HEAD会移动到相应的历史提交. 这会造成HEAD分离, <b>非常危险的操作</b>, 这个命令的说明只是为了满足你的好奇心而已, 不要使用这个命令.

![使用reset重置分支节点和工作目录](https://i.imgur.com/4mBfiBN.jpg)

- reset命令把当前分支指向另一个位置，并且有选择的变动工作目录和索引。也用来在从历史仓库中复制文件到索引，而不动工作目录。
- 如果不给选项，那么当前分支指向到那个提交。如果用--hard选项，那么工作目录也更新，如果用--soft选项，那么都不变。

![使用reset回滚到最后一次提交](https://i.imgur.com/h11krad.jpg)

- 如果没有给出提交点的版本号，那么默认用HEAD。这样，分支指向不变，但是索引会回滚到最后一次提交，如果用--hard选项，工作目录也同样。