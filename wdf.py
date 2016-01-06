#encoding=utf-8
'''
Created on 2016年1月6日

1 实现网页端登录

@author: haibara
'''
import logging
from urllib import urlencode
import urllib2 as my_urllib
import time


''' 配置log信息 '''
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='webchat.log',
                filemode='w')
uuid = ''

def getRequest(url, data = None):
    try:
        data = data.encode('utf-8')
    except Exception as e:
        logging.error('data.encode error : {0}'.format(e))
    return my_urllib.Request(url, data)

''' 获取uuid '''
def getUUID():
    
    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid' : 'wx782c26e4c19acffb' ,
        'fun' : 'new' ,
        'lang' : 'zh_CN' ,
        '_' : int(time.time())#转换成int类型
    }
    
    request = getRequest(url, data = urlencode(params))
    response = my_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')#忽略一些不可见的字符
    print('getUIID data = {0}'.format(data))
    logging.debug('getUIID data = {0}'.format(data))
    

def main():
    try:    
        opener = my_urllib.build_opener(my_urllib.HTTPCookieProcessor)
        my_urllib.install_opener(opener)
    except Exception as e:
        logging.error("url.install_opener() exception : {0}".format(e))
    
    getUUID()

if __name__ == '__main__':
#     print('中国，{0}'.format('你好'))
    print("按回车键 开始")
    try:
        raw_input()
        input = raw_input
    except:
        input()
    
    main()
    
    print("按回车键 结束")
    input()
