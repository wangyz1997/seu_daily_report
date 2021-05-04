import random
import datetime
import time
from main import run_all

report_hour = 7  # 每天7-8时之间随机时间自动填报


def get_local_time():
    utc_time = datetime.datetime.utcnow()  # 获取UTC时间
    return utc_time + datetime.timedelta(hours=+8)  # +8区时间


if __name__ == '__main__':
    while True:
        current_time = get_local_time()
        next_report_time = current_time.replace(hour=report_hour, minute=random.randint(0, 59),
                                                second=random.randint(0, 59))  # 获取下次填报时间
        if current_time.hour >= report_hour:  # 如果已经过了填报时间
            next_report_time = next_report_time + datetime.timedelta(days=1)  # 下一天再填报
        print('下次填报时间:', next_report_time.strftime('%Y年%m月%d日 %H:%M:%S'))

        while True:
            current_time = get_local_time()  # 获取当前时间
            if current_time >= next_report_time:
                run_all()
                print('\n')
                break
            time.sleep(1)  # 每秒检测一次
