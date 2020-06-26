import requests
import random
import time
import os

class request:
    def __init__(self, method="get", params=None, headers=None, cookies=None, charset="utf-8"):
        self.headers = self.get_userAgentHeaders()
        if headers is not None:
            self.headers.update(headers)
        self.params = params
        self.method = method
        self.cookies = cookies
        self.charset = charset

    def try_request(self, url, timeout=3):
        '''
        向url连接发起请求,默认为get,否则为post.
        :param url: 发起请求的url连接
        :param timeout: 请求的超时时间,默认为3
        :return: 返回Response对象
        '''
        try:
            if self.method == "get":
                response = requests.get(url, headers=self.headers, params=self.params, cookies=self.cookies, timeout=3)
            else:
                response = requests.post(url, headers=self.headers, params=self.params, cookies=self.cookies, timeout=3)
            return response
        except:
            print("[try_request]try_request failure by url:%s" % url)
            return None

    def get_content(self, url):
        '''
        向url发起请求并返回其内容
        :param url: 发起请求的url连接
        :return: 返回bytes类型Response信息
        '''
        try:
            content = self.try_request(url).content
        except:
            content = None
            print("[get_content]get_content failure by url:%s" % url)
        return content

    def get_text(self, url, charset=None, apparentEncoding=False):
        '''
        向url发起请求并返回其str文本内容
        :param url: 发起请求的url连接
        :param charset: 文本的编码格式,默认为utf-8
        :return: str
        '''
        try:
            response = self.try_request(url)
            if charset is not None:
                text = response.content.decode(charset)
            elif apparentEncoding:
                text = response.content.decode(response.apparent_encoding)
            else:
                text = response.content.decode(self.charset)
        except:
            text = None
            print("[get_text]get_text failure by url:%s" % url)
        return text

    def get_json(self, url):
        try:
            json = self.try_request(url).json()
        except:
            json = None
            print("[get_json]JSON conversion error by url:%s" % url)
        return json

    def get_userAgentHeaders(self):
        '''
        随机选取一个UserAgent.
        :return: 带有UserAgent参数的字典headers
        '''
        userAgentList = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        useragent = random.choice(userAgentList)
        headers = {'User-Agent': useragent}
        return headers


def saveImg_temp(content, imgFormat="jpg"):
    with open(f"tempImg{time.strftime('%Y%m%d%H%M%S')}.{imgFormat}", "wb") as f:
        f.write(content)


def saveImg(content, savePath: str, name="", imgFormat="jpg", timestap=True):
    if timestap:
        save = f"{savePath}/{name + ' '}{time.strftime('%Y%m%d%H%M%S')}.{imgFormat}"
    else:
        save = f"{savePath}/{name}.{imgFormat}"
    with open(save, "wb") as f:
        f.write(content)


def saveText_temp(text: str, textFormat="txt"):
    with open(f"tempText{time.strftime('%Y%m%d%H%M%S')}.{textFormat}", "w") as f:
        f.write(text)


def saveText(text: str, savePath: str, timestap=True):
    name = os.path.basename(savePath)
    mediatype = name.split(".")[-1]
    head = name.split(".")[:-1]
    if timestap:
        save = f"{savePath}/{head + ' '}{time.strftime('%Y%m%d%H%M%S')}.{mediatype}"
    else:
        save = f"{savePath}"
    with open(save, "w") as f:
        f.write(text)
