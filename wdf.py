#encoding=utf-8
'''
Created on 2016年1月6日

1 实现网页端登录
2016/01/07 完成生成二维码图片，在不同平台打开图片
@author: haibara
'''
import logging
from urllib import urlencode
import urllib2 as my_urllib
import time
import re
import os
import sys
import subprocess

''' 配置log信息 '''
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='webchat.log',
                filemode='w')
uuid = ''
QRImagePath = os.path.join(os.getcwd(), 'qr_image.jpg')

def getRequest(url, data = None):
    try:
        data = data.encode('utf-8')
    except Exception as e:
        logging.error('data.encode error : {0}'.format(e))
    return my_urllib.Request(url, data)

''' 获取uuid '''
def getUUID():
    global uuid#
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
    # data = window.QRLogin.code = 200; window.QRLogin.uuid = "gfXphf8FfQ==";
    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+)"'
    pm = re.search(regx, data)
    
    code = pm.group(1)
    uuid = pm.group(2) 
    print('code = {0} , uuid = {1}'.format(code, uuid))
    logging.debug('code = {0} , uuid = {1}'.format(code, uuid))
    if code == '200':
        return True
    else :
        return False

#显示二维码   
def showQRImage():
    
    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't' : 'webwx' ,
        '_' : int(time.time())
    }
    request = getRequest(url, data = urlencode(params))
    response = my_urllib.urlopen(request)
    
    print('qr_image_path = {0} ,'.format(QRImagePath,))
    logging.debug('qr_image_path = {0}'.format(QRImagePath))
    
    #保存到文件中去
    f = open(QRImagePath,'wb')#保存图片应该使用二进制，不然保存图片显示不正常
    f.write(response.read())
    f.close()
    
    print('sys.platform = {0}'.format(sys.platform))
    logging.debug('sys.platform = {0}'.format(sys.platform))
    if sys.platform.find('linux') >= 0 : #是linux系统
        subprocess.call(['xdg-open', QRImagePath])
    else :
        os.startfile(QRImagePath)#实现双击打开文件的效果

def main():
    try:    
        opener = my_urllib.build_opener(my_urllib.HTTPCookieProcessor)
        my_urllib.install_opener(opener)
    except Exception as e:
        logging.error("url.install_opener() exception : {0}".format(e))
    
    if not getUUID():
        print("获取uuid出错，退出")
        logging('getUUID error,quit')
        return
    
    showQRImage()
    

if __name__ == '__main__':
#     print('中国，{0}'.format('你好'))
#     print("按回车键 开始")
#     try:
#         raw_input()
#         input = raw_input
#     except:
#         input()
    
    main()
    
#     print("按回车键 结束")
#     input()
