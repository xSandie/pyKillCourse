# 超星尔雅刷课脚本
写代码不易，求右上角点个Star (T_T)
## 小白如何使用(大概只需要半小时)
环境要求：python3.6，火狐浏览器，geckodriver。 
1. [装好python3.6](https://blog.csdn.net/qq_39313596/article/details/80664945)，并自行装好火狐浏览器。
0. [下载整个项目（可以不注册账号）](https://jingyan.baidu.com/article/b907e6277ede7e46e7891cf7.html)，解压后，进入解压出来的文件夹，[在文件夹内打开命令行窗口](https://zhidao.baidu.com/question/368766370936203684.html)。
0. 在cmd窗口中输入以下命令，等待全部安装完成。
    ```pip install -r requirements.txt --user```
0. [下载geckodriver](https://pan.baidu.com/s/1UALN7gJGf7kN-o67ffcSyQ)，提取码：kskb，[配置geckodriver](https://blog.csdn.net/hy_696/article/details/80114065)。 
0. 用记事本打开并修改config.ini
    ```angular2html
    account = 账号（必须是手机号）
    password = 密码
    url = 你登陆并打开到视频播放界面的网址
    article_url = 打开阅读界面的网址
    ```
0. 右键单击killChaoxing.py选择Edit with IDLE > Edit with IDLE 3.6(64 bit)打开python文件编辑
    ```angular2html
    config_filepath = os.path.join(root_dir, 'config0.ini')  # 路径拼接
    ```
    改为
    ```angular2html
    config_filepath = os.path.join(root_dir, 'config.ini')  # 路径拼接
    ```
    ctrl + s保存，然后关闭文件。
0. [运行killChaoxing.py的python脚本](https://jingyan.baidu.com/article/22fe7ced18776f3002617f2e.html)  
0. 之后会弹出浏览器框，30秒内输入账号密码验证码登陆后，挂在电脑后台慢慢等待即可，注意：不要调整浏览器大小就让他保持最大化以免出现问题。

## 存在问题
1. 刷阅读的时候只能将鼠标放在上面，所以刷课的时候，人可以走，鼠标留着23333。
2. 有几率陷入死循环，Ctrl+C可跳出循环继续刷课。

## 实现细节
1. 主要是调了selenium库，然后加了很多sleep和重复提取页面元素的代码，因为js会刷新页面导致元素失效。
0. 使用了上下问管理器，方便切换iframe，和减少try。
0. 使用了配置文件。  

## TODO
- [x]  模块区分
- [x]  刷阅读
- [x]  自动获取课程正确答案
- [ ]  自动做完课后习题
- [ ]  修改文档

## BUGS
 - [x] 一定概率进入死循环，初步判断是重播按钮出现的缘故
 - [ ] 当随机验证码弹出时，程序就会崩溃

