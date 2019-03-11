import itertools  # 排列组合
import logging
import os
import random
from hashlib import md5
from xml import etree

import requests
from selenium.webdriver.common.action_chains import ActionChains  # ActionChains是一个底层的自动交互的方法，例如鼠标移动、鼠标按键事件、键盘响应和菜单右击交互。
# 这些对于像悬停和拖拽这种复杂的行为很有用
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import configparser
from contextlib import contextmanager
from lxml import etree

# 获取配置，全局都要用到
# 项目路径
root_dir = os.path.split(os.path.realpath(__file__))[0]  # 按照路径将文件名和路径分割开
# config.ini文件路径
config_filepath = os.path.join(root_dir, 'config0.ini')  # 路径拼接
config = configparser.ConfigParser()  # ConfigParser 是用来读取配置文件的包
config.read(config_filepath, encoding='utf-8-sig')

@contextmanager
def attempt_get():
    try:
        yield
    except Exception as e:
        pass

#todo 进入做题的frame
@contextmanager
def enter_exercise_iframe(driver):
    driver.switch_to.frame('iframe')  # 元素定位
    mid_iframe = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((
        By.TAG_NAME, 'iframe')))[
        0]  # 等待30秒直到能切换进iframe '''判断某个元素是否被加到了dom树里，并不代表该元素一定可见，如果定位到就返回WebElement'''
    driver.switch_to.frame(mid_iframe)
    driver.switch_to.frame(config.get('id','exercise_frame'))
    yield
    driver.switch_to.default_content()


def get_course_name(ele):
    '''
    找到课程元素中的课程名称
    :param ele:包含课程名的那一个大div
    :return:
    name:课程名称
    '''
    name = ele.find_elements_by_tag_name('span')[-1].text.strip()
    return name


def get_all_exercises(driver):
    ret_dic = {}  # 以字典形式返回，包括课程目录，需特殊对待的课程
    driver.maximize_window()  # 最大化窗口，方便定位和点击（headless模式下不需要）

    temp_courses = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((
        By.CLASS_NAME, config.get('cls', 'courses_total'))))  # 等待30秒，直到课程目录出现，但是出现后页面还是会被js刷新
    time.sleep(5)  # 页面加载js时间
    all_courses = driver.find_elements_by_class_name(config.get('cls', 'courses_total'))
    # 待刷的所有课程
    ret_dic['unfinishedname_lst'] = []
    for course in all_courses:
        indicator = course.find_element_by_class_name(config.get('cls', 'circle_indicator')).text.strip()
        c_name = get_course_name(course)
        if indicator == '1' or c_name != config.get('courses', 'exception1'):
            ret_dic['unfinishedname_lst'].append(course)
    return ret_dic['unfinishedname_lst']

# todo 做课程后的题目
def course_quiez(driver, ele):
    pass

#查题目接口1
def search_course_1(sess, *args: list):# 输入参数处理
    arg = args[0]
    # 接口
    url = "http://mooc.forestpolice.org/cx/0/"

    # 接口参数
    result = []
    data = {}
    data['course'] = ""
    data['type'] = ""
    data['option'] = ""

    # post请求
    try:
        res = sess.post(url + arg, data=data, verify=False)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        answer = []
        answer.append({'topic': str(e), 'correct': ''})
        result.append(answer)

    # 处理结果
    logging.info("Processing result")
    answer = []
    temp = {}
    temp['topic'] = args[0]
    temp['correct'] = res.json()['data']
    if temp['correct'] != '未找到答案':
        answer.append(temp)
    result.append(answer)

    logging.info("Return result: %s" % result)

    return result

#查题目接口2
def search_course_2(sess, *args: list):
    if not isinstance(sess, requests.Session):
        args = list(args)
        args.insert(0, sess)
        args = tuple(args)
        sess = requests.Session()

    # 接口
    url = "https://cx.poxiaobbs.com/index.php"

    # 接口参数
    data = {}
    result = []
    for i in range(len(args)):
        data['tm'] = args[i]

        # post请求
        logging.info("Post to poxiao bbs php. Question %d" % i)
        try:
            res = sess.post(url, data=data, verify=False)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            answer = []
            answer.append({'topic': str(e), 'correct': ''})
            result.append(answer)
            continue

        # 处理结果
        logging.info("Processing result")
        answer = []
        selector = etree.HTML(res.text)
        answer_div = selector.xpath('/html/body/div[1]/div[@class="ans"]')
        for each in answer_div:
            temp = {}
            answer_text = each.xpath('string(.)')\
                .strip().replace('  ', '').replace('\n', '')
            if "答案：" in answer_text:
                temp['topic'] = answer_text.split("答案：")[0]
                temp['correct'] = answer_text.split("答案：")[1]
                answer.append(temp)
        result.append(answer)

    logging.info("Return result: %s" % result)

    return result

