import requests,json,time
import re
import pymysql
import redis

class getgoods(object):

    def __init__(self):
        #全部商品  "https://sell.paipai.com/auction-list?groupId=-1&entryid=p0120003dbdlogo"
        #https://used-api.jd.com/auction/list?pageNo=2&pageSize=50&category1=&status=&orderDirection=1&auctionType=1&orderType=1&callback=__jp116
        # https://used-api.paipai.com/auction/list?pageNo=1&pageSize=50&category1=&status=1&orderDirection=1&auctionType=1&orderType=1&groupId=1000005&callback=__jp35
        #电脑数码 groupId=1000005
        #食品饮料 groupId=1000442
        #珠宝配饰 groupId=1000009
        #品牌家电 groupId=1000004
        #运动户外 groupId=1000003
        #厨房用品 groupId=1000011
        #礼品箱包 groupId=1000010
        #母婴玩具 groupId=1000002
        #美妆个护 groupId=1000404
        #居家日用 groupId=1000007
        #服饰鞋靴 groupId=1000008
        #手机通讯 groupId=1000006
        #其它分类 groupId=1999999

        self.list = (1000005,1000442,1000009,1000004,1000003,1000011,1000010,1000002,1000404,1000007,1000008,1000006,1999999)
        # self.list = (1000008,)
        # self.url = "https://used-api.jd.com/auction/list?pageNo=1&pageSize=50&category1=&status=&orderDirection=1&auctionType=1&orderType=2&callback=__jp116"
        self.headers = {
            # "Host": "used-api.jd.com",
            # "Host" : "used - api.paipai.com",
            # "Connection": "keep-alive",
            # "Referer": "https: // paipai.jd.com / auction - list",
            # "Connection": "close",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
        }
        self.myqllink = pymysql.connect(host= '127.0.0.1',user = 'root', passwd='ding123',db= 'duobaodao')
        self.cursor = self.myqllink.cursor()
        self.errordata = {'geterror':[],'setsqlerror':[]}
        self.redislink = redis.Redis(host='127.0.0.1',port=6379)

    def getAllGoods(self):
        #对外暴露方法
        #开始获取页面中的产品信息
        #对产品进行分类
        #页面中的分类
        #返回的数据格式
        #开始循环采集每个分类的数据
        for groupId in self.list:
            #开始采集每个分页中商品信息，判断是否成功的依据1、code 是否为200 和采集返回的数据中auctionInfos是否为空
            pageNo = 0
            bb = True
            while bb:
                pageNo = pageNo + 1
                url = "https://used-api.paipai.com/auction/list?pageNo=%d&pageSize=50&category1=&status=1&orderDirection=1&auctionType=1&orderType=1&groupId=%s&callback=__jp35" % (
                pageNo, groupId)
                thedata = self.__getGoods(url)
                print(groupId, pageNo)
                if thedata[0] == 444:
                    print("采集出现错误")
                    bb = False

                    self.errordata['geterror'].append(url)

                if thedata[1] == None:
                    bb = False
                    print("已经完成采集")
                else:
                    #将数据存入数据库
                    if isinstance(thedata[1], list):
                        # print("list")
                        for data1 in thedata[1]:
                            # print(data1)
                            self.__setdata(data1)
                        time.sleep(4)
                time.sleep(1)
                if pageNo >= 200:
                    pageNo = 0
                    bb = False
                    print("已经完成采集")
        self.myqllink.close()

    def test(self):
        #对外暴露方法
        #测试使用
        url = "https://used-api.paipai.com/auction/list?pageNo=1&pageSize=100&category1=&status=1&orderDirection=1&auctionType=1&orderType=1&groupId=1000005&callback=__jp35"
        thedata = self.__getGoods(url)
        print(thedata)
        if thedata[1] == None:
            bb = False
            print("已经完成采集")
        else:
            # 将数据存入数据库
            print('dddd')
            if isinstance(thedata[1], list):
                print("list")
                for data in thedata[1]:
                    self.__setdata(data)
                    time.sleep(1)

    def clearRedis(self):
        #清楚redis
        #方法需要重写
        keys = self.redislink.keys()
        for key in keys:
            print(key)
            type = self.redislink.type(key)
            if type == b'string':
                vals = self.redislink.get(key)
            elif type == b'list':
                vals = self.redislink.lrange(key, 0, -1)
                # print(vals)
            elif type == b'set':
                vals = self.redislink.smembers(key);
            elif type == b'zset':
                vals = self.redislink.zrange(key, 0, -1)
            elif type == b"hash":
                vals = self.redislink.hgetall(key)
            else:
                print(type, key)
            print(vals)
            # self.redislink.delete(key)



    def gethistory(self,auction):
        #https://used-api.paipai.com/auction/detail?callback=jQuery32108877681006626417_1574400875551&auctionId=120934440&p=2
        url = (
            "https://used-api.paipai.com/auction/detail?callback=jQuery32108877681006626417_1574400875551&auctionId={0}&p=2").format(
            auction)
        # print(url)
        r = requests.get(url)
        result_json = re.search(r'{.*}', r.text)
        result_dict = json.loads(result_json.group())
        # print(result_dict)
        pricelist = result_dict['data']['historyRecord']
        # print(pricelist)
        for nb in pricelist:
            print(nb['offerPrice'])
        # try:
        #     url = ("https://used-api.paipai.com/auction/detail?callback=jQuery32108877681006626417_1574400875551&auctionId={0}&p=2").format(auction)
        #     # print(url)
        #     r = requests.get(url)
        #     result_json = re.search(r'{.*}', r.text)
        #     result_dict = json.loads(result_json.group())
        #     # print(result_dict)
        #     pricelist = result_dict['data']['historyRecord']
        #     # print(pricelist)
        #     for nb in pricelist.keys():
        #         print(pricelist[nb]['offerPrice'])
        # except:
        #     print("采集历史成交价格出错")

    def getGoodsid(self, usedNo):
        #根据提供的usedNo获取拍卖品id
        #在获取历史成交价格和拍卖时选着使用
        sql = "SELECT id FROM goods WHERE usedNo ={0} ".format(usedNo)
        try:
            self.cursor.execute(sql)
            # 执行sql语句
            self.myqllink.commit()
            results = self.cursor.fetchall()
            return results
        except:
            # 发生错误时回滚
            print("查询商品拍卖id {0} 出错".format(usedNo))

    def getUsedNo(self, condition, usedNo = ''):
        #根据条件获取商品的usedNo 可以考虑将新旧程度也加上去
        #条件基本时允许商品名或者usedNo
        sql = "SELECT usedNo, quality, shopId FROM usedname WHERE productName LIKE '%{0}%'".format(condition)

        try:
            self.cursor.execute(sql)
            # 执行sql语句
            self.myqllink.commit()
            results = self.cursor.fetchall()
            return results
        except:
            # 发生错误时回滚
            print("查询商品 usedNo {0} 出错".format(condition))

    def printtest(self):
        print("printt")
        pass

    def seachGoods(self):
        #获取产品资料
        print("ss")

    def __getGoods(self,url):
        #获取每一个分页商品信息
        try:
            r = requests.get(url,headers = self.headers)
            result_json = re.search(r'{.*}', r.text)
            result_dict = json.loads(result_json.group())
            # print(result_dict)
            # print(result_dict["data"]["auctionInfos"])
            # exit()
            if result_dict['code'] == 200:
                #将数据返回
                code = 200
                if result_dict["data"]["auctionInfos"]:
                    thedata = result_dict["data"]["auctionInfos"]
                else:
                    thedata = None
                return code, thedata
            else:
                #进入下一次循环或者在次查询
                code = False
                thedata = ''
                return code,thedata
        except:
            thedata = ''
            code = 444
            return code,thedata
        # print(result_dict)
        # print(tt["data"][])
        # print(tt["data"]["auctionInfos"][0])

    def __setdata(self,data):

        keydata = ''
        valuedata = ''
        if isinstance(data,dict):
            #先查商品是否已经录入，可以使用redis集合
            # 如果商品没有录入就将商品存入到数据库和redis
            for key in data.keys():
                if data[key] == None:
                    data[key] = 0
            if self.redislink.sismember('usedName', data['usedNo'])== False:
                keydata = 'usedNo, productName, primaryPic, quality, shopId, size, brandId, shortProductName'
                valuedata = ("'{0}'" +","+"'{1}'" +","+"'{2}'" +","+"'{3}'" +","+"'{4}'" +","+"'{5}'" +","+"'{6}'" +","+"'{7}'" )\
                    .format(data['usedNo'],data['productName'],data['primaryPic'],data['quality'],data['shopId'],data['size'],data['brandId'],data['shortProductName'])
                sql = "INSERT INTO usedName ({0}) VALUES ({1})".format(keydata,valuedata)

                try:
                    self.cursor.execute(sql)
                    # 执行sql语句
                    self.myqllink.commit()
                    self.redislink.sadd('usedName', data['usedNo'])
                except:
                    # 发生错误时回滚

                    self.errordata['setsqlerror'].append(data)
                    print("usedno cuowu")
                    self.myqllink.rollback()
                    self.redislink.srem('usedName', data['usedNo'])

            #查商店是否已经录入，没有如入的化将商店存入数据库
            if self.redislink.sismember('shop', data['shopId'])==False:
                keydata = 'shopId,shopName'
                valuedata = ("'{0}'" +","+"'{1}'"  )\
                    .format(data['shopId'],data['shopName'])
                sql = "INSERT INTO shop ({0}) VALUES ({1})".format(keydata,valuedata)
                try:
                    self.cursor.execute(sql)
                    # 执行sql语句
                    self.myqllink.commit()
                    self.redislink.sadd('shop', data['shopId'])
                except:
                    # 发生错误时回滚

                    self.errordata['setsqlerror'].append(data)
                    print("shop cuowu")
                    self.myqllink.rollback()
                    self.redislink.srem('shop', data['shopId'])
            #查商品号是否录入
            #如果没有如入就将商品写入数据库
            if self.redislink.sismember('goodslist', data['id'])==False:
                keydata = 'id, usedNo, startTime, endTime, cappedPrice, status, quality'
                valuedata = ("'{0}'" +","+"'{1}'" +","+"'{2}'" +","+"'{3}'" +","+"'{4}'" +","+"'{5}'" +","+"'{6}'")\
                    .format(data['id'],data['usedNo'],data['startTime'],data['endTime'],data['cappedPrice'],data['status'],data['quality'])
                sql = "INSERT INTO goods ({0}) VALUES ({1})".format(keydata,valuedata)
                try:
                    self.cursor.execute(sql)
                    # 执行sql语句
                    self.myqllink.commit()
                    self.redislink.sadd('goodslist', data['id'])
                except:
                    # 发生错误时回滚

                    self.errordata['setsqlerror'].append(data)
                    print("goodslist cuowu")
                    self.myqllink.rollback()
                    self.redislink.srem('goodslist', data['id'])
            # for key in data.keys():
            #     keydata = keydata + key+","
            #     # keydata =(keydata + '%s' + key + ',')%(key)
            #     valuedata = (valuedata +"'{0}'" +",").format(data[key])
            # keydata = keydata.strip(',')
            # valuedata = valuedata.strip(',')
            # sql = "INSERT INTO goodslist ({0}) VALUES ({1})".format(keydata, valuedata)
            # self.cursor.execute(sql)
            #     # 执行sql语句
            # self.myqllink.commit()

            # try:
            #     self.cursor.execute(sql)
            #     # 执行sql语句
            #     self.myqllink.commit()
            #
            # except:
            #     # 发生错误时回滚
            #
            #     self.errordata['setsqlerror'].append(data)
            #     print("sql cuowu")
            #     self.myqllink.rollback()
        else:
            #返回数据，并对数据不做处理
            print('数据格式错误不是dict')

    def __del__(self):
        print(self.errordata)



