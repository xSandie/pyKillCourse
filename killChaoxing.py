# -*- coding:utf-8 -*- 
import itertools  # 排列组合
import os
import random

from selenium.webdriver.common.action_chains import ActionChains  # ActionChains是一个底层的自动交互的方法，例如鼠标移动、鼠标按键事件、键盘响应和菜单右击交互。
# 这些对于像悬停和拖拽这种复杂的行为很有用
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import configparser
from contextlib import contextmanager

# 获取配置，全局都要用到
# 项目路径
root_dir = os.path.split(os.path.realpath(__file__))[0]  # 按照路径将文件名和路径分割开
# config.ini文件路径
config_filepath = os.path.join(root_dir, 'config.ini')  # 路径拼接
config = configparser.ConfigParser()  # ConfigParser 是用来读取配置文件的包
config.read(config_filepath, encoding='utf-8-sig')


# 切换到视频播放器frame
@contextmanager  # 上下文管理器
def enter_video_iframe(driver):
    driver.switch_to.frame('iframe')  # 元素定位
    video_iframe = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((
        By.CLASS_NAME, str(config.get('cls', 'video_frame')))))[
        0]  # 等待30秒直到能切换进iframe '''判断某个元素是否被加到了dom树里，并不代表该元素一定可见，如果定位到就返回WebElement'''
    driver.switch_to.frame(video_iframe)
    yield
    driver.switch_to.default_content()


# 切换到阅读frame
def enter_art_iframe(driver):
    driver.switch_to.frame('iframe')  # 元素定位
    video_iframe = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((
        By.CLASS_NAME, str(config.get('cls', 'video_frame')))))[
        0]  # 等待30秒直到能切换进iframe '''判断某个元素是否被加到了dom树里，并不代表该元素一定可见，如果定位到就返回WebElement'''
    driver.switch_to.frame(video_iframe)
    yield
    driver.switch_to.default_content()


# 尝试获取元素
@contextmanager
def attempt_get():
    try:
        yield
    except Exception as e:
        pass


# 提示我可能有bug该调试了
def bugs_goup():
    import ctypes
    player = ctypes.windll.kernel32
    player.Beep(2000, 5000)  # 发出蜂鸣，2000hz，5s


# 进行登陆
def login(driver):
    login_url = config.get('account', 'url')
    ac = config.get('account', 'account')
    pswd = config.get('account', 'password')
    driver.get(login_url)
    driver.find_element_by_name('uname').send_keys(ac)
    driver.find_element_by_name('password').send_keys(pswd)


def get_course_name(ele):
    '''
    找到课程元素中的课程名称
    :param ele:包含课程名的那一个大div
    :return:
    name:课程名称
    '''
    name = ele.find_elements_by_tag_name('span')[-1].text.strip()
    return name


