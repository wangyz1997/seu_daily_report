#!/bin/env python3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import os
import json
import random
import time
import traceback
import requests
import smtplib
import sys
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

current_folder = os.path.split(os.path.realpath(__file__))[0]  # 当前py文件路径
# 疫情每日打卡URL
daily_report_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do#/dailyReport'
server_chan_url = 'http://sc.ftqq.com/{}.send/'


def email_send(username, password, remote_email_addr, content, description):
    """
    用SEU邮箱发送上报结果至指定邮箱.

    Args:
        username: 一卡通账号
        password: 一卡通密码
        remote_email_addr: 指定邮箱地址
        content: 邮件标题
        description: 邮件的具体内容
    """

    seu_email_addr = str(username) + "@seu.edu.cn"

    msg = MIMEText(description, 'plain', 'utf-8')
    msg['Subject'] = Header(content, "utf-8").encode()
    msg['From'] = format_addr("SEU Daily Reporter {}".format(seu_email_addr))
    msg['To'] = format_addr("Admin {}".format(remote_email_addr))

    server = smtplib.SMTP_SSL("smtp.seu.edu.cn", 465)  # 启用SSL发信, 端口一般是465
    server.login(seu_email_addr, password)
    server.sendmail(seu_email_addr, [remote_email_addr], msg.as_string())
    server.quit()


def format_addr(s):
    """
    格式化地址.

    Args:
        s: str, 类似"SEU Daily Reporter <xxx@seu.edu.cn>"

    Returns:
        str, 类似"'=?utf-8?q?SEU Daily Reporter?= <xxx@seu.edu.cn>'"
    """
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def server_chan_send(key, content, description):
    """
    使用server酱推送消息

    Args:
        key: API Key (SCKEY)
        content: 消息的标题
        description: 消息的具体内容

    Returns:
        str, http响应
    """
    get_url = server_chan_url.format(key)
    param = dict()
    param['text'] = content
    param['desp'] = description.replace('\n', '\n\n')  # 将格式改为MarkDown格式
    return requests.get(get_url, param)  # 使用requests自带的编码库来避免url编码问题


def message(user, content, description):
    """
    向控制台打印消息，并会根据传入的用户信息判断是否使用server酱或者邮件推送

    Args:
        user: 用户信息
        content: 消息的标题
        description: 消息的具体内容
    """
    print(content)  # 控制台打印消息
    if len(description):
        print('\033[31m'+description+'\033[0m')

    if len(user['server_chan_key']) > 0:
        server_chan_send(user['server_chan_key'], content, description)  # 使用server酱发送

    if len(user['email_addr']) > 0:
        email_send(user['username'], user['password'], user['email_addr'], content, description)


def wait_element_by_class_name(drv, class_name, timeout):
    """
    等待某个class出现

    Args:
        drv: webdriver对象
        class_name: 要等待的class名
        timeout: 超时时间，超时后会由WebDriver抛出异常
    """
    WebDriverWait(drv, timeout).until(lambda d: d.find_element_by_class_name(class_name))


def find_element_by_class_placeholder_keyword(drv, class_name, keyword):
    """
    寻找指定class并具有指定占位文本的输入框对象

    Args:
        drv: webdriver对象
        class_name: 要寻找的class名
        keyword: 占位文本的关键词

    Returns:
        WebElement, 要寻找的对象
    """
    elements = drv.find_elements_by_class_name(class_name)
    for element in elements:
        if element.get_attribute('placeholder').find(keyword) >= 0:  # 查找占位符
            return element

    return None


def find_element_by_class_keyword(drv, class_name, keyword):
    """
    寻找指定class并具有指定占位文本的对话框/普通按钮对象

    Args:
        drv: webdriver对象
        class_name: 要寻找对象的class名
        keyword: 寻找对象中文本的关键词

    Returns:
        WebElement, 要寻找的对象
    """
    elements = drv.find_elements_by_class_name(class_name)
    for element in elements:
        if element.text.find(keyword) >= 0:  # 查找文本
            return element

    return None


