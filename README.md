# 超星军事理论课刷课脚本
## 小白如何使用

1. 环境要求：python3.6，火狐浏览器。 
2. 下载整个项目，解压之后，进入解压之后的文件夹，[在文件夹内打开命令行窗口](https://zhidao.baidu.com/question/368766370936203684.html)。
3. 在cmd窗口中输入pip install -r requirements.txt --user，等待全部安装完成。 
4. 用记事本打开config.ini，修改account和password等于号后面的值，其中*password为密码*，*account为账号*。
5. [运行junshililun.py的python脚本](https://jingyan.baidu.com/article/22fe7ced18776f3002617f2e.html)  
6. 之后会弹出浏览器框，30秒内输入账号密码验证码登陆后，挂在电脑后台慢慢等待即可，注意：不要调整浏览器大小就让他保持最大化以免出现问题。

## 实现细节
1. 主要是调了selenium库，然后加了很多sleep和try catch语句块，保证稳定性。
2. 各个模块区分比较明确，方便修改。  

## TODO
- [x]  模块区分
- [ ]  自动确认刷完
- [ ]  自动获取课程正确答案
- [ ]  自动做完课后习题
- [ ]  修改文档

