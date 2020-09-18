from selenium import webdriver
from config import username, password
import os
import platform
import random

"""
WebDriver下载: http://npm.taobao.org/mirrors/chromedriver/
使用方法请参见README.md
"""

driver_folder = os.path.split(os.path.realpath(__file__))[0]
system_type = platform.system()

if system_type == 'Windows':
    driver = webdriver.Chrome(executable_path=os.path.join(driver_folder, "Chromedriver.exe"))
else:
    driver = webdriver.Chrome(executable_path=os.path.join(driver_folder, "Chromedriver"))

login_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do#/dailyReport'

location = '江苏省, 南京市, 玄武区'
temp_range = (35.5, 36.5)


def login():
    """登录"""
    driver.get(login_url)  # 打开登录界面
    username_input = driver.find_element_by_id('username')
    password_input = driver.find_element_by_id('password')
    login_button = driver.find_element_by_class_name('auth_login_btn')  # 登录按钮

    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()  # 登录账户


def press_add_btn():
    """点击填报按钮"""
    btn_found = False
    buttons = driver.find_elements_by_css_selector('.mint-button--normal')  # 根据CSS找到所有按钮
    for add_btn in buttons:
        if add_btn.get_attribute('textContent').find('新增') >= 0:  # 找到按钮文字是"新增"的按钮
            btn_found = True
            add_btn.click()  # 点击新增填报按钮
            break

    if not btn_found:
        raise Exception('今日已填报')


def input_data():
    """输入体温及定位"""
    inputs = driver.find_elements_by_class_name('mint-field-core')
    for temp_input in inputs:
        if temp_input.get_attribute("placeholder").find("请输入当天晨检体温") >= 0:
            temp_input.click()  # 点击输入框
            temp = random.randint(int(temp_range[0]*10), int(temp_range[1]*10))  # 产生随机体温
            temp_input.send_keys(str(temp/10))  # 输入体温

    cells = driver.find_elements_by_class_name('emapm-item')  # 找到所有列表项
    for location_cell in cells:
        cell_title = location_cell.find_element_by_class_name('mint-cell-title')
        if cell_title.get_attribute('textContent') == '当前位置':  # 找到当前位置列表项
            location_input = location_cell.find_element_by_class_name('mint-cell-value')  # 找到输入框
            location_input.set_attribute('textContent', location)  # 强制设置位置


if __name__ == '__main__':
    try:
        # 登录
        login()
        # 网站响应较慢 需要延时
        driver.implicitly_wait(5)
        # 点击填报按钮
        press_add_btn()
        # 输入数据
        input_data()
        # 暂停
        os.system('pause')

    except Exception as e:
        print(e)

    finally:
        # driver.quit()  # 退出整个浏览器
        pass
