import json
import requests
import time
from requests_toolbelt import MultipartEncoder
from wxworkerror import *


class WXWork:
    def __init__(self, agentid, corpid, corpsecret, user):
        """
        Initial WXWork Class's Params and get the first access_token
        :param agentid: application id
        :param corpid: corpration id
        :param corpsecret: application secret
        :param user: user that you want to send message, if have multi users, seperate by "|", such as jessy|janny|chason...
        """
        self.__expiretime = time.time()
        self.__agentid = agentid
        self.__corpid = corpid
        self.__corpsecret = corpsecret
        self.__user = user
        self.__refreshAccessToken()

    def __refreshAccessToken(self):
        """
        Refresh stored access_token
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        params = {
            'corpid': self.__corpid,
            'corpsecret': self.__corpsecret
        }
        req = requests.get(url, params)
        data = json.loads(req.text)
        if data['errcode'] == 0:
            self.__accesstoken = data['access_token']
            self.__expiretime = time.time() + data['expires_in']
            print('Access Token will expired at ' + time.asctime(time.localtime(self.__expiretime)))
        else:
            raise WXWorkError(data['errcode'], data['errmsg'])

    def __getAccessToken(self):
        """
        Compare current time and stored access_token's expired_time，if expired, will call refreshAccessToken()
        """
        currenttime = time.time()
        # print('Current Time is: ' + str(currenttime))
        # print('Expired time is: ' + str(self.__expiretime))
        # print(str(currenttime - self.__expiretime))
        if currenttime >= self.__expiretime:
            try:
                self.__refreshAccessToken()
            except WXWorkError as e:
                print(e)

    def __uploadMediaFile(self, filename, filetype):
        """
        Upload Temporary Media Material.
        :param filename: upload media's name
        :param filetype: It could be image/voice/video/file
        image: <=10MB support JPG/PNG
        voice: <=2MB support AMR
        video: <=10MB support MP4
        file: <=20MB
        :return: upload media's id
        """
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload'
        params = {
            'access_token': self.__accesstoken,
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
            # print(respond)
            return respond['media_id']

    def sendTextInfo(self, text):
        """
        Send text to users.
        :param text: such as ("你的快递已到，请携带工卡前往邮件中心领取。\n出发前可查看<a href=\"http://work.weixin.qq.com\">邮件中心视频实况</a>，聪明避开排队。")
        support \n and a tag
        """
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            'access_token': self.__accesstoken
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
        """
        send image/voice/file to user
        :param filename: media's name
        :param filetype: It could be image/voice/video/file
        image: <=10MB support JPG/PNG
        voice: <=2MB support AMR
        file: <=20MB
        :return:
        """
        media_id = self.__uploadMediaFile(filename, filetype)
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            'access_token': self.__accesstoken,
            'debug': 1
        }
        body = {
            'touser': self.__user,
            'msgtype': filetype,
            'agentid': self.__agentid,
            filetype: {
                'media_id': media_id
            },
        }
        req = requests.post(url, json=body, params=params)
        respond = json.loads(req.text)
        if respond['errcode'] != 0:
            raise WXWorkError(respond['errcode'], respond['errmsg'])

    def sendVideo(self, videoname, title, description):
        """
        send video to user
        :param videoname: video's name
        :param title: title
        :param description: description
        video: <=10MB support MP4
        """
        media_id = self.__uploadMediaFile(videoname, 'video')
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            'access_token': self.__accesstoken
        }
        body = {
            'touser': self.__user,
            'msgtype': 'video',
            'agentid': self.__agentid,
            'video': {
                'content': media_id,
                'title': title,
                'description': description
            },
        }
        req = requests.post(url, json=body, params=params)
        respond = json.loads(req.text)
        if respond['errcode'] != 0:
            raise WXWorkError(respond['errcode'], respond['errmsg'])

    def sendTextCard(self, textcard):
        """
        send textcard to user
        :param textcard: A dictionary contain title/description/url.such as
            {
                "title" : "领奖通知",
                "description" : "<div class=\"gray\">2016年9月26日</div> <div class=\"normal\">恭喜你抽中iPhone 7一台，领奖码：xxxx</div><div class=\"highlight\">请于2016年10月10日前联系行政同事领取</div>",
                "url" : "URL"
            },
            the description support gray/normal/highlight
        :return:
        """
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            'access_token': self.__accesstoken
        }
        body = {
            'touser': self.__user,
            'msgtype': 'textcard',
            'agentid': self.__agentid,
            'textcard': textcard
        }
        req = requests.post(url, json=body, params=params)
        respond = json.loads(req.text)
        if respond['errcode'] != 0:
            raise WXWorkError(respond['errcode'], respond['errmsg'])

    def sendNews(self, newstype, news):
        """
        send Pic-News to user. news is stored in your phone.
        :param newstype: can be news or mpnews, the difference between them is mpnews will be stored in the WXWork, and news is stored in your phone.
        :param news: a dictionary contain {'articles': [1-8 dicts list]}
        For news:
            in the list the dicts should have key-value as below:
            title:(must)
            description:(optional)
            url:(optional)
            picurl:(optional)1068*455 or 150*150 will be a better resolution
            appid:(optional)Little-App's appid, the Little-App should be connected to the application
            pagepath:(optional)Little-App's page path
            the url and appid+pagepath should have one, if have appid+pagepath, the url will be ignored.
        For mpnews:
            in the list the dicts should have key-value as below:
            title:(must)
            thumb_media_id:(must)picture present in the mpnews.
            author:(optional)
            content_source_url:(optional)
            content:(must) mpnews's content, support html tag
            digest:(optional) mpnews's description
        """
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            'access_token': self.__accesstoken
        }
        body = {
            'touser': self.__user,
            'msgtype': newstype,
            'agentid': self.__agentid,
            newstype: news
        }
        req = requests.post(url, json=body, params=params)
        respond = json.loads(req.text)
        if respond['errcode'] != 0:
            raise WXWorkError(respond['errcode'], respond['errmsg'])

    def sendMarkdown(self, markdownContent):
        self.__getAccessToken()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            'access_token': self.__accesstoken
        }
        body = {
            'touser': self.__user,
            'msgtype': 'markdown',
            'agentid': self.__agentid,
            'markdown': {
                'content': markdownContent
            }
        }
        req = requests.post(url, json=body, params=params)
        respond = json.loads(req.text)
        if respond['errcode'] != 0:
            raise WXWorkError(respond['errcode'], respond['errmsg'])


if __name__ == '__main__':
    with open('account.json', 'r') as f:
        account = json.load(f)
    print(account)
    print(type(account))
    wxwork = WXWork(account[0]['agentid'], account[0]['corpid'], account[0]['corpsecret'], account[0]['user'])
    print("init finished.")
    print("send Text")
    wxwork.sendTextInfo('hello world')
    time.sleep(5)
    print("send image")
    wxwork.sendMedia('2022-04-15.png', 'image')
    time.sleep(5)
    print("send file")
    wxwork.sendMedia('但斌内部讲话.pdf', 'file')
    time.sleep(5)
    print("send textcard")
    wxwork.sendTextCard({'title': 'test', 'description': 'test', 'url': 'www.baidu.com'})
    time.sleep(5)
    print("send news")
    wxwork.sendNews('news', {'articles': [{'title': 'test news', 'description': 'test', 'url': 'www.baidu.com'}]})
    time.sleep(5)
    print("send markdown")
    markdown = "您的会议室已经预定，稍后会同步到**邮箱**"
    wxwork.sendMarkdown(markdown)
