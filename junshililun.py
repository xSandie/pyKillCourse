# -*- coding:utf-8 -*- 
import os

from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import configparser
from contextlib import contextmanager
# 获取配置，全局都要用到
# 项目路径
root_dir = os.path.split(os.path.realpath(__file__))[0]
# config.ini文件路径
config_filepath = os.path.join(root_dir, 'config1.ini')
config = configparser.ConfigParser()
config.read(config_filepath, encoding='utf-8')

#切换到视频播放器frame
@contextmanager
def enter_iframe(driver):
    driver.switch_to.frame('iframe')
    video_iframe = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((
        By.CLASS_NAME, str(config.get('cls', 'video_frame')))))[0]#等待30秒直到能切换进iframe
    driver.switch_to.frame(video_iframe)
    yield
    driver.switch_to.default_content()

#尝试获取元素
@contextmanager
def attempt_get():
    try:
        yield
    except Exception as e:
        pass

#进行登陆
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
    ret_dic = {}#以字典形式返回，包括课程目录，需特殊对待的课程
    driver.maximize_window()  # 最大化窗口，方便定位和点击（headless模式下不需要）

    temp_courses = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((
        By.CLASS_NAME, config.get('cls', 'courses_total'))))#等待30秒，直到课程目录出现，但是出现后页面还是会被js刷新
    time.sleep(10)  # 页面加载js时间
    all_courses = driver.find_elements_by_class_name(config.get('cls', 'courses_total'))
    # 待刷的所有课程
    ret_dic['unfinishedname_lst'] = []
    for course in all_courses:
        indicator = course.find_element_by_class_name(config.get('cls', 'circle_indicator')).text.strip()
        c_name = get_course_name(course)
        if indicator == '2' and c_name != config.get('courses', 'exception1'):
            ret_dic['unfinishedname_lst'].append(course)

    courses_tree = driver.find_element_by_class_name(config.get('cls', 'courses_tree'))#获得课程目录树
    all_divs = courses_tree.find_elements_by_tag_name('div')#所有后代div 有单元有课程
    ret_dic['have_goal_text'] = []  # 找到所有具有学习目标的课程，需特殊对待
    ret_dic['normal_text'] = []#用于刷正常课
    for div in all_divs:
        if div.get_attribute('class') == config.get('cls', 'section'):#是单元
            have_goal_ele = div.find_element_by_class_name(config.get('cls', 'courses_total'))#此单元中含有学习目标的课程webelement
            ele_name = get_course_name(have_goal_ele)
            ret_dic['have_goal_text'].append(ele_name)
        elif div.get_attribute('class') == config.get('cls', 'courses_total'):#是正常课程
            ele_name = get_course_name(div)
            ret_dic['normal_text'].append(ele_name)
    todo_ele_lst = ret_dic['unfinishedname_lst']
    normal_lst = ret_dic['normal_text']
    abnormal_lst = ret_dic['have_goal_text']
    time.sleep(3)#等待页面刷新，免得元素过期
    return todo_ele_lst, normal_lst, abnormal_lst


def show_abnormal_video(course_ele, driver):
    time.sleep(3)
    course_ele.click()
    video_ele = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, config.get('cls', 'video_btn'))))
    video_ele[0].click()
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.ID, 'iframe')))


def show_normal_video(course_ele, driver):
    '''
    从正常元素中得到可点击的视频
    :param course_ele: 可点击的课程目录标题
    :param driver: 在主frame的driver
    '''
    time.sleep(3)
    course_ele.click()
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.ID, 'iframe')))
    driver.switch_to.parent_frame()


#todo 开始看视频
def watch_video(driver):
    video_start_btn = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, str(config.get('cls','head_play_btn')))))[0]
    video_start_btn.click()
    video = driver.find_element_by_tag_name('video')
    ActionChains(driver).move_to_element(video).perform()
    time.sleep(3)
    begin_time = time.time()
    with attempt_get():#todo 改成while True
        time_object = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, str(config.get('cls','duration')))))[0]
        find_time = time_object.get_attribute('textContent')  # 获取隐藏元素
        if find_time == 0:
            time.sleep(30)  # 如果还没获取到，再等半分钟
            find_time = time_object.get_attribute('textContent')  # 获取隐藏元素
        minutes, _ = find_time.strip().split(":")
        minutes = int(minutes)
        end_time = begin_time + 60 * (minutes + 2)
        print('视频时长：'+str(minutes)+'分钟')
        while time.time() < end_time:
            with attempt_get():
                question = driver.find_element_by_class_name(str(config.get('cls','quiz')))
                if question != None:
                    QA(driver)
            video = driver.find_element_by_tag_name('video')
            ActionChains(driver).move_to_element(video).perform()
            time.sleep(10)#每10秒移上一次






#todo 做视频中的题目
def QA(driver):
    single_quiz(driver)
    pass
#todo 做视频中的单选
def single_quiz(driver):
    random_choice = 0
    ans_length = 0
    try:
        while True:
            ans = driver.find_elements_by_name(str(config.get('name','ans_opt')))
            ans_length = len(ans)
            ans[random_choice].click()
            submit = driver.find_element_by_class_name(str(config.get('cls','quiz_submit')))
            submit.click()
            random_choice += 1  # 随机选一个
            time.sleep(2)#睡两秒再做
    except Exception as e:
        if random_choice >= ans_length:
            raise Exception()#如果单选选大于选项数量次还没选中，抛出异常
        pass

#todo 多选题
def muti_quiz():
    pass

#todo 做课程后的题目
def course_quiez():
    pass

