import configparser
import os
import random
import time

# 获取配置，全局都要用到
# 项目路径
from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver import ActionChains

from killChaoxing import bugs_goup

root_dir = os.path.split(os.path.realpath(__file__))[0] #按照路径将文件名和路径分割开
# config.ini文件路径
config_filepath = os.path.join(root_dir, 'config0.ini')#路径拼接
config = configparser.ConfigParser()#ConfigParser 是用来读取配置文件的包
config.read(config_filepath, encoding='utf-8')

@contextmanager
def attempt_get():
    try:
        yield
    except Exception as e:
        pass

# todo 解决阅读，轨迹问题未解决
def kill_article(driver):
    end_time = time.time() + 60 * 60 + random.randint(1, 200)
    loop_time = 0
    rand_pixel = 100
    while time.time() < end_time:
        rand_pixel += random.randint(10, 100)
        js = f"var q=document.documentElement.scrollTop={rand_pixel}"
        driver.execute_script(js)
        sleep_time = random.randint(10, 100)
        time.sleep(sleep_time)
        with attempt_get():  # 让鼠标放在元素上
            main_content = driver.find_element_by_id(config.get('id', 'main_content'))
            p_lst = main_content.find_elements_by_tag_name('p')
            to_perform = p_lst[loop_time]
            ActionChains(driver).move_to_element(to_perform).perform()
        with attempt_get():
            load_more = driver.find_element_by_id(str(config.get('id', 'load_btn')))
            if load_more and loop_time % 20 == 0:  # 可以点下一页了
                bugs_goup()
                load_more.click()
        loop_time += 1
#进行登陆
def login(driver):
    login_url = str(config.get('account','article_url'))
    driver.get(login_url)

if __name__ == '__main__':
    driver = webdriver.Firefox()
    login(driver)
    kill_article(driver)