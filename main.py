#!/bin/env python3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
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
    if add_btn.text == '退出':  # 没有找到新增按钮
        message(user, '用户' + user['username'] + '今日已进行过每日上报！', '')
        return
    else:
        add_btn.click()  # 点击新增填报按钮
        time.sleep(1)
        popup = find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定')  # 查询是否弹出了对话框
        if popup is not None:  # 如果弹出了对话框
            message(user, '用户' + user['username'] + '当前不在每日健康上报时间!', '')
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


def select_default_item_by_keyword(drv, keyword):
    """
    在入校申请时选择默认项

    Args:
        drv: webdriver对象
        keyword: 关键词
    """
    items = drv.find_elements('class name', 'emapm-item')  # 找到所有项目
    for item in items:
        if item.text.find(keyword) >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直到元素可见
            item.click()

    wait_element_by_class_name(drv, 'mint-picker__confirm', 5)  # 等待弹出动画
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-picker__confirm', '确定').click()  # 点击确定
    time.sleep(1)


def select_default_item_in_areas(drv, keyword):
    """
    在入校申请时选择通行区域

    Args:
        drv: webdriver对象
        keyword: 通行区域关键词
    """
    items = drv.find_elements('class name', 'emapm-item')  # 找到所有项目
    for item in items:
        if item.text.find(keyword) >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直元素可见
            item.click()

    wait_element_by_class_name(drv, 'mint-checkbox-new-row', 5)  # 等待弹出动画
    time.sleep(1)
    drv.find_element('class name', 'mint-checkbox-new-row').click()  # 点击复选框
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-selected-footer-confirm', '确定').click()  # 点击确定按钮
    time.sleep(1)


def picker_click(drv, column, cnt):
    """
    选择滚轮的中的项目

    Args:
        drv: webdriver对象
        column: 滚轮的栏目
        cnt: 要选择的位置
    """
    pickers = column.find_elements('class name', 'mt-picker-column-item')  # 所有滚动元素
    drv.execute_script("arguments[0].scrollIntoView();", pickers[cnt])  # 滚动页面直元素可见
    pickers[cnt].click()  # 选中元素


def time_date_reason_pick(drv, user):
    """
    选择通行时间及申请理由

    Args:
        drv: webdriver对象
        user: 用户信息
    """
    items = drv.find_elements('class name', 'emapm-item')  # 找到所有项目
    for item in items:
        if item.text.find('通行开始时间') >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直元素可见
            item.click()  # 点击项目
            columns = item.find_elements('class name', 'mint-picker-column')  # 找到项目内所有滚轮
            time.sleep(1)
            picker_click(drv, columns[0], date_of_tomorrow.date().year - 1920)  # 年 从1920年开始
            picker_click(drv, columns[1], date_of_tomorrow.date().month - 1)  # 月 从1开始
            picker_click(drv, columns[2], date_of_tomorrow.date().day - 1)  # 日 从1开始
            picker_click(drv, columns[3], 7)  # 时
            picker_click(drv, columns[4], 31)  # 分 入校时间为7时31分
            time.sleep(1)
            find_element_by_class_keyword(drv, 'mint-picker__confirm', '确定').click()  # 点击确定按钮
            time.sleep(1)

        if item.text.find('通行结束时间') >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直元素可见
            item.click()  # 点击项目
            columns = item.find_elements('class name', 'mint-picker-column')  # 找到项目内所有滚轮
            time.sleep(1)
            picker_click(drv, columns[0], date_of_tomorrow.date().year - 1920)  # 年 从1920年开始
            picker_click(drv, columns[1], date_of_tomorrow.date().month - 1)  # 月 从1开始
            picker_click(drv, columns[2], date_of_tomorrow.date().day - 1)  # 日 从1开始
            picker_click(drv, columns[3], 21)  # 时
            picker_click(drv, columns[4], 59)  # 分 出校时间为21时59分
            time.sleep(1)
            find_element_by_class_keyword(drv, 'mint-picker__confirm', '确定').click()  # 点击确定按钮
            time.sleep(1)

        if item.text.find('申请理由') >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直元素可见
            item.click()  # 点击项目
            column = item.find_element_by_class_name('mint-picker-column')  # 找到项目内所有滚轮
            time.sleep(1)
            picker_click(drv, column, user['reasons'][date_of_tomorrow.date().weekday()])  # 根据星期自动填写目的
            time.sleep(1)
            find_element_by_class_keyword(drv, 'mint-picker__confirm', '确定').click()  # 点击确定按钮
            time.sleep(1)


