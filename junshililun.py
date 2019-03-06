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

#切换frame
@contextmanager
def enter_iframe(driver):
    driver.switch_to.frame('iframe')
    yield
    driver.switch_to.parent_frame()

#进行登陆
def login(driver):
    login_url = config.get('account', 'url')
    ac = config.get('account', 'account')
    pswd = config.get('account', 'password')
    driver.get(login_url)
    driver.find_element_by_name('uname').send_keys(ac)
    driver.find_element_by_name('password').send_keys(pswd)

#todo 获得所有课程，数据结构还需要确定。
def get_all_courses(driver):
    ret_dic = {}#以字典形式返回，包括课程目录，需特殊对待的课程
    driver.maximize_window()  # 最大化窗口，方便定位和点击（headless模式下不需要）
    all_courses = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((
        By.CLASS_NAME, config.get('cls', 'courses_total'))))#等待30秒，直到课程目录出现
    courses_tree = driver.find_element_by_class_name(config.get('cls', 'courses_tree'))#获得课程目录树
    all_divs = courses_tree.find_elements_by_tag_name('div')#所有后代div 有单元有课程
    ret_dic['have_goal_text'] = []  # 找到所有具有学习目标的课程，需特殊对待
    ret_dic['have_goal_eles'] = []  # 找到所有具有学习目标的课程，需特殊对待
    ret_dic['normal_text'] = {}#用于刷正常课
    section_name = ''#单元名，会被覆盖
    for div in all_divs:
        if div.get_attribute('class') == config.get('cls', 'section'):#是单元
            section_name = div.find_element_by_class_name(config.get('cls', 'section_name')).text.strip()#单元名
            have_goal_ele = div.find_element_by_class_name(config.get('cls', 'courses_total'))#此单元中含有学习目标的课程webelement
            ret_dic['have_goal'].append(have_goal_ele.text.strip())
            ret_dic['have_goal_eles'].append(have_goal_ele)#特殊对待的元素
        elif div.get_attribute('class') == config.get('cls', 'courses_total'):#是正常课程
            if div.text.strip() in ret_dic['have_goal']:
                pass
            else:
                ret_dic['normal_eles'][section_name].append(div)

    normal_eles = ret_dic['normal_eles']
    abnormal_eles = ret_dic['have_goal_eles']
    ret_dic['finishedname_lst'] = []#已完成刷课的课程，标题名
    ret_dic['errorname_lst'] = []#出错的课程，标题名
    ret_dic['unfinishedname_lst'] = []#未完成的课程，标题名
    return ret_dic

#todo 通过课程名找到开始的序号
def find_start_index(course_name,):
    pass
#todo 开始刷课
def watch_video(driver, course_name, normal_courses, abnormal_courses):
    pass

#todo 做视频中的题目
def video_quiez():
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
        print(m)
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
    courses_dic = get_all_courses(driver)
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

