# -*- coding:utf-8 -*- 
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 18161712640
# gaizuodeshi0108

def watch_video(x,driver,all_course):
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
    url = 'https://mooc1-1.chaoxing.com/mycourse/studentstudy?chapterId=127091078&courseId=201743061&clazzid=4302016&enc=e200b5108777a46d8908d5e8bccf937f'#填登陆后课程界面url
    driver = webdriver.Firefox()
    driver.get(url)
    # time.sleep(30)#输入账号密码的时间
    all_course = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ncells")))
    driver.maximize_window()
    course_len=len(all_course)
    print("总共"+str(course_len)+"节课")
    i=51#开始课程序号
    wrong_list=[]

    print("第一遍执行刷课")
    for i in [20,21,23,27,32,34,37]:
        print("执行"+str(i)+"的当前driver")
        print(driver)

        try:
            all_course= WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ncells")))
            #出错原因怀疑是all_course太长，缓存不够，所以重新获取一次
            driver,wl=watch_video(i,driver,all_course)
        except Exception as e:
            print(str(i)+"出错")
            # print(e)
            print("======================================")
            wl=i
        if wl:
            try:
                driver.refresh()
            except:
                print("可能断网了")
                print("此时出错列表")
                print(wrong_list)
            all_course= WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ncells")))
            wrong_list.append(wl)
        i+=1

    print("回刷出错课程")
    while True:
        print('剩余出错课程：')
        print(wrong_list)
        if wrong_list:
            for item in wrong_list:
                item=int(item)
                try:
                    all_course = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"ncells")))
                    driver, wl = watch_video(item, driver, all_course)
                except Exception as e:
                    print(str(item) + "出错")
                    # print(e)
                    print("======================================")
                    wl = item
                if wl:
                    driver.refresh()
                    wrong_list.append(wl)
                else:
                    wrong_list.remove(item)
        else:
            print('---------------------all done------------------')
            break

