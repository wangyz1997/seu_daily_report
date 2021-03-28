# [东南大学](https://www.seu.edu.cn) 疫情每日上报自动化脚本

> 免责声明：本脚本仅为个人为学习python之目的所编写，使用该脚本造成的一切后果均由使用者承担。
>
> 本人仍然提倡每日按时手动进行疫情上报与入校申请，配合学校进行好疫情防控。

这是一个每日健康上报的自动化脚本，通过正确配置之后，可以实现每日自动健康上报，并通过微信或邮件推送上报结果。

# 使用方法：

## 1. 下载WebDriver

**如果你用的浏览器是 [Google Chrome](https://www.google.cn/chrome/) ，那么**

1. 首先请检查您安装的Chrome版本：浏览器右上角的3个点-帮助-关于Google Chrome。

2. 进入 [淘宝Chrome Driver镜像站](http://npm.taobao.org/mirrors/chromedriver/) 下载与您使用浏览器相同版本的Chrome Driver。

3. 下载后请与本脚本文件放置于同一目录中, Windows平台命名为`Chromedriver.exe`。

**如果你用的浏览器是 [Mozilla Firefox](https://www.firefox.com) ，那么**

1. 请检查安装的Firefox版本：浏览器右上角3条杠-帮助-关于Firefox。

2. 进入 [淘宝geckodriver镜像站](http://npm.taobao.org/mirrors/geckodriver/) 下载与浏览器相同版本的geckodriver。

3. 下载后与本脚本文件放置于同一目录中, Windows平台命名为`geckodriver.exe`。

> Linux / macOS平台请将可执行文件放置于与脚本相同的目录中，并自行修改脚本中`executable_path`中的文件名。

## 2. 安装`python`依赖

本脚本依赖`selenium`包与`requests`包。要安装它们，只需要使用`pip`即可。

```shell
# Windows
pip install requests selenium -i https://pypi.douban.com/simple --user
# unix-python3
pip3 install requests selenium -i https://pypi.douban.com/simple --user
```

## 3. 配置脚本

1. 将脚本目录中的`config_sample.json`重命名为`config.json`。

2. 打开`config.json`，向各个字段中填入合适的值，每个字段的描述如下表所示。

3. [server酱](http://sc.ftqq.com/) 是一个微信推送工具，可以将服务器端执行结果推送到您的微信上。本脚本支持`server酱`推送，您只需要按照其网站上的指引，使用`GitHub`账号登录并扫码绑定您的微信，即可获得`SCKEY`。将取得的`SCKEY`填入`config.json`中的`server_chan_key`字段中，即可启用微信推送功能。
> 由于微信模板消息即将停用，`server酱`也将会停止微信推送服务。若需要使用`server酱`官方提供的其他推送通道，可以直接在`server酱`官网绑定新的推送通道，并将新的`SCKEY`填入。本程序中的接口无需更新。

4. 本脚本同样支持使用邮箱推送执行结果。在`config.json`中的`to_addr`字段填写接收邮件使用的邮箱，即可使用打卡所使用账号的东大邮箱发送一封邮件到该地址。

| 字段名                       | 描述                                                | 是否必填 |
| --------------------------- | -------------------------------------------------- | -------- |
| `username`                  | 一卡通账号（9位）                                     | YES      |
| `password`                  | 一卡通密码                                           | YES      |
| `temp_range`                | 体温范围 ***请一定要在确定自己体温正常的情况下使用此功能*** | YES      |
| `server_chan_key`           | Server酱SCKEY（留空不启用）                           | NO       |
| `from_addr`                 | 发送执行结果的邮箱地址（建议使用SEU邮箱，留空不启用）       | NO       |
| `email_password`            | 发送邮箱密码                                          | NO       |
| `smtp_server`               | 发送邮箱的SMTP服务器地址                               | NO       |
| `to_adr`                    | 接收执行结果的邮箱地址                                  | NO       |
| `browser`                   | 选择浏览器类型（chrome / firefox）                     | YES      |

## 4. 运行脚本

在您正式运行脚本之前，请确认您脚本目录下存在`main.py` `config.json`与`chromedriver.exe`或`geckodriver.exe`。

之后，使用`python`运行`main.py`即可。

## 5. 进阶

您也可以将脚本与运行环境部署到云服务器上，并设置定时计划任务，实现每日自动签到。

若想要同时为多个用户执行本脚本，只需要将`config.json`中`users`字段的配置信息复制多份，每一份均填写一位用户的信息即可。例如：

```
"users": [
      {
         "username": "xxxxxx", "password": "***",
         "temp_range": [35.5, 36.2],
         "server_chan_key": "",
         "to_addr": ""
      },
        {
         "username": "xxxxxx", "password": "***",
         "temp_range": [35.5, 36.2],
         "server_chan_key": "",
         "to_addr": ""
      },
   ]
```
