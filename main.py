from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import config
import os
import platform
import random

"""
WebDriver下载: http://npm.taobao.org/mirrors/chromedriver/
下载后请与本py文件放置于同一目录中, Windows平台命名为Chromedriver.exe, *nix平台命名为chromedriver
使用方法请参见README.md
"""

driver_folder = os.path.split(os.path.realpath(__file__))[0]
system_type = platform.system()

if system_type == 'Windows':
    driver = webdriver.Chrome(executable_path=os.path.join(driver_folder, "Chromedriver.exe"))
else:
    driver = webdriver.Chrome(executable_path=os.path.join(driver_folder, "Chromedriver"))

login_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do#/dailyReport'


def find_element_by_class_keyword(drv, class_name, keyword):
    elements = WebDriverWait(drv, 10).until(
        lambda d: d.find_elements_by_class_name(class_name))
    for element in elements:
        if element.text.find(keyword) >= 0:
            return element

    return None


def login(drv, cfg):
    """登录"""
    drv.get(login_url)  # 打开登录界面
    username_input = drv.find_element_by_id('username')
    password_input = drv.find_element_by_id('password')
    login_button = drv.find_element_by_class_name('auth_login_btn')  # 登录按钮

    username_input.send_keys(cfg.username)
    password_input.send_keys(cfg.password)
    login_button.click()  # 登录账户


def daily_report(drv, cfg):
    """进行每日上报"""

    # 新增填报
    add_btn = find_element_by_class_keyword(drv, 'mint-button--normal', '新增')  # 找到按钮文字是"新增"的按钮
    if add_btn:
        add_btn.click()  # 点击新增填报按钮
    else:
        print('今日已填报')
        return

    # 输入体温
    temp_input = find_element_by_class_keyword(drv, 'mint-field-core', '请输入当天晨检体温')
    temp_input.click()  # 点击输入框
    temp = random.randint(int(cfg.temp_range[0]*10), int(cfg.temp_range[1]*10))  # 产生随机体温
    temp_input.send_keys(str(temp/10))  # 输入体温

    # 点击提交按钮并确认
    find_element_by_class_keyword(drv, 'mint-button--large', '确认并提交').click()  # 点击提交按钮
    find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定').click()  # 点击确认按钮


if __name__ == '__main__':
    try:
        # 登录
        login(driver, config)
        # 每日填报
        daily_report(driver, config)
        print('每日疫情上报成功!')

    finally:
        driver.quit()  # 退出整个浏览器
