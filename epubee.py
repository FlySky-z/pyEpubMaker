import requestTools as rT
import re
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor
import sys
import os
import gen_epub_testCode

nowPath = os.path.dirname(os.path.abspath(sys.argv[0]))
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)s %(levelname)s: %(message)s",
                    datefmt='%Y-%m-%d  %H:%M:%S'  # 注意月份和天数不要搞乱了，这里的格式化符与time模块相同
                    )
sampleUrl = "http://reader.epubee.com/books/mobile/"
sampleUrl_1 = "http://reader.epubee.com/books/mobile/4a/4a00438722c3a2ce6be1fb55eb242a14/"
epubeeHtml_catcher = rT.request()


def get_book_key(normalUrl: str):
    # sampleUrl_1 = "http://reader.epubee.com/books/mobile/9e/9e114fc8ba5a1b9242baf8ed95982239/text00000.html"
    # sampleUrl_2 = "http://reader.epubee.com/books/mobile/f7/f758b8a18b6bcd665adadf7c15b1bded/"
    keys = normalUrl.split("/")
    try:
        index = keys.index("mobile")
        book_key = keys[index + 1] + '/' + keys[index + 2] + '/'
    except ValueError:
        logging.warning(f"[book_key] ValueError")
        return ""
    logging.info(f"[book_key]={book_key}")
    return book_key


def catch_htmlImg(targetUrl: str, id_list: list):
    imgUrl_list = [targetUrl + img for img in id_list]
    logging.debug(f"[catch_htmlImg imgUrl_list]={imgUrl_list}")
    threadPool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="imgCatch_")
    img_StorePath = nowPath+'/'+'epubeeImg'
    logging.info(f"[catch_htmlImg img_StorePath]={img_StorePath}")
    if not os.path.exists(img_StorePath):
        os.mkdir(img_StorePath)
    img = rT.request()
    contents = threadPool.map(img.get_content, imgUrl_list)
    threadPool.shutdown(wait=True)
    imgId = id_list.__iter__()
    for content in contents:
        imgName = imgId.__next__()
        imgNames = imgName.split(".")
        rT.saveImg(content, img_StorePath, imgNames[0], imgFormat=imgNames[1],timestap=False)


def catch_html(url: str, epub=None):
    urlKey = get_book_key(url)
    if not urlKey:
        logging.warning("[catch_html] not find book_key")
        return None
    htmlUrl = sampleUrl+urlKey
    epubeeHtml = epubeeHtml_catcher.get_text(htmlUrl+"text00001.html")

    all_textList = re.findall(f"/books/mobile/{urlKey}(.*?)#", epubeeHtml)
    textList = list(set(all_textList))
    textList.sort()  # 确保去重后顺序正确
    logging.debug(f"[catch_html textList]={textList}")
    logging.info(f"[catch_html text]预计抓取{len(textList)}页")

    imgList = []
    for text in textList:
        bookHtml = '<html xmlns="http://www.w3.org/1999/xhtml">\r\n<head>\r\n<title>book</title>\r\n</head>\r\n<body> '
        now_imgList = re.findall(r'<img align=".*?" height=".*?" width=".*?" src="(.*?)" />', epubeeHtml)
        logging.debug(f"[catch_html now_imgList]={now_imgList}")
        logging.info(f"[catch_html img]{text}预计抓取{len(now_imgList)}张")
        imgList.extend(now_imgList)

        epubeeHtml = epubeeHtml_catcher.get_text(htmlUrl + text)
        soup = BeautifulSoup(epubeeHtml, "html.parser")
        for img in soup.findAll('img'):
            if not img['src'].startswith('http://'):
                img['src'] = "images/"+img['src']

        bookHtml += soup.find("div",attrs={"class":"readercontent-inner"}).__str__()
        # bookHtml = re.sub(f'<a href="text\d+\.html#filepos', '<a href="#filepos', bookHtml)  # 替换为本地filepos
        bookHtml += '</body>\r\n</html>'
        rT.saveText(bookHtml, nowPath+f"/{text}", False)
        ep.add_document_fromlocal(text)
    imgList = list(set(imgList))
    # catch_htmlImg(htmlUrl, imgList)


logging.info("start epubee crawler")
ep = gen_epub_testCode.EPUBMarker("机器学习实战")
catch_html(sampleUrl_1, ep)
imglist = os.listdir("epubeeImg")
# for img in imglist:
#     ep.add_image_fromlocal("epubeeImg/"+img)
ep.add_image_fromlocal("/Users/flysky/Desktop/cover.png", iscover=True)
ep.set_creator("sample only")
ep.saveEPUB("epubBook")