# -*- coding:utf-8 -*- 
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import time
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By


def watch_video(x,driver,all_course):
    all_course[x].click()
    time.sleep(10)#不能简单用sleep可能网络不太好
    # try:
    #     WebDriverWait(driver,30).until(EC.frame_to_be_available_and_switch_to_it((By.ID,'iframe')))
    #     print('加载完成')
    # finally:
    wrong_list=None
    try:
        driver.switch_to.frame('iframe')
        driver.switch_to.frame(driver.find_element_by_class_name('ans-insertvideo-online'))
        video=driver.find_element_by_id('video')
        video.click()
        ActionChains(driver).move_to_element(video).perform()
        random_choice=0
        time.sleep(10)
        begin_time=time.time()
        find_time_object=driver.find_elements_by_class_name('vjs-duration-display')
        print(find_time_object)
        print(find_time_object[0])
        print(find_time_object[0].is_displayed())#确实被隐藏了，注意是个list
        find_time=find_time_object[0].get_attribute('textContent')#获取隐藏元素
        m, s = find_time.strip().split(":")
        m=int(m)
        print(m)
        s=int(s)
        end_time=time.time()+60*(m+2)
        question=None
        print(end_time-time.time())
        while time.time()<end_time:
            try:
                question=driver.find_element_by_class_name('ans-videoquiz-title')
            except Exception as e:
                pass
            if question!=None:
                ans=driver.find_elements_by_class_name('ans-videoquiz-opt')
                ans[random_choice%2].click()
                submit=driver.find_element_by_class_name('ans-videoquiz-submit')
                random_choice+=1
                question=None
            time.sleep(20)
    except Exception as e:
        print(e)
        print(str(x)+'出错')
        wrong_list=x
    driver.switch_to.default_content()#回到主frame
    return driver,wrong_list

if __name__=='__main__':
    url = 'https://mooc1-1.chaoxing.com/mycourse/studentstudy?chapterId=127091078&courseId=201743061&clazzid=4302016&enc=e200b5108777a46d8908d5e8bccf937f'#填登陆后课程界面url
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(30)#输入账号密码的时间
    driver.maximize_window()
    # print(driver.get_cookies())
    all_course = driver.find_elements_by_class_name('ncells')
    print(all_course)
    course_len=len(all_course)
    i=24
    wrong_list=[]
    while i<=course_len:
        driver,wl=watch_video(i,driver,all_course)
        if wl:
            wrong_list.append(wl)
        i+=1
    while True:
        if wrong_list:
            for item in wrong_list:
                item=int(item)
                driver,wl=watch_video(item,driver,all_course)
                if wl:
                    wrong_list.append(wl)
                else:
                    wrong_list.remove(item)
        else:
            print('---------------------all done------------------')
            break

# headers={
# 'Host': 'mooc1-1.chaoxing.com',
# 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
# 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
# 'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
# 'Accept-Encoding': 'gzip, deflate, br',
# 'Cookie': 'fid=1924; _uid=78686572; uf=b2d2c93beefa90dc9c9035182dd8c3554f0c5b39610c07406cf36d3a947e6f87a4d78b2270b1d3259d8de331baf9c44dc49d67c0c30ca5047c5a963e85f110990a3f4b20137d0760ce71fc6e59483dd3c518c95084e771fd2fa51da0f72104b89e349e167d408b2a; _d=1539249955005; UID=78686572; vc=AD09EDB5EC01D1DF1CA3456019FEEE3F; vc2=22BAA769474148E051984BA8624388CF; DSSTASH_LOG=C_38-UN_238-US_78686572-T_1539249955005; thirdRegist=0; rt=-1; tl=0; k8s=8fac0495dc2644c5d841528b561109868510d03c; __dxca=d1e2c46c-bf51-4ef4-9ae0-043078693bb7; jrose=C1AC141A1F1B1AA1B6FCC63894B67D88.mooc-3265293574-sf4jj; route=7aaebcbdcf7cf94856c7fb5f82d77b4b; k8s-ed=afc6a7a92849717ff27e5598f9206251e076cce1'
# }
#
# cookies=[
# {'name': 'k8s',
#  'value': '8a9dca9a1b3345b89fab64400f7d23a5819c4b99',
#  'path': '/',
#  'domain': 'mooc1-1.chaoxing.com',
#  'secure': False,
#  'httpOnly': True},
#     {'name': '__dxca',
#      'value': 'fededaef-da77-46c2-a0dc-68d1051b683d',
#      'path': '/', 'domain': 'mooc1-1.chaoxing.com',
#      'secure': False, 'httpOnly': False, 'expiry': 1633870851},
#     {'name': 'jrose', 'value': '634117E86BC9E72C8DE2F9BE7D2EE90E.mooc-3265293574-pg000',
#      'path': '/', 'domain': 'mooc1-1.chaoxing.com', 'secure': True, 'httpOnly': True},
#     {'name': 'route', 'value': '7aaebcbdcf7cf94856c7fb5f82d77b4b', 'path': '/',
#      'domain': 'mooc1-1.chaoxing.com', 'secure': False, 'httpOnly': False},
#     {'name': 'fid', 'value': '1924', 'path': '/', 'domain': '.chaoxing.com', 'secure': False,
#      'httpOnly': False, 'expiry': 1541854875},
#     {'name': '_uid', 'value': '78686572', 'path': '/', 'domain': '.chaoxing.com', 'secure': False, 'httpOnly': False, 'expiry': 1541854875}, {'name': 'uf', 'value': 'b2d2c93beefa90dc97110b15199892d8a6e37636162a26271bfd6b0f12b8f504bd219da1209c546aa6676ac7084751f7d807a544f7930b6abeaaa6286f1f1754db7125af630ddfbbfd68be96b6183b1a65d6ba3b8314d6ee3ce0dde87a8cdc4319ce30a066caa6ff', 'path': '/', 'domain': '.chaoxing.com', 'secure': False, 'httpOnly': False, 'expiry': 1541854875}, {'name': '_d', 'value': '1539262875455', 'path': '/', 'domain': '.chaoxing.com', 'secure': False, 'httpOnly': False, 'expiry': 1541854875},
#     {'name': 'UID', 'value': '78686572', 'path': '/', 'domain': '.chaoxing.com', 'secure': False, 'httpOnly': False, 'expiry': 1541854875},
#     {'name': 'vc', 'value': 'AD09EDB5EC01D1DF1CA3456019FEEE3F', 'path': '/', 'domain': '.chaoxing.com', 'secure': False, 'httpOnly': True, 'expiry': 1541854875},
#     {'name': 'vc2', 'value': '22BAA769474148E051984BA8624388CF', 'path': '/', 'domain': '.chaoxing.com', 'secure': False, 'httpOnly': True, 'expiry': 1541854875},
#     {'name': 'DSSTASH_LOG', 'value': 'C_38-UN_238-US_78686572-T_1539262875455', 'path': '/', 'domain': '.chaoxing.com', 'secure': False, 'httpOnly': False, 'expiry': 1541854875},
#     {'name': 'k8s-ed', 'value': 'afc6a7a92849717ff27e5598f9206251e076cce1', 'path': '/', 'domain': 'mooc1-1.chaoxing.com', 'secure': False, 'httpOnly': True}]
## time.sleep(20)
# print(driver.get_cookies())
# driver.add_cookie(cookies)

