from selenium import webdriver
from bs4 import BeautifulSoup
#from selenium.webdriver.common.keys import Keys
#from openpyxl import *
import time
from selenium.webdriver.remote.utils import format_json
from selenium.common.exceptions import NoSuchElementException
from tkinter import *
from urllib.request import *
from operator import itemgetter

def srim(code):
    driver.get('https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd='+code+'&amp;target=finsum_more')

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    searchbutton = driver.find_element_by_css_selector("#cns_Tab21") #연간 버튼
    searchbutton.click()#클릭

    try:
        name = driver.find_element_by_xpath('//*[@id="pArea"]/div[1]/div/table/tbody/tr[1]/td/dl/dt[1]/span').text
        roe22=float(driver.find_element_by_xpath('/html/body/div/form/div[1]/div/div[2]/div[3]/div/div/div[14]/table[2]/tbody/tr[22]/td[7]/span').text)
        zabon=float(driver.find_element_by_xpath('/html/body/div/form/div[1]/div/div[2]/div[3]/div/div/div[14]/table[2]/tbody/tr[11]/td[6]/span').text.replace(",",""))
        zusiksu=driver.find_element_by_xpath('//*[@id="cTB11"]/tbody/tr[7]/td').text.replace(",","")
        zusiksum = driver.find_element_by_xpath('//*[@id="cTB11"]/tbody/tr[5]/td').text.replace(",","")

    except NoSuchElementException:
        print('추정치 없어서 과거값 사용.')
        searchbutton = driver.find_element_by_css_selector("#cns_Tab22")
        searchbutton.click()
        name = driver.find_element_by_xpath('//*[@id="pArea"]/div[1]/div/table/tbody/tr[1]/td/dl/dt[1]/span').text
        roe22_1=float(driver.find_element_by_xpath('/html/body/div/form/div[1]/div/div[2]/div[3]/div/div/div[14]/table[2]/tbody/tr[22]/td[5]/span').text)
        roe22_2=float(driver.find_element_by_xpath('/html/body/div/form/div[1]/div/div[2]/div[3]/div/div/div[14]/table[2]/tbody/tr[22]/td[4]/span').text)
        roe22_3=float(driver.find_element_by_xpath('/html/body/div/form/div[1]/div/div[2]/div[3]/div/div/div[14]/table[2]/tbody/tr[22]/td[3]/span').text)
        roe22=(roe22_1*3+roe22_2*2+roe22_3)/6
        zabon=float(driver.find_element_by_xpath('/html/body/div/form/div[1]/div/div[2]/div[3]/div/div/div[14]/table[2]/tbody/tr[11]/td[5]/span').text.replace(",",""))
        zusiksu=driver.find_element_by_xpath('//*[@id="cTB11"]/tbody/tr[7]/td').text.replace(",","")
        zusiksum = driver.find_element_by_xpath('//*[@id="cTB11"]/tbody/tr[5]/td').text.replace(",","")
    
    for i in range (30):
        if zusiksu[i] == '주':
            zusiksu = float(zusiksu[:i])
            break

    for i in range (10):
        if zusiksum[i] == '억':
            zusiksum = float(zusiksum[:i])
            break
    try:
        zagizusik=float(driver.find_element_by_css_selector('#cTB13 > tbody > tr.p_sJJ30 > td.line.num').text.replace(",",""))
    except NoSuchElementException:
        zagizusik=0

    calzusiksu = zusiksu-zagizusik
    nowp = zusiksum*100000000/zusiksu
    
    a=zabon*100000000
    r=a+a*(roe22*0.01-bit*0.01)/(bit*0.01)
    plusiic=(a*(roe22*0.01-bit*0.01))
    tenper=a+(plusiic*0.9/(1+bit*0.01-0.9))
    twper=a+(plusiic*0.8/(1+bit*0.01-0.8))
    srimwonp=r/calzusiksu
    gapratiop=(srimwonp-nowp)/nowp*100
    print('종목명 : ',name)
    print('현재주가 : ',nowp)
    print('srim(적정가) : ',r/calzusiksu,'원')
    print('1차 매수가, 1차 매도가 : ',tenper/calzusiksu)
    print('2차 매수가: ',twper/calzusiksu)
    print('괴리율 : ',gapratiop)
    print('=========================================')
    return name,gapratiop

def get_code(url):
    lis=[]
    with urlopen(url) as response:
        soup = BeautifulSoup(response, 'html.parser')
        #titl=soup.select('td.name a')  #업종 & 테마
        titl = soup.select('.tltle')    #황금선 & 거래량
        for i in titl:
            lis.append(i.get('href')[20:])
        return lis

def start(code):
    upzong=get_code(code)
    lis2up=[]
    for i in upzong:
        try:
            name,r=srim(i)
            lis2up.append([name,r])
            time.sleep(1)
        except:
            #데이터 부족
            print('이회사 에러')

    soonwe = sorted(lis2up, key=itemgetter(1),reverse=True)
    print(soonwe)


if __name__ == '__main__':
    driver = webdriver.Chrome('./chromedriver.exe')

    #회사채 구하기 bbb-까지가 투자로 분류(최소 투자등급에 해당하는 회사채 수익률)
    with urlopen('https://www.kisrating.com/ratingsStatistics/statics_spread.do') as response:
        soup = BeautifulSoup(response, 'html.parser')
        titl=soup.select('#con_tab1 > div.table_ty1 > table > tbody > tr:nth-child(11) > td:nth-child(8)')
        bit=float(titl[0].text)

    #테마,업종
    #start('https://finance.naver.com/sise/sise_group_detail.nhn?type=theme&no=149')
    
    #골드크로스
    start('https://finance.naver.com/sise/item_gold.nhn')
    
    #거래량 급증
    #start('https://finance.naver.com/sise/sise_quant_high.nhn?sosok=1')

    #개별종목
    #srim('014470')