def check_today_report(drv):
    """
    检查当日是否已进行过入校申请

    Args:
        drv: webdriver对象
    """
    items = drv.find_elements('class name', 'res-list')  # 找到所有已填报项目
    if len(items) == 0:
        return False  # 第一次填报视为未填报
    latest = find_element_by_class_keyword(items[0], 'res-item-ele', '申请时间').text  # 第一个项目即为最近一次的填报
    latest = latest[latest.find(' ') + 1: latest.rfind(' ')]  # 只保留日期
    latest_date = datetime.datetime.strptime(latest, '%Y-%m-%d').date()  # 转换

    if latest_date == date_of_today.date():  # 今日已经填报过了
        return True

    return False


def enter_campus_apply(drv, user):
    """
    进行入校申请

    Args:
        drv: webdriver对象
        user: 用户信息
    """
    wait_element_by_class_name(drv, 'mint-loadmore-content', 30)  # 等待界面加载 超时30s

    if check_today_report(drv):  # 今日已进行入校申请
        message(user, '用户' + user['username'] + '今日已进行过入校申请！', '')
        return

    drv.find_element_by_class_name('mint-fixed-button').click()  # 找到并点击新增按钮

    time.sleep(2)  # 等待窗口动画弹出
    popup = find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定')  # 查询是否弹出了对话框
    if popup is not None:  # 如果弹出了对话框
        message(user, '用户' + user['username'] + '当前不在入校申请填报时间!', '')
        return

    wait_element_by_class_name(drv, 'emapm-item', 30)  # 等待界面加载
    select_default_item_by_keyword(drv, '身份证件类型')
    select_default_item_by_keyword(drv, '工作场所是否符合防护要求')
    select_default_item_by_keyword(drv, '工作人员能否做好个人防护')
    select_default_item_by_keyword(drv, '是否已在南京居家隔离')
    select_default_item_by_keyword(drv, '目前身体是否健康')

    # 由于上传通信行程码的功能使用了微信内置浏览器API，普通浏览器暂时无法模拟，若您能够解决此问题，欢迎提出PR

    select_default_item_in_areas(drv, '通行区域')  # 填写通行区域

    time_date_reason_pick(drv, user)  # 填入入校时间/出校时间/入校理由

    temp_input = find_element_by_class_placeholder_keyword(drv, 'mint-field-core', '请输入所到楼宇')
    drv.execute_script("arguments[0].scrollIntoView();", temp_input)  # 滚动页面直元素可见
    temp_input.click()  # 点击输入框
    temp_input.send_keys(user['places'][date_of_tomorrow.weekday()])  # 输入入校地址

    find_element_by_class_keyword(drv, 'tg-button', '提交').click()  # 点击提交按钮
    wait_element_by_class_name(drv, 'mint-msgbox-confirm', 5)  # 等待弹出动画
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定').click()  # 点击确认按钮

    message(user, '用户' + user['username'] + '每日入校申请成功!', '')


def get_driver(cfg):
    """
    根据平台及环境获取webdriver对象

    Args:
        cfg: 配置信息

    Returns:
        drv: webdriver对象，若失败返回None
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
                return webdriver.Firefox(executable_path=os.path.join(current_folder, file))
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
        # 打开疫情填报页面并登录
        driver.get(daily_report_url)
        login(driver, user)
        # 每日打卡
        daily_report(driver, user)
        if config['enter_campus_apply']:
            # 打开入校申请页面
            driver.get(enter_campus_apply_url)
            # 入校申请
            enter_campus_apply(driver, user)
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
        config = j['config']

        for user in users:
            print('\033[35m用户' + user['username'] + '正在每日上报...\033[0m')
            run(user, config)
            time.sleep(3)


if __name__ == '__main__':
    run_all()
