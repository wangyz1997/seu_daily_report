from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import config
import os
import platform
import random
import time
import datetime
import server_chan
import traceback

"""
WebDriver下载: http://npm.taobao.org/mirrors/chromedriver/
下载后请与本py文件放置于同一目录中, Windows平台命名为Chromedriver.exe, *nix平台命名为chromedriver
使用方法请参见README.md
"""

driver_folder = os.path.split(os.path.realpath(__file__))[0]
system_type = platform.system()

if system_type == 'Windows':  # 根据系统类型找到driver路径
    driver = webdriver.Chrome(executable_path=os.path.join(driver_folder, "Chromedriver.exe"))
else:
    driver = webdriver.Chrome(executable_path=os.path.join(driver_folder, "chromedriver"))

date_of_tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)  # 次日日期

daily_report_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do#/dailyReport'
enter_campus_apply_url = 'http://ehall.seu.edu.cn/qljfwapp3/sys/lwWiseduElectronicPass/*default/index.do'


def wait_element_by_class_name(drv, class_name, timeout):
    """等待某个class出现"""
    WebDriverWait(drv, timeout).until(lambda d: d.find_element_by_class_name(class_name))


def find_element_by_class_placeholder_keyword(drv, class_name, keyword):
    """用于找具有占位符的对话框"""
    elements = drv.find_elements_by_class_name(class_name)
    for element in elements:
        if element.get_attribute('placeholder').find(keyword) >= 0:
            return element

    return None


def find_element_by_class_keyword(drv, class_name, keyword):
    """寻找对话框/普通按钮"""
    elements = drv.find_elements_by_class_name(class_name)
    for element in elements:
        if element.text.find(keyword) >= 0:
            return element

    return None


def select_default_item_by_keyword(drv, keyword):
    """在入校申请时选择默认项"""
    items = drv.find_elements_by_class_name('emapm-item')  # 找到所有项目
    for item in items:
        if item.text.find(keyword) >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直元素可见
            item.click()

    wait_element_by_class_name(drv, 'mint-picker__confirm', 5)  # 等待弹出动画
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-picker__confirm', '确定').click()  # 点击确定
    time.sleep(1)


def select_default_item_in_areas(drv, keyword):
    """在入校申请时选择通行区域"""
    items = drv.find_elements_by_class_name('emapm-item')  # 找到所有项目
    for item in items:
        if item.text.find(keyword) >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直元素可见
            item.click()

    wait_element_by_class_name(drv, 'mint-checkbox-new-row', 5)  # 等待弹出动画
    time.sleep(1)
    drv.find_element_by_class_name('mint-checkbox-new-row').click()  # 点击复选框
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-selected-footer-confirm', '确定').click()  # 点击确定按钮
    time.sleep(1)


def picker_click(drv, column, cnt):
    """选择滚轮的中的项目"""
    pickers = column.find_elements_by_class_name('mt-picker-column-item')  # 所有滚动元素
    drv.execute_script("arguments[0].scrollIntoView();", pickers[cnt])  # 滚动页面直元素可见
    pickers[cnt].click()  # 选中元素


def time_date_reason_pick(drv, cfg):
    """选择通行时间及申请理由"""
    items = drv.find_elements_by_class_name('emapm-item')  # 找到所有项目
    for item in items:
        if item.text.find('通行开始时间') >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直元素可见
            item.click()  # 点击项目
            columns = item.find_elements_by_class_name('mint-picker-column')  # 找到项目内所有滚轮
            time.sleep(1)
            picker_click(drv, columns[0], date_of_tomorrow.date().year - 1920)  # 年 从1920年开始
            picker_click(drv, columns[1], date_of_tomorrow.date().month - 1)  # 月
            picker_click(drv, columns[2], date_of_tomorrow.date().day - 1)  # 日
            picker_click(drv, columns[3], 7)  # 时
            picker_click(drv, columns[4], 31)  # 分 入校时间为7时31分
            time.sleep(1)
            find_element_by_class_keyword(drv, 'mint-picker__confirm', '确定').click()  # 点击确定按钮
            time.sleep(1)

        if item.text.find('通行结束时间') >= 0:  # 找到项目标题
            drv.execute_script("arguments[0].scrollIntoView();", item)  # 滚动页面直元素可见
            item.click()  # 点击项目
            columns = item.find_elements_by_class_name('mint-picker-column')  # 找到项目内所有滚轮
            time.sleep(1)
            picker_click(drv, columns[0], date_of_tomorrow.date().year - 1920)  # 年 从1920年开始
            picker_click(drv, columns[1], date_of_tomorrow.date().month - 1)  # 月
            picker_click(drv, columns[2], date_of_tomorrow.date().day - 1)  # 日
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
            picker_click(drv, column, cfg.reasons[date_of_tomorrow.date().weekday()])  # 根据星期自动填写目的
            time.sleep(1)
            find_element_by_class_keyword(drv, 'mint-picker__confirm', '确定').click()  # 点击确定按钮
            time.sleep(1)