#查题目接口3
def search_course_3(sess, args: str):
    # 接口
    url = "https://wangke120.com/selectCxDb.php"

    # 接口参数
    result = []
    data = {}
    data['question'] = args

    # post请求
    try:
        res = sess.post(url, data=data, verify=False)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        answer = []
        answer.append({'topic': str(e), 'correct': ''})
        result.append(answer)

    # 处理结果
    logging.info("Processing result")
    answer = []
    temp = {}
    temp['topic'] = args
    temp['correct'] = res.text
    if temp['correct'] != '未找到':
        answer.append(temp)
    result.append(answer)

    logging.info("Return result: %s" % result)

    return result


#查题目接口4
def search_course_4(sess, *args:list):
    # 接口
    url = "http://www.92daikan.com/tiku.aspx"

    # 获取接口参数
    try:
        res = sess.get(url, verify=False)
        res.raise_for_status()
        selector = etree.HTML(res.text)
        viewstate = selector.xpath('//*[@id="__VIEWSTATE"]/@value')
        viewstategenerator = selector.xpath(
            '//*[@id="__VIEWSTATEGENERATOR"]/@value')
        eventvalidation = selector.xpath(
            '//*[@id="__EVENTVALIDATION"]/@value')
    except requests.exceptions.RequestException as e:
        result = []
        for each in args:
            answer = []
            answer.append({'topic': str(e), 'correct': ''})
            result.append(answer)
        return result

    # 接口参数
    result = []
    data = {}
    data['__VIEWSTATE'] = viewstate
    data['__VIEWSTATEGENERATOR'] = viewstategenerator
    data['__EVENTVALIDATION'] = eventvalidation
    data['ctl00$ContentPlaceHolder1$gen'] = '查询'
    for i in range(len(args)):
        data['ctl00$ContentPlaceHolder1$timu'] = args[i]

        # post请求
        logging.info("Post to 92daikan. Question %d" % i)
        try:
            res = sess.post(url, data=data, verify=False)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            answer = []
            answer.append({'topic': str(e), 'correct': ''})
            result.append(answer)
            continue

        # 处理结果
        logging.info("Processing result")
        answer = []
        selector = etree.HTML(res.text)
        temp = {}
        temp['topic'] = args[i]
        temp['correct'] = selector.xpath('//*[@id="daan"]/text()')[0]
        if temp['correct'] != '未找到答案':
            answer.append(temp)
        result.append(answer)

    logging.info("Return result: %s" % result)

    return result

# 进行登陆
def login(driver):
    login_url = config.get('account', 'url')
    ac = config.get('account', 'account')
    pswd = config.get('account', 'password')
    driver.get(login_url)
    driver.find_element_by_name('uname').send_keys(ac)
    driver.find_element_by_name('password').send_keys(pswd)

# 点击课程
def click_c(course):
    course.click()
    time.sleep(5)

#获得答案列表
def query_ans(single_ques) -> list:
    sess = requests.session()
    ques = [single_ques]
    res1 = [[]]
    res2 = [[]]
    res3 = [[]]
    res4 = [[]]
    with attempt_get():
        res1 = search_course_1(sess, *ques)
    with attempt_get():
        res2 = search_course_2(sess, ques)
    with attempt_get():
        res3 = search_course_3(sess, ques[0])
    with attempt_get():
        res4 = search_course_4(sess, ques)
    #拆包
    ans = []
    ans.append(get_candidate(res1))
    ans.append(get_candidate(res2))
    ans.append(get_candidate(res3))
    ans.append(get_candidate(res4))
    ans_set = set(ans)#去除列表中空的元素
    ans_set.remove('')
    ans = list(ans_set)
    return ans

#拆包，返回可能的答案
def get_candidate(lst_lst) -> str:
    try:
        return lst_lst[0][0].get('correct')
    except IndexError as e:
        return ''

#todo 写单选题逻辑
def kill_single_choice(title_ele, ans_eles):
    pass

#todo 跳转到课后题tag
def switch_to_exercise(driver):
    pass

#todo 写判断题逻辑
def kill_judge(title_ele, ans_eles):
    pass

#todo 写多选题逻辑
def kill_muti_choice(title_ele, ans_eles):
    pass

#todo 获取元素文字内容
def get_text(ele):
    pass

#todo 比较哪个为正确答案逻辑，返回序号
def compare_to_ans()->int:
    pass

if __name__ == '__main__':
    print(query_ans('【单选题】（）属于纪实感很强的电影。'))
    # driver = webdriver.Firefox()
    # login(driver)
    # _ = get_all_exercises(driver)

    # errorname_lst = []
    # while True:
    #     todo_ele_lst = get_all_exercises(driver)
    #     ele = todo_ele_lst[0]


