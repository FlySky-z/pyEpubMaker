import os
import sys
import zipfile
import logging
from time import strftime
from lxml import etree
import uuid
import shutil

# 设置日志格式
LOG_FORMAT = '%(asctime)s : %(levelname)s [%(funcName)s] -%(processName)s- thread<%(thread)s>	"%(message)s"'
# 设置日志的时间格式
# DATE_FORMAT = "%Y/%m/%d %H:%M:%S %a"
# 设置日志的输出等级.调试时为DEBUG
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
# savepath = os.path.abspath(os.path.basename(sys.argv[0]))
savepath = "epubBook/"


class XMLMaker:
    def __init__(self, root="xml", attrib=None, text=None, nsmap=None):
        if attrib and type(attrib) != dict:
            raise SyntaxError("attrs is a dict")

        self.root = etree.Element(root, attrib, nsmap=nsmap)
        self.tree = etree.ElementTree(self.root)
        if text:
            self.root.text = text
        self.xml = self.root

    def get_element(self, tag=None, root=None):
        if not tag:
            return self.root
        elif not root:
            return self.root.find(tag)
        else:
            return root.find(tag)

    def add_element(self, tag: str, rootElement=None, attrib=None, text=None, nsmap=None):
        if rootElement is None:
            rootElement = self.root
        if attrib and type(attrib) != dict:
            raise SyntaxError("attrs is a dict")

        element = etree.Element(tag, attrib, nsmap=nsmap)
        if text:
            element.text = str(text)
        rootElement.append(element)
        return element

    @staticmethod
    def static_add_element(tag: str, rootElement, attrib=None, text=None, nsmap=None):
        if attrib and type(attrib) != dict:
            raise SyntaxError("attrs is a dict")
        element = etree.Element(tag, attrib, nsmap=nsmap)
        if text:
            element.text = str(text)
        rootElement.append(element)
        return element

    def add_docinfo(self, info: str, content: str):
        exec(f"self.tree.docinfo.{info}=str(content)")

    def genXML(self, pretty_print=True, encoding="UTF-8"):
        return etree.tostring(self.tree, pretty_print=pretty_print, encoding=encoding, method="xml",
                              xml_declaration=True,
                              standalone=None)

    def saveXML(self, name: str, path=None, pretty_print=True, encoding="UTF-8"):
        if not path:
            path = ""
        elif not path.endswith(("/", "\\")):
            path += "/"
        with open(path + name, "wb") as f:
            f.write(self.genXML(pretty_print=pretty_print, encoding=encoding))


