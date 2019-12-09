import requests,json
import re
from random import randint
from config import Agent
from login import loginCook

class duobao(object):

    def onegoods(self):
        #获取已经存储的信息
        pass

    def goodsinfo(self, paimaiid):
        #获取目前最高价格
        #https://used-api.paipai.com/auctionRecord/batchCurrentInfo?auctionId=120846715&callback=__jp5
        s = requests.session()
        headers = {
            "User-Agent": Agent[randint(0, 3)]['User-Agent'],
        }
        query_url = 'https://used-api.paipai.com/auctionRecord/batchCurrentInfo?auctionId={0}&callback=__jp5' \
            .format(paimaiid)
        try:
            r = s.get(query_url, headers=headers, timeout=1)
            # print(r.text)
            result_json = re.search(r'{.*}', r.text)
            result_dict = json.loads(result_json.group())
        except:
            print("没有查询到信息")
            result_dict = {}
        finally:
            return result_dict

    def sendPrice(self,youcookie,auctionId,price):
        #出价
        buy_url = 'https://used-api.jd.com/auctionRecord/offerPrice'
        data = {
            # 'trackId': 'dde516c09ed6a70f14d0d9404cd963c7',
            # 'eid': 'UM3RCYTFRHBSSVPTU6IQSQSIMW77JIHEC7PWVTBCEVGSCJWMNTV3THFHD4F3N7I7SOINX3RMKXD4HJY3OX6AR5FQCQ',
        }
        HEADERS = {
            'Referer': 'https://paipai.jd.com/auction-detail',
            'User-Agent':Agent[randint(0, 3)]['User-Agent'],
            'Cookie': youcookie
        }
        data['price'] = str(int(price))
        data['auctionId'] = str(auctionId)
        # print(data)
        resp = requests.post(buy_url, headers=HEADERS, data=data)
        resultdata = resp.json()
        if resultdata['code'] == 501 and resultdata['message'] == "用户未登录":
            loginclass =loginCook()
            loginclass.longduomingdao()
            self.sendPrice(youcookie,auctionId,price)
        return resultdata