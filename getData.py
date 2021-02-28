import re
import csv
import json
import time
import base64
import pickle
import requests
import urllib.request
from PIL import Image
from bs4 import BeautifulSoup



# 提交表单登录并获取cookie

def get_cookie_from_net(sno, pwd):

    url = 'http://card.sysu.edu.cn'
    # timestamp = int(time.time())
    login_html = s.get(url, headers=headers).text

    verif_img_url = "http://card.sysu.edu.cn/Login/GetValidateCode"
    verif_img_data = s.get(verif_img_url, headers=headers).content

    with open('card.jpg', 'wb') as f:
        f.write(verif_img_data)


    # 手动输入验证码
    img = Image.open('card.jpg')
    Image._show(img)
    verify_code = str(input("输入验证码："))

    # pwd base64加密
    npwd = base64.urlsafe_b64encode(pwd.encode()).decode().strip("=")

    # 构建表单
    payload = {'sno': sno,
                'pwd': npwd,
                'ValiCode': verify_code,
                'remember': '0',
                'uclass': '1',
                'json': "true"
                }
    print(payload)

    url = 'http://card.sysu.edu.cn/Login/LoginBySnoQuery'
    data = s.post(url, headers=headers, data=payload, verify=False)
    with open('cookies.sysu', 'wb') as f:
        cookiedict = requests.utils.dict_from_cookiejar(s.cookies)
        pickle.dump(cookiedict, f)
    '''
    这里可以用用户名进一步的验证是否登录成功
    '''
    # print(data.text)
    return s.cookies

# 从cookie文件获取cookie
def get_cookie_from_file():
    with open('cookies.sysu', 'rb') as f:
        cookiedict = pickle.load(f)
        cookies = requests.utils.cookiejar_from_dict(cookiedict)
    print("解析文件，成功提取cookis...")
    return cookies

# 获取account
def getaccount():
    accountPayload = {
        "json": "true"
    }
    accountUrl = "http://card.sysu.edu.cn/User/GetCardInfoByAccountNoParm"
    accountData = s.post(accountUrl, data=accountPayload, verify=False).json()
    account = json.loads(accountData['Msg'])['query_card']['card'][0]['account']
    return account


def getdata():
    dataHeaders = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/83.0",
            'Host': 'card.sysu.edu.cn',
            'Origin': 'http://card.sysu.edu.cn',
            'Referer': 'http://card.sysu.edu.cn/Page/Page',
            'X_REQUESTED_WITH': '5b3b1a369d8fb2e33514113a56809819f3d3db040ede8e6017952dac451983ee',
            'X-Requested-With': "XMLHttpRequest"
            }
    
    dataUrl = "http://card.sysu.edu.cn/Report/GetPersonTrjn"
    account = getaccount()
    dataPayload = {
        "sdate": "2019-01-01",
        "edate": "2021-01-05",
        "account": account,
        "page": "1",
        "rows": "100"
    }
    statusData = s.post(dataUrl, headers=dataHeaders, data=dataPayload, verify=True).json()
    totalAmount = statusData["total"]
    dataFile = open("data.csv", 'w')
    csvFile = csv.writer(dataFile)
    # 列名
    colNames = ['RO', 'OCCTIME', 'EFFECTDATE', 'MERCNAME', 'TRANAMT', 'TRANNAME', 
                'TRANCODE', 'CARDBAL', 'JDESC', 'JNUM', 'MACCOUNT', 'F1', 'F2',
                'F3', 'SYSCODE', 'POSCODE', 'CMONEY', 'ZMONEY']
    csvFile.writerow(colNames)
    for i in range(1, totalAmount // 100 + 2):
        pagePayload = {
            "sdate": "2019-01-01",
            "edate": "2021-02-28",
            "account": account,
            "page": str(i),
            "rows": "100"
            }
        pageData = s.post(dataUrl, headers=dataHeaders, data=pagePayload, verify=True).json()['rows']
        for row in pageData:
            csvFile.writerow(row.values())
    dataFile.close()


def login_and_getdata(sno, pwd):
    # s.cookies = get_cookie_from_net(sno, pwd)
    s.cookies = get_cookie_from_file()
    # 获取流水数据
    getdata()


if __name__=='__main__':
    # 一些全局变量
    s = requests.session()
    headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/83.0",
                'Host': 'card.sysu.edu.cn',
                'Origin': 'http://card.sysu.edu.cn',
                'Referer': 'http://card.sysu.edu.cn/',
                'X_REQUESTED_WITH': '5b3b1a369d8fb2e33514113a56809819f3d3db040ede8e6017952dac451983ee',
                'X-Requested-With': "XMLHttpRequest"
                }
    sno = "xxx"  # 学号
    pwd = "xxx"  # 密码

    # 登录并获取数据
    login_and_getdata(sno, pwd)