def login(drv, cfg):
    """登录"""
    username_input = drv.find_element_by_id('username')
    password_input = drv.find_element_by_id('password')
    login_button = find_element_by_class_keyword(drv, 'auth_login_btn', '登录')  # 登录按钮

    username_input.send_keys(cfg.username)
    password_input.send_keys(cfg.password)
    login_button.click()  # 登录账户


def daily_report(drv, cfg):
    """进行每日上报"""
    # 新增填报
    wait_element_by_class_name(drv, 'mint-layout-lr', 30)  # 等待界面加载 超时30s
    add_btn = drv.find_element_by_xpath('//*[@id="app"]/div/div[1]/button[1]')  # 找到新增按钮
    if add_btn.text == '退出':
        server_chan.server_chan_send(cfg.server_chan_key, '今日疫情上报已填报', '')
        return
    else:
        add_btn.click()  # 点击新增填报按钮
        time.sleep(3)  # 等待界面动画

    # 输入体温
    temp_input = find_element_by_class_placeholder_keyword(drv, 'mint-field-core', '请输入当天晨检体温')
    drv.execute_script("arguments[0].scrollIntoView();", temp_input)  # 滚动页面直元素可见
    temp_input.click()  # 点击输入框
    temp = random.randint(int(cfg.temp_range[0] * 10), int(cfg.temp_range[1] * 10))  # 产生随机体温
    temp_input.send_keys(str(temp / 10))  # 输入体温

    # 点击提交按钮并确认
    find_element_by_class_keyword(drv, 'mint-button--large', '确认并提交').click()  # 点击提交按钮
    wait_element_by_class_name(drv, 'mint-msgbox-confirm', 5)  # 等待弹出动画
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定').click()  # 点击确认按钮

    server_chan.server_chan_send(cfg.server_chan_key, '每日疫情上报成功!', '')


def enter_campus_apply(drv, cfg):
    """进行入校申请"""
    wait_element_by_class_name(drv, 'res-item-ele', 30)  # 等待界面加载 超时30s
    drv.find_element_by_xpath('//*[@id="app"]/div/div[3]').click()  # 找到新增按钮

    time.sleep(2)  # 等待窗口动画弹出
    popup = find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定')  # 查询是否弹出了对话框
    if type(popup) is not None:
        server_chan.server_chan_send(cfg.server_chan_key, '今日入校申请已填报或者不在填报时间', '')
        return

    wait_element_by_class_name(drv, 'emapm-item', 30)  # 等待界面加载
    select_default_item_by_keyword(drv, '身份证件类型')
    select_default_item_by_keyword(drv, '工作场所是否符合防护要求')
    select_default_item_by_keyword(drv, '工作人员能否做好个人防护')
    select_default_item_by_keyword(drv, '是否已在南京居家隔离')
    select_default_item_by_keyword(drv, '目前身体是否健康')

    select_default_item_in_areas(drv, '通行区域')

    time_date_reason_pick(drv, cfg)  # 填入入校时间/出校时间/入校理由

    temp_input = find_element_by_class_placeholder_keyword(drv, 'mint-field-core', '请输入所到楼宇')
    drv.execute_script("arguments[0].scrollIntoView();", temp_input)  # 滚动页面直元素可见
    temp_input.click()  # 点击输入框
    temp_input.send_keys(cfg.reasons[date_of_tomorrow.weekday()])  # 输入入校地址

    find_element_by_class_keyword(drv, 'tg-button', '提交').click()  # 点击提交按钮
    wait_element_by_class_name(drv, 'mint-msgbox-confirm', 5)  # 等待弹出动画
    time.sleep(1)
    find_element_by_class_keyword(drv, 'mint-msgbox-confirm', '确定').click()  # 点击确认按钮

    server_chan.server_chan_send(cfg.server_chan_key, '每日入校申请成功!', '')


def run(drv, cfg):
    try:
        # 打开疫情填报网站
        driver.get(daily_report_url)
        # 登录
        login(drv, cfg)
        # 每日填报
        daily_report(drv, cfg)
        # 打开入校申请网站
        time.sleep(5)
        drv.get(enter_campus_apply_url)
        # 填写入校申请
        enter_campus_apply(drv, cfg)
    except Exception:
        exception = traceback.format_exc()
        server_chan.server_chan_send(cfg.server_chan_key, '出错啦！', exception)
    finally:
        time.sleep(10)
        drv.quit()  # 退出整个浏览器


if __name__ == '__main__':
    run(driver, config)
