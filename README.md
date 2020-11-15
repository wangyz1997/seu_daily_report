# [东南大学](https://www.seu.edu.cn) 疫情每日上报及入校申请自动化脚本

> 免责声明：本脚本仅为个人为学习python之目的所编写，使用该脚本造成的一切后果均由使用者承担。
>
> 本人仍然提倡每日按时手动进行疫情上报与入校申请，配合学校进行好疫情防控。

# 使用方法：

## 1. 下载WebDriver
推荐使用 [Google Chrome](https://www.google.cn/chrome/) 作为本脚本使用的浏览器，本文档后面也将以Google Chrome作为示范。

首先请检查您安装的Chrome版本：浏览器右上角的3个点-帮助-关于Google Chrome。

接下来，进入 [淘宝Chrome Driver镜像站](http://npm.taobao.org/mirrors/chromedriver/) 下载与您使用浏览器相同版本的Chrome Driver。

下载后请与本脚本文件放置于同一目录中, Windows平台命名为`Chromedriver.exe`。

Linux/macOS平台请将可执行文件放置于与脚本相同的目录中，并自行修改脚本中`executable_path`中的文件名。

## 2. 下载`python`依赖
本脚本依赖`selenium`包与`requests`包。要安装它们，只需要使用`pip`即可。

```shell script
# Windows
pip install requests selenium -i https://pypi.douban.com/simple --user
# unix-python3
pip3 install requests selenium -i https://pypi.douban.com/simple --user
```

## 3. 使用 [server酱](http://sc.ftqq.com/) 接收脚本执行结果
[server酱](http://sc.ftqq.com/) 是一个微信推送工具，可以将服务器端执行结果推送到您的微信上。

本脚本支持 server酱 推送，您只需要按照其网站上的指引，使用`GitHub`账号登录并扫码绑定您的微信，即可获得`SCKEY`。
将取得的`SCKEY`填入`config.json`中的`server_chan_key`字段中，即可启用微信推送功能。

> 提示：将`server_chan_key`留空，即可禁用微信推送功能。

## 4. 配置脚本

> 提示：与`1.0`版本中不同，`2.0`中为了实现多用户功能，改用了`json`格式的配置文件，如果您进行了版本升级，请重新进行配置。

将脚本目录中的`config_sample.json`重命名为`config.json`。

打开`config.json`，向其中的`username`与`password`后填入您的一卡通账号与密码。

您还可以在其中的`temp_range`中自定义您想要填写的体温范围。 ***请一定要在确定自己体温正常的情况下使用此功能。***

在`places`与`reasons`中您还可以自定义您每日想要填写的入校区域与入校理由，其中的第一个元素为周一，最后一个元素为周日。

`reasons`的取值`0-7`所对应的理由如下所示。

|          理由          | 对应数字 |
| :--------------------: | :------: |
|      到教学楼上课      |    0     |
|      实验室做实验      |    1     |
|      到办公室科研      |    2     |
|    到图书馆学习借书    |    3     |
| 到职能部门、院系办手续 |    4     |
|          开会          |    5     |
|    往返无线谷实验室    |    6     |
|          其他          |    7     |

除此之外，在`config.json`中的`config`字段中，您也可以通过将`enable_enter_campus_apply`项设置为`true`来启动入校申请或`false`来关闭入校申请。

## 5. 运行脚本
在您正式运行脚本之前，请确认您脚本目录下的文件和下面相同：

```
|-- seu_daily_report
    |-- .gitignore
    |-- chromedriver.exe
    |-- config.json
    |-- main.py
    |-- README.md
```

之后，使用`python`运行`main.py`即可。
您也可以将脚本与运行环境部署到云服务器上，并设置定时计划任务，实现每日自动签到。

## 6. 进阶
若想要同时为多个用户执行本脚本，只需要将`config.json`中`users`字段的配置信息复制多份，每一份均填写一位用户的信息即可。