def get_all_courses(driver):
    '''
    获得所有课程
    :param driver:停留在主文档的driver
    :return:
    todo_ele_lst:待刷的课程
    normal_lst:使用正常逻辑刷就可以的课程
    abnormal_lst:不同于使用正常逻辑刷课的课程
    '''
    ret_dic = {}  # 以字典形式返回，包括课程目录，需特殊对待的课程
    driver.maximize_window()  # 最大化窗口，方便定位和点击（headless模式下不需要）

    temp_courses = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((
        By.CLASS_NAME, config.get('cls', 'courses_total'))))  # 等待30秒，直到课程目录出现，但是出现后页面还是会被js刷新
    time.sleep(10)  # 页面加载js时间
    all_courses = driver.find_elements_by_class_name(config.get('cls', 'courses_total'))
    # 待刷的所有课程
    ret_dic['unfinishedname_lst'] = []
    for course in all_courses:
        indicator = course.find_element_by_class_name(config.get('cls', 'circle_indicator')).text.strip()
        c_name = get_course_name(course)
        if indicator == '2' or config.get('courses', 'exception1') in c_name:
            ret_dic['unfinishedname_lst'].append(course)

    courses_tree = driver.find_element_by_class_name(config.get('cls', 'courses_tree'))  # 获得课程目录树
    all_divs = courses_tree.find_elements_by_tag_name('div')  # 所有后代div 有单元有课程
    ret_dic['have_goal_text'] = []  # 找到所有具有学习目标的课程，需特殊对待
    ret_dic['normal_text'] = []  # 用于刷正常课
    ret_dic['article'] = []  # 阅读课程
    for div in all_divs:
        if div.get_attribute('class') == config.get('cls', 'section'):  # 是单元
            have_goal_ele = div.find_element_by_class_name(
                config.get('cls', 'courses_total'))  # 此单元中含有学习目标的课程webelement
            ele_name = get_course_name(have_goal_ele)
            if config.get('courses', 'exception1') not in ele_name:
                ret_dic['have_goal_text'].append(ele_name)
        elif div.get_attribute('class') == config.get('cls', 'courses_total'):  # 是正常课程
            ele_name = get_course_name(div)
            if ele_name not in ret_dic['have_goal_text'] and  config.get('courses', 'exception1') not in ele_name:
                ret_dic['normal_text'].append(ele_name)
            elif config.get('courses', 'exception1') in ele_name:
                ret_dic['article'].append(ele_name)
    todo_ele_lst = ret_dic['unfinishedname_lst']
    normal_lst = ret_dic['normal_text']
    abnormal_lst = ret_dic['have_goal_text']
    article = ret_dic['article']
    time.sleep(3)  # 等待页面刷新，免得元素过期
    return todo_ele_lst, normal_lst, abnormal_lst, article


# 确认是否得用非常逻辑对待
def confirm_abnormal(driver):
    div = driver.find_element_by_class_name(str(config.get('cls', 'tab_bar')))
    span_lst = div.find_elements_by_tag_name('span')
    if len(span_lst) == 3:
        return True
    return False


# 点击课程
def click_c(course):
    course.click()
    time.sleep(5)


# 调出不正常课程
def show_abnormal_video(driver):
    video_ele = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, config.get('cls', 'video_btn'))))
    video_ele[0].click()
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.ID, 'iframe')))


# 调出正常课程
def show_normal_video(driver):
    '''
    从正常元素中得到可点击的视频
    :param course_ele: 可点击的课程目录标题
    :param driver: 在主frame的driver
    '''
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.ID, 'iframe')))
    driver.switch_to.parent_frame()


# todo 开始看视频
def watch_video(driver):
    video_start_btn = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, str(config.get('cls', 'head_play_btn')))))[0]
    video_start_btn.click()
    video = driver.find_element_by_tag_name('video')
    ActionChains(driver).move_to_element(video).perform()
    time.sleep(3)
    begin_time = time.time()
    with attempt_get():
        time_object = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, str(config.get('cls', 'duration')))))[0]
        find_time = time_object.get_attribute('textContent')  # 获取隐藏元素
        if find_time == 0:
            time.sleep(30)  # 如果还没获取到，再等半分钟
            find_time = time_object.get_attribute('textContent')  # 获取隐藏元素
        minutes, _ = find_time.strip().split(":")
        minutes = int(minutes)
        end_time = begin_time + 60 * (minutes + 2)
        print('视频时长：' + str(minutes) + '分钟')
        question = None
        while time.time() < end_time:
            with attempt_get():
                question = driver.find_element_by_class_name(str(config.get('cls', 'quiz')))
            if question != None:
                QA(driver)
            question = None
            video = driver.find_element_by_tag_name('video')
            if driver.find_elements_by_class_name(str(config.get('cls', 'pause'))):
                video.click()
                ActionChains(driver).move_to_element(video).perform()
            time.sleep(10)  # 每10秒移上一次
            ended = None
            with attempt_get():
                ended = driver.find_element_by_class_name(str(config.get('cls', 'ended_btn')))
            if ended:
                break


