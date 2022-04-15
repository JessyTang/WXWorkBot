import json
import requests
import time
from requests_toolbelt import MultipartEncoder
from wxworkerror import *


class WXWork:
    def __init__(self):
        self.__filename = 'account.json'
        self.__expiretime = time.time()
        try:
            file = open(self.__filename, 'r')
        except FileNotFoundError as e:
            print(e)
        else:
            info = json.load(file)
            self.__agentid = info['agentid']
            self.__corpid = info['corpid']
            self.__corpsecret = info['corpsecret']
            self.__user = info['user']
        finally:
            file.close()

    def __refreshAccessToken(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        params = {
            'corpid': self.__corpid,
            'corpsecret': self.__corpsecret
        }
        req = requests.get(url, params)
        data = json.loads(req.text)
        if data['errcode'] == 0:
            self.__accessToken = data['access_token']
            self.__expireTime = time.time() + data['expires_in'] * 60
            print('Access Token will expired at ' + time.asctime(time.localtime(self.__expireTime)))
        else:
            raise WXWorkError(data['errcode'], data['errmsg'])

    def __getAccessToken(self):
        currenttime = time.time()
        if currenttime >= self.__expiretime:
            try:
                self.__refreshAccessToken()
            except WXWorkError as e:
                print(e)

    def __uploadMediaFile(self, filetype, filename):
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload'
        params = {
            'access_token': self.__accessToken,
            'type': filetype
        }
        data = MultipartEncoder(
            fields={'file': (filename, open('./TempMedia/'+filename, 'rb'), 'multipart/form-data')}
        )
        req = requests.post(url, params=params, data=data, headers={'Content-Type': data.content_type})
        respond = json.loads(req.text)
        if respond['errcode'] != 0:
            raise WXWorkError(respond['errcode'], respond['errmsg'])
        else:
            return respond['media_id']

    def sendTextInfo(self, text):
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            'access_token': self.__accessToken
        }
        body = {
            'touser': self.__user,
            'msgtype': 'text',
            'agentid': self.__agentid,
            'text': {
                'content': text
            },
        }
        req = requests.post(url, json=body, params=params)
        respond = json.loads(req.text)
        if respond['errcode'] != 0:
            raise WXWorkError(respond['errcode'], respond['errmsg'])

    def sendMedia(self, filename, filetype):
        pass




if __name__ == '__main__':
    print()