class EPUBMarker:
    def __init__(self, title=None):
        if title is None:
            self.title = "my epub book"
        else:
            self.title = title
        logging.debug("EpubMaker __init__ start")
        self.item_id = 0
        self.playOrder = 1
        self.dc_uri = "{http://purl.org/dc/elements/1.1/}"
        self.opf_uri = "{http://www.idpf.org/2007/opf}"
        self.identifier = str(uuid.uuid4())
        self.container = self.create_container()
        self.files_list = []
        self.images_list = []
        self.filename_list = []
        self.file_content = {}
        self.opf_metadata = None
        self.opf_manifest = None
        self.opf_spine = None
        self.opf_guide = None
        self.opf = self.create_basic_opf()

        self.ncx_head = None
        self.docTitle_text = None
        self.ncx_navMap = None
        self.ncx = self.create_basic_ncx()
        self.add_opf_item("toc.ncx", "ncx", "application/x-dtbncx+xml")
        self.add_opf_item(href="stylesheet.css")
        self.stylesheet = self.set_styleshteet()
        logging.info("EpubMaker __init__ fine")

    def create_mimetype(self, savepath):
        with open(savepath + "mimetype", "w") as f:
            f.write("application/epub+zip")
            f.close()

    def create_container(self):
        container_nsmap = {None: "urn:oasis:names:tc:opendocument:xmlns:container"}
        container_dic = {"version": "1.0"}
        container = XMLMaker("container", attrib=container_dic, nsmap=container_nsmap)

        rootfiles = container.add_element("rootfiles")

        rootfile_dic = {"full-path": "OEBPS/content.opf",
                        "media-type": "application/oebps-package+xml"}
        container.add_element("rootfile", attrib=rootfile_dic, rootElement=rootfiles)
        logging.debug("create notice 'container.xml' generate fine")
        return container

    def create_basic_opf(self):
        package_nsmap = {None: "http://www.idpf.org/2007/opf"}
        package_dic = {"unique-identifier": "uid",
                       "version": "2.0"}
        opf = XMLMaker("package", attrib=package_dic, nsmap=package_nsmap)

        metadata_nsmap = {"calibre": "http://calibre.kovidgoyal.net/2009/metadata",
                          "dcterms": "http://purl.org/dc/terms/",
                          "dc": "http://purl.org/dc/elements/1.1/",
                          "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
        self.opf_metadata = opf.add_element("metadata", nsmap=metadata_nsmap)
        opf.add_element(self.dc_uri + "title", text=self.title, rootElement=self.opf_metadata)
        opf.add_element(self.dc_uri + "language", text="ZN", rootElement=self.opf_metadata)
        identifier_dic = {"id": "uid"}
        opf.add_element(self.dc_uri + "identifier", text="urn:uuid:" + self.identifier, attrib=identifier_dic,
                        rootElement=self.opf_metadata)
        opf.add_element(self.dc_uri + "creator", text="None", rootElement=self.opf_metadata)
        opf.add_element(self.dc_uri + "contributor", text="None", rootElement=self.opf_metadata)
        opf.add_element(self.dc_uri + "publisher", text="None", rootElement=self.opf_metadata)
        opf.add_element(self.dc_uri + "source", text="None", rootElement=self.opf_metadata)
        date_dic = {"event": "publication"}
        opf.add_element(self.dc_uri + "date", text=f"{strftime('%Y-%m-%d')}", rootElement=self.opf_metadata, nsmap=date_dic)
        opf.add_element(self.dc_uri + "rights", text="None", rootElement=self.opf_metadata)

        self.opf_manifest = opf.add_element("manifest")
        spine_dic = {"toc": "ncx"}
        self.opf_spine = opf.add_element("spine", attrib=spine_dic)
        self.opf_guide = opf.add_element("guide")
        logging.debug("create notice basic'content.opf' generate fine")
        return opf

    def create_basic_ncx(self):
        ncx_nsmap = {None: "http://www.daisy.org/z3986/2005/ncx/"}
        ncx_dic = {"version": "2005-1"}
        ncx = XMLMaker("ncx", attrib=ncx_dic, nsmap=ncx_nsmap)

        ncx.add_docinfo("public_id", "-//NISO//DTD ncx 2005-1//EN")
        ncx.add_docinfo("system_url", "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd")

        self.ncx_head = ncx.add_element("head")
        meta_dic = {"name": "dtb:uid",
                    "content": f"urn:uuid:{self.identifier}"}
        ncx.add_element("meta", attrib=meta_dic, rootElement=self.ncx_head)
        meta_dic["name"] = "dtb:depth"
        meta_dic["content"] = "1"
        ncx.add_element("meta", attrib=meta_dic, rootElement=self.ncx_head)
        meta_dic["name"] = "dtb:totalPageCount"
        meta_dic["content"] = "0"
        ncx.add_element("meta", attrib=meta_dic, rootElement=self.ncx_head)
        meta_dic["name"] = "dtb:maxPageNumber"
        meta_dic["content"] = "0"
        ncx.add_element("meta", attrib=meta_dic, rootElement=self.ncx_head)
        meta_dic["name"] = "dtb:generator"
        meta_dic["content"] = "pyEPUB"
        ncx.add_element("meta", attrib=meta_dic, rootElement=self.ncx_head)

        docTitle = ncx.add_element("docTitle")
        self.docTitle_text = ncx.add_element("text", rootElement=docTitle)
        self.docTitle_text.text = self.title
        self.ncx_navMap = ncx.add_element("navMap")
        logging.debug("create notice basic'toc.ncx' generate fine")
        return ncx

    def set_styleshteet(self, csstext=None):
        if csstext is None:
            logging.debug("create notice basic'styleshteet.css' generate fine")
            return "body{font-family:sans-serif;}h1,h2,h3,h4{font-family:serif;color:blue;}"
        else:
            self.stylesheet = csstext

    def set_title(self, titile: str):
        self.title = titile
        dc = self.opf_metadata.find(f"{self.dc_uri}title")
        dc.text = titile

    def set_language(self, language: str):
        dc = self.opf_metadata.find(f"{self.dc_uri}language")
        dc.text = language

    def set_identifier(self, identifier=None, isbn=None):
        if isbn is not None:
            identifier_nsmap = {"scheme": "ISBN"}
            XMLMaker.static_add_element(self.dc_uri + "identifier", text=isbn, rootElement=self.opf_metadata,
                                        nsmap=identifier_nsmap)
        if identifier is not None:
            self.identifier = identifier
            dc = self.opf_metadata.find(f"{self.dc_uri}identifier")
            dc.text = identifier
        self.set_ncx_uid(identifier)

    def set_creator(self, creator: str):
        dc = self.opf_metadata.find(f"{self.dc_uri}creator")
        dc.text = creator

    def set_contributor(self, contributor: str):
        dc = self.opf_metadata.find(f"{self.dc_uri}contributor")
        dc.text = contributor

    def set_publisher(self, publisher: str):
        dc = self.opf_metadata.find(f"{self.dc_uri}publisher")
        dc.text = publisher

    def set_source(self, source: str):
        dc = self.opf_metadata.find(f"{self.dc_uri}source")
        dc.text = source

    def set_date(self, date: str):
        dc = self.opf_metadata.find(f"{self.dc_uri}date")
        dc.text = date

    def set_rights(self, rights: str):
        dc = self.opf_metadata.find(f"{self.dc_uri}rights")
        dc.text = rights

    def saveEPUB(self, savepath=None):
        if not savepath:
            savepath = ""
        elif not savepath.endswith(("/", "\\")):
            savepath += "/"
        self.create_mimetype(savepath)
        container_path = savepath + "META-INF"
        if not os.path.exists(container_path):
            os.mkdir(container_path)
        self.container.saveXML("container.xml", path=container_path)

        opf_path = savepath + "OEBPS"
        if not os.path.exists(opf_path):
            os.mkdir(opf_path)
        with open(opf_path + "/stylesheet.css", "w") as style:
            style.write(self.stylesheet)
        self.opf.saveXML("content.opf", path=opf_path)
        self.ncx.saveXML("toc.ncx", path=opf_path)
        for file in self.files_list:
            self.copyfile(file, opf_path + "/" + os.path.basename(file))

        img_path = opf_path + "/images"
        if not os.path.exists(img_path):
            os.mkdir(img_path)
        for file in self.images_list:
            self.copyfile(file, img_path + "/" + os.path.basename(file))

    def add_opf_meta(self, name, content):
        XMLMaker.static_add_element(name, text=content, rootElement=self.opf_metadata)

    def add_opf_item(self, href: str, id=None, mediatype=None, properties=None):
        if mediatype is None:
            try:
                mediatype = href.split(".")[-1]
                if mediatype in ("html", "xml", "xhtml"):
                    mediatype = "application/xhtml+xml"
                elif mediatype in ("jpg", "jpeg", "png", "gif"):
                    mediatype = "image/" + mediatype
                else:
                    mediatype = "text/" + mediatype
            except:
                mediatype = "text/txt"
        logging.info(f"file '{href}' add, mediatype is {mediatype}")
        if id is None:
            self.item_id += 1
            id = f"item{self.item_id}"

        item_dic = {"id": id,
                    "href": href,
                    "media-type": mediatype
                    }
        if properties is not None:
            item_dic.update({"properties": properties})
        XMLMaker.static_add_element("item", attrib=item_dic, rootElement=self.opf_manifest)

    def add_opf_spine(self, idref: str, linear=None):
        itemref_dic = {"idref": idref}
        if linear is not None:
            itemref_dic["linear"] = str(linear)
        XMLMaker.static_add_element("itemref", attrib=itemref_dic, rootElement=self.opf_spine)

    def add_opf_guide(self, href: str, title: str, type: str):
        reference_dic = {"href": href,
                         "title": title,
                         "type": type}
        XMLMaker.static_add_element("reference", attrib=reference_dic, rootElement=self.opf_guide)

    def add_ncx_navPoint(self, src: str, text: str, playOrder=None, lastnavpoint=None):
        if lastnavpoint is None:
            lastnavpoint = self.ncx_navMap
        if playOrder is None:
            playOrder = str(self.playOrder)
            self.playOrder += 1
        navPoint_dic = {"id": "navpoint" + playOrder,
                        "playOrder": playOrder}
        navPoint = XMLMaker.static_add_element("navPoint", attrib=navPoint_dic, rootElement=lastnavpoint)
        navLabel = XMLMaker.static_add_element("navLabel", rootElement=navPoint)
        XMLMaker.static_add_element("text", text=text, rootElement=navLabel)
        content_dic = {"src": src}
        XMLMaker.static_add_element("content", attrib=content_dic, rootElement=navPoint)
        return navPoint

    def set_ncx_depth(self, depth: int):
        meta = self.ncx_head.find("meta[@name='dtb:depth']")
        meta.attrib.update({"content": str(depth)})

    def set_ncx_totalPageCount(self, totalPageCount: int):
        meta = self.ncx_head.find("meta[@name='dtb:totalPageCount']")
        meta.attrib.update({"content": str(totalPageCount)})

    def set_ncx_generator(self, generator: int):
        meta = self.ncx_head.find("meta[@name='dtb:generator']")
        meta.attrib.update({"content": str(generator)})

    def set_ncx_maxPageNumber(self, maxPageNumber: int):
        meta = self.ncx_head.find("meta[@name='dtb:maxPageNumber']")
        meta.attrib.update({"content": str(maxPageNumber)})

    def set_ncx_uid(self, uid: str):
        meta = self.ncx_head.find("meta[@name='dtb:uid']")
        meta.attrib.update({"content": "urn:uuid:" + str(uid)})

    def copyfile(self, srcfile, dstfile):
        if not os.path.isfile(srcfile):
            logging.warning(f"can not find '{srcfile}'")
            return False
        else:
            fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
            if not os.path.exists(fpath):
                os.makedirs(fpath)  # 创建路径
            shutil.copyfile(srcfile, dstfile)  # 复制文件
            return True

    def add_document_fromlocal(self, filepath: str):
        name = os.path.basename(filepath)
        self.files_list.append(filepath)
        self.filename_list.append(name)
        self.add_opf_item(href=filepath)
        self.add_opf_spine(f"item{self.item_id}")

    def add_css_fromlocal(self, filepath: str):
        name = os.path.basename(filepath)
        self.files_list.append(filepath)
        self.filename_list.append(name)
        self.add_opf_item(href=name)

    def add_image_fromlocal(self, filepath: str, replace=True, iscover=False, linear="no"):
        name = os.path.basename(filepath)
        if self.check_img_exists(name, replace=replace):
            if replace:
                logging.warning(f"add image '{name}' is exists in epub and replaced!")
            else:
                logging.warning(f"add image '{name}' is exists in epub!")
            return None
        else:
            pass
        self.images_list.append(filepath)
        if iscover:
            self.set_coverimgmes(name, linear)
        else:
            self.add_opf_item(href="images/" + name)
            self.add_opf_spine(f"item{self.item_id}")

    def add_image_content(self, name: str, content, replace=True, iscover=False, linear="no"):
        if self.check_img_exists(name, replace=replace):
            if replace:
                logging.warning(f"add image '{name}' is exists in epub and replaced!")
            else:
                logging.warning(f"add image '{name}' is exists in epub!")
            return None
        else:
            pass
        self.filename_list.append(name)
        self.file_content[name] = content
        if iscover:
            self.set_coverimgmes(name, linear)
        else:
            self.add_opf_item(href="images/" + name)
            self.add_opf_spine(f"item{self.item_id}")

    def check_img_exists(self, name, replace=False):
        if self.filename_list.__contains__(name):
            logging.info(f"image {name} is exists")
            if not replace:
                return True
            else:
                exist_file = list(filter(lambda s: s.__contains__(name), self.images_list))
                list(map(lambda s: self.images_list.remove(s), exist_file))
                return True
        else:
            if not replace:
                return False
            else:
                self.filename_list.append(name)
                return False

    def set_coverimgmes(self, name: str, linear="no"):
        if self.opf_metadata.find("meta[@name='cover']"):
            item = self.opf_manifest.find("item[@id='cover]")
            item.attrib["href"] = "images/" + name
            if linear is not None:
                itemref = self.opf_spine.find("itemref[@id='cover']")
                itemref.attrib["linear"] = linear
        else:
            self.add_opf_meta("cover", "cover")
            self.add_opf_item(href="images/" + name, id="cover")
            self.add_opf_spine("cover", linear=linear)


# epub = EPUBMarker("machine learning")
# epub.set_creator("pyepub")
# epub.add_document_fromlocal("content.html")
# epub.add_opf_guide("content.html", "content", "cover")
# epub.add_image_fromlocal("file/test.jpg", iscover=True)
# epub.saveEPUB("epubBook")