def watch_video_legacy(x,driver,all_course):
    all_course[x].click()
    time.sleep(10)  # 不能简单用sleep可能网络不太好
    wrong_list = None
    driver.switch_to.frame('iframe')
    driver.switch_to.frame(driver.find_element_by_class_name('ans-insertvideo-online'))
    try:
        # try:
        # WebDriverWait(driver,30).until(EC.frame_to_be_available_and_switch_to_it((By.ID,'iframe')))
        # print('加载完成')
        # finally:
        video=driver.find_element_by_id('video')
        video.click()
        ActionChains(driver).move_to_element(video).perform()
        random_choice=0
        time.sleep(10)
        begin_time=time.time()
        find_time_object=driver.find_elements_by_class_name('vjs-duration-display')
        # print(find_time_object)
        # print(find_time_object[0])
        # print(find_time_object[0].is_displayed())#确实被隐藏了，注意是个list
        find_time=find_time_object[0].get_attribute('textContent')#获取隐藏元素

        if find_time==0:
            time.sleep(30)#如果还没获取到，再等半分钟
            find_time = find_time_object[0].get_attribute('textContent')  # 获取隐藏元素

        m, s = find_time.strip().split(":")
        m=int(m)
        s=int(s)
        end_time=begin_time+60*(m+2)
        question=None
        print(end_time-time.time())
        while time.time()<end_time:
            try:
                question=driver.find_element_by_class_name('ans-videoquiz-title')
            except Exception as e:
                pass
            if question!=None:
                ans=driver.find_elements_by_name('ans-videoquiz-opt')
                print("尝试第"+str(random_choice+1)+"次做题")
                ans[random_choice].click()
                submit=driver.find_element_by_class_name('ans-videoquiz-submit')
                submit.click()
                random_choice+=1#随机选一个
                if random_choice >= 4:
                    print('第'+str(x)+'是多选')
                    wrong_list=x
                    break
                question=None
                try:
                    driver.switch_to.default_content()
                    # wrong_ans=driver.switch_to.alert
                    # time.sleep(1)
                    # if wrong_ans:
                    #     print('得到wrong_ans对象,回答错误')
                    #     wrong_ans.accept()
                    #     print('已点击确认')
                except:
                    driver.switch_to.default_content()#尝试卡bug
                    pass
                #切换frame
                driver.switch_to.frame('iframe')
                driver.switch_to.frame(driver.find_element_by_class_name('ans-insertvideo-online'))
            #中间要是暂停了就继续播放
            if driver.find_elements_by_class_name('vjs-paused'):
                video.click()
                ActionChains(driver).move_to_element(video).perform()

            time.sleep(20)
        print(str(x)+'看完')
        print("======================================")

    except Exception as e:
        # print(e)
        print("第"+str(x)+'出错'+"====极可能是答题块内部出错")
        wrong_list=x
    driver.switch_to.default_content()#回到主frame
    # time.sleep(1)
    return driver,wrong_list

if __name__=='__main__':
    driver = webdriver.Firefox()
    login(driver)
    todo_ele_lst, normal_lst, abnormal_lst = get_all_courses(driver)
    errorname_lst = []
    while True:
        # time.sleep(5)  # 等待刷新完成
        todo_ele_lst, normal_lst, abnormal_lst = get_all_courses(driver)
        print('待刷课程：' + str(len(todo_ele_lst)) + '个')
        ele = todo_ele_lst[0]#每次取最早的没刷的
        time.sleep(5)  # 等待刷新完成
        c_name = get_course_name(ele)
        if c_name in abnormal_lst:#不能使用正常方法刷
            show_abnormal_video(ele, driver)
            with enter_iframe(driver):
                watch_video(driver)
        elif c_name in normal_lst:#能用正常方法刷
            show_normal_video(ele, driver)
            with enter_iframe(driver):
                watch_video(driver)
        # if not errorname_lst:
        #     break
    # time.sleep(30)#输入账号密码的时间
    # all_course = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ncells")))
    # driver.maximize_window()
    # course_len=len(all_course)
    # print("总共"+str(course_len)+"节课")
    # i=51#开始课程序号
    # wrong_list=[]

    # print("第一遍执行刷课")
    # for i in [20,21,23,27,32,34,37]:
    #     print("执行"+str(i)+"的当前driver")
    #     print(driver)
    #
    #     try:
    #         all_course= WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ncells")))
    #         #出错原因怀疑是all_course太长，缓存不够，所以重新获取一次
    #         driver,wl=watch_video(i,driver,all_course)
    #     except Exception as e:
    #         print(str(i)+"出错")
    #         # print(e)
    #         print("======================================")
    #         wl=i
    #     if wl:
    #         try:
    #             driver.refresh()
    #         except:
    #             print("可能断网了")
    #             print("此时出错列表")
    #             print(wrong_list)
    #         all_course= WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ncells")))
    #         wrong_list.append(wl)
    #     i+=1
    #
    # print("回刷出错课程")
    # while True:
    #     print('剩余出错课程：')
    #     print(wrong_list)
    #     if wrong_list:
    #         for item in wrong_list:
    #             item=int(item)
    #             try:
    #                 all_course = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"ncells")))
    #                 driver, wl = watch_video(item, driver, all_course)
    #             except Exception as e:
    #                 print(str(item) + "出错")
    #                 # print(e)
    #                 print("======================================")
    #                 wl = item
    #             if wl:
    #                 driver.refresh()
    #                 wrong_list.append(wl)
    #             else:
    #                 wrong_list.remove(item)
    #     else:
    #         print('---------------------all done------------------')
    #         break