# for item in cookies:
#     driver.add_cookie(item)

# driver.add_cookie({'name':'_uid', 'value':78686572,"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False})
# driver.add_cookie({'name':'fid', 'value':1924,"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,})
# driver.add_cookie({'name':'UID', 'value':78686572,"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,})
# driver.add_cookie({'name':'DSSTASH_LOG', 'value':'C_38-UN_238-US_78686572-T_1539258544213',"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,})
# driver.add_cookie({'name':'__dxca', 'value':'5f4d702e-a0e6-4c0e-baee-869d146d1ee7',"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,})
# driver.add_cookie({'name':'_d', 'value':1539258544213,"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,})
# driver.add_cookie({'name':'uf', 'value':'b2d2c93beefa90dc97110b15199892d8a6e37636162a26271bfd6b0f12b8f504ced5a1aed728430ea7136d25ac4b7749d807a544f7930b6abeaaa6286f1f1754db7125af630ddfbbfd68be96b6183b1a65d6ba3b8314d6ee32f055f2c5a78e59d77489aac558a9a7',"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,})
# driver.add_cookie({'name':'vc', 'value':'AD09EDB5EC01D1DF1CA3456019FEEE3F',"expires": "",
#     'path': '/',
#     'httpOnly': True,
#     'HostOnly': False,
#     'Secure': False,})
# driver.add_cookie({'name':'vc', 'value':'AD09EDB5EC01D1DF1CA3456019FEEE3F',"expires": "",
#     'path': '/',
#     'httpOnly': True,
#     'HostOnly': False,
#     'Secure': False,})
# driver.add_cookie([
#     {'name':'_uid', 'value':78686572,"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False}
#     ,{'name':'fid', 'value':1924,"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,}
#     ,{'name':'UID', 'value':78686572,"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,}
#     ,{'name':'DSSTASH_LOG', 'value':'C_38-UN_238-US_78686572-T_1539258544213',"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,}
#     ,{'name':'__dxca', 'value':'5f4d702e-a0e6-4c0e-baee-869d146d1ee7',"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,}
#     ,{'name':'_d', 'value':1539258544213,"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False,}
#     ,{'name':'uf', 'value':'b2d2c93beefa90dc97110b15199892d8a6e37636162a26271bfd6b0f12b8f504ced5a1aed728430ea7136d25ac4b7749d807a544f7930b6abeaaa6286f1f1754db7125af630ddfbbfd68be96b6183b1a65d6ba3b8314d6ee32f055f2c5a78e59d77489aac558a9a7',"expires": "",
#     'path': '/',
#     'httpOnly': False,
#     'HostOnly': False,
#     'Secure': False}
#     ,{'name':'vc', 'value':'AD09EDB5EC01D1DF1CA3456019FEEE3F',"expires": "",
#     'path': '/',
#     'httpOnly': True,
#     'HostOnly': False,
#     'Secure': False},
#     {'name':'vc', 'value':'AD09EDB5EC01D1DF1CA3456019FEEE3F',"expires": "",
#     'path': '/',
#     'httpOnly': True,
#     'HostOnly': False,
#     'Secure': False}])
# driver.get(url)
