#!/bin/env python3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import os
import json
import random
import time
import datetime
import traceback
import requests
import smtplib
import sys
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

date_of_today = datetime.datetime.now()  # 当日日期
date_of_tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)  # 次日日期
current_folder = os.path.split(os.path.realpath(__file__))[0]  # 当前py文件路径
# 疫情每日上报和入校申请URL
daily_report_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do#/dailyReport'
enter_campus_apply_url = 'http://ehall.seu.edu.cn/qljfwapp3/sys/lwWiseduElectronicPass/*default/index.do#/'
server_chan_url = 'https://sc.ftqq.com/{}.send/'


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
    WebDriverWait(drv, timeout).until(lambda d: d.find_element('class name', class_name))


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
    elements = drv.find_elements('class name', class_name)
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
    elements = drv.find_elements('class name', class_name)
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
    username_input = drv.find_element('id', 'username')  # 账户输入框
    password_input = drv.find_element('id', 'password')  # 密码输入框
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
    add_btn = drv.find_element('xpath', '//*[@id="app"]/div/div[1]/button[1]')  # 找到新增按钮
    if add_btn.text == '新增':
        add_btn.click()  # 点击新增填报按钮
        time.sleep(1)
        popup = find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定')  # 查询是否弹出了对话框
        if popup is not None:  # 如果弹出了对话框
            message(user, '用户' + user['username'] + '当前不在每日健康上报时间!', '')
            return
    else:  # 没有找到新增按钮
        message(user, '用户' + user['username'] + '今日已进行过每日上报！', '')
        return

    wait_element_by_class_name(drv, "emapm-form", 30)  # 等待界面动画

    # 输入体温
    temp_input = find_element_by_class_placeholder_keyword(drv, 'mint-field-core', '请输入当天晨检体温')
    drv.execute_script("arguments[0].scrollIntoView();", temp_input)  # 滚动页面直元素可见
    temp_input.click()  # 点击输入框
    time.sleep(0.5)
    temp = random.randint(int(user['temp_range'][0] * 10), int(user['temp_range'][1] * 10))  # 产生随机体温
    temp_input.send_keys(str(temp / 10))  # 输入体温
    time.sleep(0.5)

    # 点击提交按钮并确认
    find_element_by_class_keyword(drv, 'mint-button--large', '确认并提交').click()  # 点击提交按钮
    wait_element_by_class_name(drv, 'mint-msgbox-confirm', 5)  # 等待弹出动画
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定').click()  # 点击确认按钮

    message(user, '用户' + user['username'] + '每日上报成功', '')


def get_driver():
    """
    获取webdriver对象

    Returns:
        drv: webdriver对象，若失败返回None
    """
    file_list = os.listdir()

    # 判断浏览器类型
    for file in file_list:
        if file.lower().find('chromedriver') != -1:
            return webdriver.Chrome(service=ChromeService(executable_path=os.path.join(current_folder, file)))

    for file in file_list:
        if file.lower().find('geckodriver') != -1:
            return webdriver.Firefox(service=FirefoxService(executable_path=os.path.join(current_folder, file)))

    print("\033[31m找不到可用的Webdriver\033[0m")
    return None


def run(user):
    """
    填报一个用户

    Args:
        user: 要填报的用户
    """
    driver = get_driver()
    if driver is None:
        return

    try:
        # 打开疫情填报页面并登录
        driver.get(daily_report_url)
        login(driver, user)
        # 每日打卡
        daily_report(driver, user)
    except Exception:
        exception = traceback.format_exc()
        message(user, '用户'+user['username']+'每日上报过程中出错，请尝试手动重新填报', exception)
    finally:
        time.sleep(3)
        driver.quit()  # 退出整个浏览器


def run_all():
    """
    主函数，针对配置文件中的每个用户进行填报
    """
    with open(os.path.join(current_folder, 'config.json'), encoding='UTF-8') as config_file:
        j = json.load(config_file)
        users = j['users']

        for user in users:
            print('\033[35m用户' + user['username'] + '正在每日上报...\033[0m')
            run(user)
            time.sleep(3)


if __name__ == '__main__':
    run_all()