def login(drv, user):
    """
    登录

    Args:
        drv: webdriver对象
        user: 用户信息
    """
    username_input = drv.find_element_by_id('username')  # 账户输入框
    password_input = drv.find_element_by_id('password')  # 密码输入框
    login_button = find_element_by_class_keyword(drv, 'auth_login_btn', '登录')  # 登录按钮
    if login_button is None:
        login_button = find_element_by_class_keyword(drv, 'auth_login_btn', 'Sign in')  # 登录按钮

    username_input.send_keys(user['username'])
    password_input.send_keys(user['password'])
    login_button.click()  # 登录账户


def daily_report(drv, user):
    """
    执行每日健康填报

    Args:
        drv: webdriver对象
        user: 用户信息
    """
    # 新增填报
    wait_element_by_class_name(drv, 'mint-loadmore-top', 30)  # 等待界面加载 超时30s
    time.sleep(1)
    add_btn = drv.find_element_by_xpath('//*[@id="app"]/div/div[1]/button[1]')  # 找到新增按钮
    if add_btn.text == '退出':  # 没有找到新增按钮
        message(user, 'User ' + user['username'] + ' has already reported today.', '')
        return
    else:
        add_btn.click()  # 点击新增填报按钮
        time.sleep(10)  # 等待界面动画

    # 输入体温
    temp_input = find_element_by_class_placeholder_keyword(drv, 'mint-field-core', '请输入当天晨检体温')
    drv.execute_script("arguments[0].scrollIntoView();", temp_input)  # 滚动页面直元素可见
    temp_input.click()  # 点击输入框
    temp = random.randint(int(user['temp_range'][0] * 10), int(user['temp_range'][1] * 10))  # 产生随机体温
    temp_input.send_keys(str(temp / 10))  # 输入体温
    time.sleep(1)

    # 点击提交按钮并确认
    find_element_by_class_keyword(drv, 'mint-button--large', '确认并提交').click()  # 点击提交按钮
    wait_element_by_class_name(drv, 'mint-msgbox-confirm', 5)  # 等待弹出动画
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定').click()  # 点击确认按钮

    message(user, str(user['username']) + 'Daily report for ' + user['username'] + ' success!', '')


def get_driver(cfg):
    """
    根据平台及环境获取webdriver对象

    Args:
        cfg: 配置信息

    Returns:
        drv: webdriver对象
    """
    # 判断平台
    driver_option = webdriver.ChromeOptions()
    file_list = os.listdir()

    os_platform = sys.platform
    if os_platform == 'linux':
        ret = os.popen('cat /proc/1/cgroup')
        if ret.read().find('docker') != -1:  # 判断是否在docker中
            print('\033[32m检测到Docker环境，禁用Chrome沙箱\033[0m')  # 检测到docker
            driver_option.add_argument('--no-sandbox')  # 禁用浏览器沙箱

    # 判断浏览器类型
    if cfg['browser'] == "chrome":
        for file in file_list:
            if file.lower().find('chromedriver') != -1:
                return webdriver.Chrome(executable_path=os.path.join(current_folder, file), options=driver_option)

    elif cfg['browser'] == "firefox":
        for file in file_list:
            if file.lower().find('geckodriver'):
                return webdriver.Chrome(executable_path=os.path.join(current_folder, file))
    else:
        print('\033[31m请在config.json中指定正确的浏览器类型\033[0m')
        return None

    print("\033[31m找不到可用的Webdriver\033[0m")
    return None


def run(user, config):
    """
    填报一个用户

    Args:
        user: 要填报的用户
        config: 配置信息
    """
    driver = get_driver(config)
    if driver is None:
        return

    try:
        # 打开疫情填报网站
        driver.get(daily_report_url)
        # 登录
        login(driver, user)
        # 每日打卡
        daily_report(driver, user)
    except Exception:
        exception = traceback.format_exc()
        message(user, '填报'+user['username']+'过程中出错,请尝试手动重新填报', exception)
    finally:
        time.sleep(1)
        driver.quit()  # 退出整个浏览器


def exec():
    """
    主函数，针对配置文件中的每个用户进行填报
    """
    with open(os.path.join(current_folder, 'config.json'), encoding='UTF-8') as config_file:
        j = json.load(config_file)
        users = j['users']
        config = j['config']

        for user in users:
            print('正在填报', user['username'], '...')
            run(user, config)
            print(user['username'], '每日健康上报完毕')
            time.sleep(1)


if __name__ == '__main__':
    exec()
