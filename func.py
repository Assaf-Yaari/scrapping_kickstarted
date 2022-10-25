from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import concurrent.futures
import pandas as pd 
import random
import time



def reward_data(urladress):
    global scrap_info
    scrap_info = [["div","pledge__info" ,reward_num_func] ,["span","money" ,reward_median_func]]
    start_threads(download_url,urladress)
    # intial_list = pd.read_csv('temp2.csv' , delimiter=',')
    # start_threads(scrapper2,intial_list['reward_html'])

def scrapper2(html_list):
    re_list =[[html_list[0][0]]]
    soup = BeautifulSoup(html_list[0][1], "html.parser")
    for x in scrap_info:
        job_elements = soup.find_all(x[0], class_= x[1])
        end_game = x[2](job_elements)
        re_list[0].append(end_game)
    reward_df = pd.DataFrame(columns =['reward_url','reward_num','reward_median'],data=re_list)
    # live_links = pd.DataFrame(columns =['reward_url'],data=[html_list[0][0]])
    # live_links.to_csv('livelinks.csv', mode='a', encoding='utf-8', index=False ,header=False)
    reward_df.to_csv('livelinks.csv',columns=['reward_url'] ,mode='a', encoding='utf-8', index=False ,header=False)
    reward_df.to_csv('reward_data.csv' ,mode='a', encoding='utf-8', index=False ,header=False)
    

def tor_proxy ():
    session = requests.session()
    session.proxies = {}
    session.proxies['http'] = 'socks5h://localhost:9050'
    session.proxies['https'] = 'socks5h://localhost:9050'
    return session
 
def start_threads(func,urladress):
    '''global user_agents
    global good_agents
    user_agents = pd.read_csv('user_agents.csv')
    good_agents = pd.read_csv('good_agents.csv')'''
    MAX_THREADS = 30
    threads = min(MAX_THREADS, len(urladress))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        try:
            executor.map(func,urladress)
        except:
            executor.shutdown()
            random.seed(300)
            time.sleep(random.random())
            checkpoint = pd.read_csv('livelinks.csv')
            new_adressess = np.where(checkpoint['reward_url'] != urladress)
            start_threads(func,new_adressess)
    

def download_url(adress): 
    page = req_restart(adress)
    if(page[0][1] !='0'):
        scrapper2(page)
    else:
        dead_links = pd.DataFrame(columns =['reward_url','reward_html'],data=page)
        dead_links.to_csv('badlinks.csv', mode='a', encoding='utf-8', index=False ,header=False)

def req_restart(adress):
    ln = [[adress]]
    random.seed(4)
    time.sleep(random.random())
    proxy= tor_proxy()
    page = proxy.get(adress)
    soup = BeautifulSoup(page.content , "html.parser")
    dtd_hack = len(soup.find_all('div', class_="NS_projects__rewards_section"))
    error_handelling = ['301','401','403','404','408','429','503']
    if (dtd_hack != 0 and page.status_code not in error_handelling):
        ln[0].append(page.text) 
        good_agents = pd.DataFrame(columns =['agent'],data=['agent'])
        good_agents.to_csv('good_agents.csv', mode='a', encoding='utf-8', index=False ,header=False)
    else:
        ln[0].append('0')
        raise Exception('botched user')
    return ln 
        

def reward_median_func(reward_list):
    amounts_only = 0
    if(len(reward_list)!= 0):
        amounts_only = re.sub('[^0-9]','', reward_list[int(len(reward_list) / 2)].text)
    return amounts_only

def reward_num_func(reward_list):
    return len(reward_list)

''''''
        
def word_count(blurb_list):
    word_list =[]
    for blurb_index in blurb_list:
        word_list.append(len(str(blurb_index).split()))
    return word_list

def media_num(urladress):
    num_media_list = []
    for adress in urladress:
        task_element = scrapper2(adress,"img","fit lazyloaded")
        task_element2 = scrapper2(adress,"img","fit js-lazy-image")
        num_media_list.append(len(task_element) + len(task_element2) )
    return num_media_list

    
    