# todo 做视频中的题目
def QA(driver):
    title = driver.find_element_by_class_name(config.get('cls', 'quiz')).text.strip()
    if '多选' in title:
        muti_quiz(driver)
    else:
        single_quiz(driver)

# 做视频中的单选
def single_quiz(driver):
    random_choice = 0
    ans_length = 0
    last_ans_length = 1
    print('有单选')
    try:
        bugs_goup()
        while True:
            ans = driver.find_elements_by_name(str(config.get('name', 'ans_opt')))
            ans_length = len(ans)
            ans[random_choice].click()
            if ans_length != 0:
                last_ans_length = ans_length  # 防止出现关掉之后ans长度变成0的问题
            submit = driver.find_element_by_class_name(str(config.get('cls', 'quiz_submit')))
            submit.click()
            random_choice += 1  # 随机选一个
            with attempt_get():
                driver.switch_to.alert.accept()  # 关掉错误提示弹窗
            print('第' + str(random_choice) + '次做题')
            time.sleep(2)  # 睡两秒再做
    except Exception as e:
        if random_choice > last_ans_length:
            raise Exception()  # 如果单选选大于选项数量次还没选中，抛出异常
        pass


# todo 多选题
def muti_quiz(driver):
    ans_length = 0
    print('有多选')
    choose_indecator = 2  # 多选的选中数量指示器
    try:
        while True:
            ans = driver.find_elements_by_name(str(config.get('name', 'ans_opt')))
            ans_length = len(ans)
            all_choices = (i for i in range(0, ans_length + 1))  # 生成可选选项的序号列表【0，1，2，3】
            for choice in itertools.combinations(all_choices, choose_indecator):
                for opt in choice:
                    ans[opt].click()  # 选择选项
                submit = driver.find_element_by_class_name(str(config.get('cls', 'quiz_submit')))
                submit.click()  # 提交
                print('选' + str(choose_indecator) + '个选项'
                      + '，共' + str(ans_length) + '个选项，' +
                      '选中' + str(choice))
                for _ in range(4):
                    with attempt_get():
                        driver.switch_to.alert.accept()  # 关掉错误提示弹窗
            choose_indecator += 1  # 选更多的选项
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


# todo 做课程后的题目
def course_quiez():
    pass


# todo 切换tab
def switch_window(driver):
    cur_handle = driver.current_window_handle
    handles = driver.window_handles
    for handle in handles:
        if handle != cur_handle:
            next_handle = handle
    driver.switch_to.window(next_handle)
    time.sleep(10)


if __name__ == '__main__':
    driver = webdriver.Firefox()
    login(driver)
    todo_ele_lst, normal_lst, abnormal_lst, _ = get_all_courses(driver)
    errorname_lst = []
    while True:
        # time.sleep(5)  # 等待刷新完成
        todo_ele_lst, normal_lst, abnormal_lst, article_lst = get_all_courses(driver)
        print('待刷课程：' + str(len(todo_ele_lst)) + '个')
        ele = todo_ele_lst[0]  # 每次取最早的没刷的
        time.sleep(5)  # 等待刷新完成
        c_name = get_course_name(ele)
        if c_name in abnormal_lst:  # 不能使用正常方法刷
            click_c(ele.find_elements_by_tag_name('a')[0])
            if confirm_abnormal(driver):
                show_abnormal_video(driver)
                with enter_video_iframe(driver):
                    watch_video(driver)
            else:  # 其实并非异常课程，没有课程目标
                show_normal_video(driver)
                with enter_video_iframe(driver):
                    watch_video(driver)
        elif c_name in article_lst:
            js = 'window.open("' + str(config.get('account', 'article_url')) + '");'
            driver.execute_script(js)
            switch_window(driver)
            kill_article(driver)
        elif c_name in normal_lst:  # 能用正常方法刷
            click_c(ele.find_elements_by_tag_name('a')[0])
            show_normal_video(driver)
            with enter_video_iframe(driver):
                watch_video(driver)
        
        else:
            pass
