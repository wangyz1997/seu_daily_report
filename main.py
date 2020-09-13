from selenium import webdriver
from config import username, password
import os
import time

driver = webdriver.Chrome(executable_path="Chromedriver.exe")
login_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do#/dailyReport'


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
    buttons = driver.find_elements_by_css_selector('.bh-btn')  # 根据CSS找到所有按钮
    for btn in buttons:
        if btn.get_attribute('textContent').find('新增') >= 0:  # 找到按钮文字是"新增"的按钮
            btn.click()  # 点击新增填报按钮
            break

    texts = driver.find_elements_by_class_name('content')
    for text in texts:
        if text.get_attribute('textContent').find('今日已填报') >= 0:  # 找到今日已填报对话框
            raise Exception('今日已填报')


if __name__ == '__main__':
    try:
        # 登录
        login()
        # 网站响应较慢 需要延时
        time.sleep(10)
        # 点击填报按钮
        press_add_btn()
        # 暂停
        os.system('pause')

    except Exception as e:
        print(e)

    finally:
        # driver.quit()  # 退出整个浏览器
        pass
