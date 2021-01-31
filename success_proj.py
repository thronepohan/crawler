# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def getValidStr(object):
    if(object != None):
        return object.text
    else:
        return ''


inputUrl = input('Enter url: ')
outputFileName = input('Enter file name: ')

options = Options()
options.add_argument("--disable-notifications")

chrome = webdriver.Chrome('./chromedriver', chrome_options=options)
chrome.get(inputUrl)

button = chrome.find_elements_by_class_name("btn.fDark.btn-block.btn-more")
chrome.execute_script("$('.btn-more').click()")

for i in range(1, 150):
    chrome.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(0.5)
soup = BeautifulSoup(chrome.page_source)

mainPageHandle = chrome.current_window_handle

projectList = []
for block in soup.select('.projectCard'):
    projectList.append(block)

allList = []
cnt = 0
total = len(projectList)
for project in projectList:
    oneList = []

    cnt = cnt + 1
    print('%d/%d' %(cnt, total))
    # if(cnt == 20):
    #     break
    ### check status
    success = project.find(class_= 'tag red')
    endDate = getValidStr(project.find(class_= 'date pull-right'))
    dateStr= '已結束'
    if(success == None):
        print('未成功')
        continue
    if(endDate != dateStr):
        print('未結束')
        continue

    projectUrl = project.find('a', {'class': 'projectUrl'})
    #content = project.find('div', {'class': 'pcontent'})
    title = getValidStr(project.find('h2', {'class': 'title'}))
    creator = getValidStr(project.find('p', {'class': 'creator'}).a)
    goalMoney = getValidStr(project.find('span', {'class': 'goalMoney'}))
    percent = getValidStr(project.find('span', {'class': 'hidden-md goalpercent goal'}))
    # print(title, creator)
    
    # js = 'window.open("%s");' % projectUrl['href']
    # chrome.execute_script(js)
    # ### Sub page operation ###
    # subPageHandle = chrome.current_window_handle
    # handles = chrome.window_handles

    # subPageHandle = None
    # for handle in handles:
    #     if handle != mainPageHandle:
    #         subPageHandle = handle

    # chrome.switch_to.window(subPageHandle)
    # time.sleep(0.1)
    # chrome.execute_script("$('.videoBlock').click()")
    
    ### open project html
    response = requests.get(projectUrl['href'])
    projectSoup = BeautifulSoup(response.text, 'lxml')
    
    # print(projectSoup)
    ### start time & end time ###
    timeRaw = projectSoup.find(class_='success')
    if(timeRaw == None):
        print(projectUrl['href'])
        continue
    m = re.findall(r'\d{4}/\d{1,2}/\d{1,2}', timeRaw.text)
    startTime = m[0]
    endTime = m[1]
    #print(m[0], m[1])

    # videoSoup = BeautifulSoup(chrome.page_source, 'lxml')
    # videoDuration = videoSoup.find(class_='videoFrame').iframe['src']#.find(class_='ytp-time-duration')
    # ytSoup = BeautifulSoup(videoDuration, 'lxml')
    # dur = ytSoup.find
    # print(videoDuration)


    ### external websites ###
    urlFB = ''
    urlWeb = ''
    detail = projectSoup.find(class_='creator-detail')
    
    if(detail.find(class_='creatorFanpage') != None):
        urlFB = detail.find(class_='creatorFanpage')['href']
    if(detail.find(class_='creatorWebsite') != None):
        urlWeb = detail.find(class_='creatorWebsite')['href']

    ### check img & video ###
    isImg = ''
    isVideo = ''
    story = projectSoup.find(class_= 'story')
    img = story.find('img')
    video = story.find(class_= 'fr-video fr-fvc fr-dvb fr-draggable')
    topVideo = projectSoup.find(class_= 'videoBlock')
    # videoYTSrcs = story.find_all(class_= 'ytp-cued-thumbnail-overlay')
    if(img != None):
        isImg = 'v'
    if(video != None or topVideo != None):
        isVideo = 'v'

    #title = projectSoup.find(class_='ptitle')
    #print(title.text)
    # commentsUrl = projectUrl['href'] + '/comments'
    totalPeople = getValidStr(projectSoup.find('div', {'class': 'numberRow totalPeople'}).h2)
    # progressMoney = getValidStr(projectSoup.find('p', {'class': 'metatext moneyFormat'}))
    progressMoney = re.findall("\d+", getValidStr(projectSoup.find('p', {'class': 'metatext moneyFormat'})))[0]
    # timeScope = project.find('div', {'class': 'col-sm-4 sidebar numberSidebar'}).blockquote.text
    #commentsUrl = projectSoup.find('a', {'class': 'commentNav '})
    #print(commentsUrl)
    offlineItems = projectSoup.find_all(class_='rewardItem offline')
    itemNum = len(offlineItems)

    

    progress = projectSoup.find(class_= 'postNav')
    freqQ = projectSoup.find(class_= 'faqNav')
    comments = projectSoup.find(class_= 'commentNav')

    progressNum = -1
    if(progress != None):
        progressResponse = requests.get(progress['href'])
        progressSoup = BeautifulSoup(progressResponse.text)
        time.sleep(0.1)
        goals = progressSoup.find(class_= 'postWrapper').find_all(class_= 'post post-goal')
        items = progressSoup.find(class_= 'postWrapper').find_all(class_= 'post post-item')
        progressNum = len(goals) + len(items)

    faqsNum = -1
    if(freqQ != None):
        freqQResponse = requests.get(freqQ['href'])
        freqQSoup = BeautifulSoup(freqQResponse.text)
        time.sleep(0.1)
        faqs = freqQSoup.find(class_= 'faqWrapper').find_all(class_= 'faq')
        faqsNum = len(faqs)

    commentsNum = -1
    if(comments != None):
        commentsResponse = requests.get(comments['href'])
        commentsSoup = BeautifulSoup(commentsResponse.text)
        time.sleep(0.1)
        commentsGroups = commentsSoup.find_all('div', {'class': 'comment-group'})
        commentsNum = len(commentsGroups)

    ### 商品名 提案者 目標金額 募到總金額 達成百分比 贊助總人數 留言人數 贊助方案數量
    oneList.append(title)
    oneList.append(creator)
    oneList.append(progressMoney)
    oneList.append(goalMoney)
    oneList.append(percent)
    oneList.append(totalPeople)
    oneList.append(startTime)
    oneList.append(endTime)
    oneList.append(urlFB)
    oneList.append(urlWeb)
    oneList.append(isImg)
    oneList.append(isVideo)
    # oneList.append(timeScope)
    oneList.append(faqsNum)
    oneList.append(commentsNum)
    oneList.append(progressNum)

    ### Cases ###
    oneList.append(itemNum)

    for offlineItem in offlineItems:
        ammount = offlineItem.find('div', {'class': 'number pull-left'})
        #print(ammount.text)
        number = offlineItem.find('div', {'class': 'meta-wrapper'}).find('p', {'class': 'meta-detail'})
        #print(number.text)
        container = offlineItem.find(class_= 'cardrow rewardMeta container-fluid').find(class_= 'meta-wrapper').find_all(class_= 'meta-item')
        sponsors = ''
        limit = ''
        expectTime = ''
        for c in container:
            label = c.find(class_= 'meta-label')
            detail = c.find(class_= 'meta-detail')
            if(label == None or detail == None):
                continue
            # print(type(label))
            str1 = '贊助人數'
            str2 = '限量'
            str3 = '預計寄送時間'
            if(label.text == str1):
                sponsors = detail.text
            elif(label.text == str2):
                limit = detail.text
            elif(label.text == str3):
                expectTime = detail.text
        
        content = offlineItem.find(class_= 'cardrow rewardDes')

        oneList.append(ammount.text)
        oneList.append(sponsors)
        oneList.append(expectTime)
        oneList.append(limit)
        oneList.append(content.text)
        
    
    # for commentsGroup in commentsGroups:
    #     print(commentsGroup)
    
    # print(itemNum)
    # print(commentsNum)
    allList.append(oneList)
    
    # chrome.close()
    # chrome.switch_to.window(mainPageHandle)

    # if(cnt == 3):
    #     break

test = pd.DataFrame(data=allList)
test.to_excel(outputFileName + '_success.xlsx', encoding='utf-8')

allList.clear()

chrome.quit()
