from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import os
import json
import random
import time
import traceback
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr


current_folder = os.path.split(os.path.realpath(__file__))[0]  # 当前py文件路径
# 疫情每日打卡URL
daily_report_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do#/dailyReport'
server_chan_url = 'http://sc.ftqq.com/{}.send/'

def email_send(username, password, remote_email_addr, message):
    """
    用SEU邮箱发送上报结果至指定邮箱.

    Args:
        username: 一卡通账号
        password: 一卡通密码
        remote_email_addr: 指定邮箱地址
        msg: 上报结果.
    """
    if len(remote_email_addr) <=0 :
        return None

    seu_email_addr = str(username) +"@seu.edu.cn"

    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = format_addr("SEU Daily Reporter {}".format(seu_email_addr))
    msg['To'] = format_addr("Admin {}".format(remote_email_addr))
    msg['Subject'] = Header("每日上报结果", "utf-8").encode()

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
    print(content, '\r\n', description)
    if len(key) <= 0:
        return None

    get_url = server_chan_url.format(key)
    param = dict()
    param['text'] = content
    param['desp'] = description.replace('\n', '\n\n')  # 将格式改为MarkDown格式
    return requests.get(get_url, param)  # 使用requests自带的编码库来避免url编码问题


def wait_element_by_class_name(drv, class_name, timeout):
    """等待某个class出现"""
    WebDriverWait(drv, timeout).until(lambda d: d.find_element_by_class_name(class_name))


def find_element_by_class_placeholder_keyword(drv, class_name, keyword):
    """用于找具有占位符的对话框"""
    elements = drv.find_elements_by_class_name(class_name)
    for element in elements:
        if element.get_attribute('placeholder').find(keyword) >= 0:  # 查找占位符
            return element

    return None


def find_element_by_class_keyword(drv, class_name, keyword):
    """寻找对话框/普通按钮"""
    elements = drv.find_elements_by_class_name(class_name)
    for element in elements:
        if element.text.find(keyword) >= 0:  # 查找文本
            return element

    return None


def login(drv, cfg):
    """登录"""
    username_input = drv.find_element_by_id('username')  # 账户输入框
    password_input = drv.find_element_by_id('password')  # 密码输入框
    login_button = find_element_by_class_keyword(drv, 'auth_login_btn', '登录')  # 登录按钮
    if login_button is None:
        login_button = find_element_by_class_keyword(drv, 'auth_login_btn', 'Sign in')  # 登录按钮

    username_input.send_keys(cfg['username'])
    password_input.send_keys(cfg['password'])
    login_button.click()  # 登录账户


def daily_report(drv, cfg):
    """进行每日上报"""
    # 新增填报
    wait_element_by_class_name(drv, 'mint-loadmore-top', 30)  # 等待界面加载 超时30s
    time.sleep(1)
    add_btn = drv.find_element_by_xpath('//*[@id="app"]/div/div[1]/button[1]')  # 找到新增按钮
    if add_btn.text == '退出':  # 没有找到新增按钮
        server_chan_send(cfg['server_chan_key'], '今日已经进行过疫情上报！', '')
        email_send(cfg['username'], cfg['password'], cfg['email_addr'], '今日已经进行过疫情上报！')
        return
    else:
        add_btn.click()  # 点击新增填报按钮
        time.sleep(10)  # 等待界面动画

    # 输入体温
    temp_input = find_element_by_class_placeholder_keyword(drv, 'mint-field-core', '请输入当天晨检体温')
    drv.execute_script("arguments[0].scrollIntoView();", temp_input)  # 滚动页面直元素可见
    temp_input.click()  # 点击输入框
    temp = random.randint(int(cfg['temp_range'][0] * 10), int(cfg['temp_range'][1] * 10))  # 产生随机体温
    temp_input.send_keys(str(temp / 10))  # 输入体温
    time.sleep(1)

    # 点击提交按钮并确认
    find_element_by_class_keyword(drv, 'mint-button--large', '确认并提交').click()  # 点击提交按钮
    wait_element_by_class_name(drv, 'mint-msgbox-confirm', 5)  # 等待弹出动画
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定').click()  # 点击确认按钮

    server_chan_send(cfg['server_chan_key'], str(cfg['username'])+'每日疫情上报成功!', '')
    email_send(cfg['username'], cfg['password'], cfg['email_addr'], '每日疫情上报成功!')


def run(profile, cfg):
    if cfg['browser'] == "chrome":
        driver = webdriver.Chrome(executable_path=os.path.join(current_folder, "Chromedriver.exe"))
    elif cfg['browser'] == "firefox":
        driver = webdriver.Firefox(executable_path=os.path.join(current_folder, "geckodriver.exe"))

    try:
        # 打开疫情填报网站
        driver.get(daily_report_url)
        # 登录
        login(driver, profile)
        # 每日打卡
        daily_report(driver, profile)
    except Exception:
        exception = traceback.format_exc()
        server_chan_send(profile['server_chan_key'], '出错啦,请尝试手动重新填报', exception)
        email_send(cfg['username'], cfg['password'], cfg['email_addr'], '出错啦,请尝试手动重新填报')
    finally:
        time.sleep(1)
        driver.quit()  # 退出整个浏览器


if __name__ == '__main__':
    with open(os.path.join(current_folder, 'config.json'), encoding='UTF-8') as config_file:
        j = json.load(config_file)
        users = j['users']

        for user in users:
            print(user['username'], '正在填报...')
            run(user)
            print(user['username'], '填报完成')
            time.sleep(1)
