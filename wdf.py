# encoding=utf-8
'''
Created on 2016年1月6日

1 实现网页端登录
2016/01/07 完成生成二维码图片，在不同平台打开图片
2016/01/12 二维码扫码登录成功，post请求数据时中的cookies关键值
   need to do 怎么关闭扫码成功后的打开的图片
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
import xml.dom.minidom as minidom

''' 配置log信息 '''
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='webchat.log',
                filemode='w')
uuid = ''
deviceId = 'e1234567890'
QRImagePath = os.path.join(os.getcwd(), 'qr_image.jpg')

def getRequest(url, data=None):
    try:
        data = data.encode('utf-8')
    except Exception as e:
        logging.error('data.encode error : {0}'.format(e))
    return my_urllib.Request(url, data)

''' 获取uuid '''
def getUUID():
    global uuid  #
    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid' : 'wx782c26e4c19acffb' ,
        'fun' : 'new' ,
        'lang' : 'zh_CN' ,
        '_' : int(time.time())  # 转换成int类型
    }
    
    request = getRequest(url, data=urlencode(params))
    response = my_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')  # 忽略一些不可见的字符
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

# 显示二维码   
def showQRImage():
    
    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't' : 'webwx' ,
        '_' : int(time.time())
    }
    request = getRequest(url, data=urlencode(params))
    response = my_urllib.urlopen(request)
    
    print('qr_image_path = {0} ,'.format(QRImagePath,))
    logging.debug('qr_image_path = {0}'.format(QRImagePath))
    
    # 保存到文件中去
    f = open(QRImagePath, 'wb')  # 保存图片应该使用二进制，不然保存图片显示不正常
    f.write(response.read())
    f.close()
    
    print('sys.platform = {0}'.format(sys.platform))
    logging.debug('sys.platform = {0}'.format(sys.platform))
    if sys.platform.find('linux') >= 0 :  # 是linux系统
        subprocess.call(['xdg-open', QRImagePath])
    else :
        os.startfile(QRImagePath)  # 实现双击打开文件的效果 windows

''' 扫描等到登录'''        
def waitLogin():
    global tip, redirect_uri, base_uri
    tip = 0
    url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?uuid=%s&tip=%s&_=%s' % (
            uuid, '0', int(time.time()))
    print('waitLogin url = {0}'.format(url))
    request = getRequest(url)
    response = my_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    print('waitLogin data = {0}'.format(data))
    logging.debug('waitLogin data = {0}'.format(data))
    
    regx = r'window.code=(\d+);'
    pm = re.search(regx, data)
    code = pm.group(1)
    # 201 表示扫描成功在等待， 200 表示确认登录， 408代表超时
    print('waitLogin code = {0}'.format(code))
    if code == '201':
        print('扫描成功，请在手机上确认登录')
        return False
    elif code == '200':
        # 返回一个redirect_uri
        regx = r'window.redirect_uri="(\S+)";'
        pm = re.search(regx, data)
        redirect_uri = pm.group(1) + '&fun=new'  # 作用未知
        base_uri = redirect_uri[:redirect_uri.rfind('/')]  # https://wx2.qq.com/cgi-bin/mmwebwx-bin
        print('base_uri = {0}'.format(base_uri))
        return True
    elif code == '408':
        # print('超时')
        return False

''' 登录'''
def login():
    global skey, wxsid, wxuin, pass_ticket, baseRequest
    request = getRequest(redirect_uri)
    response = my_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
#     print('login dat = {0}'.format(data))
    logging.debug('login return data = {0}'.format(data))
    '''
    <error>
        <ret>0</ret>
        <message>OK</message>
        <skey>@crypt_5d78f094_3f0a5e8e08d80e48fdc207a3ba7475bf</skey>
        <wxsid>J7r1X0NIj4zd0hTC</wxsid>
        <wxuin>757895900</wxuin>
        <pass_ticket>FfR%2FHQGCGYntMsj6ItnWkn1MP8K3N5M0JqRlh4yW87bUmsWWm06d%2FOPgpcXhqhSb</pass_ticket>
        <isgrayscale>1</isgrayscale>
    </error>
    '''
    doc = minidom.parseString(data)
    root = doc.documentElement
    for node in root.childNodes:
        if node.nodeName == 'skey':
            skey = node.childNodes[0].data
        elif node.nodeName == 'wxsid':
            wxsid = node.childNodes[0].data
        elif node.nodeName == 'wxuin':
            wxuin = node.childNodes[0].data
        elif node.nodeName == 'pass_ticket':
            pass_ticket = node.childNodes[0].data
    print('login() skey = {0}, wxsid = {1}, wxuin = {2}, pass_ticket = {3}'
          .format(skey, wxsid, wxuin, pass_ticket))
    
    if not all((skey,wxsid,wxuin,pass_ticket)): #查看 all的含义
        return False
    
    #后续通信需要使用post的方式提交数据
    baseRequest = {
        'Uin' : int(wxuin) ,
        'Sid' : wxsid ,
        'Skey' : skey ,
        'DeviceID' : deviceId#DeviceID是一个本地生成的随机字符串 e开头
    }
    

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
    
    while not waitLogin() :
        pass
    
    os.remove(QRImagePath) #关闭显示图片的窗口,windows不可
    login()

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
