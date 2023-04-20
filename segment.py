#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import random
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image, ImageDraw
import common
import bs4

import requests
import shutil
import setting


TRANSPARENCY = .25  # Degree of transparency, 0-100%
OPACITY = int(255 * TRANSPARENCY)

class Segment:
    def __init__(self, html_file_name=None):
        options = Options()
        # options.binary_location = setting.CHROME_BINARY_LOCATION
        options.add_argument('--headless')
        # self.browser = webdriver.Chrome(chrome_options=options)
        # self.browser.set_window_size(setting.SCREEN_WIDTH, 800)  # set the window size that you need
        self.parser = HTMLParser()
        #read html file from html_file_name
        if html_file_name is not None:
            with open(html_file_name, 'r', encoding="utf-8", errors="ignore") as f:
                self.html_file = f.read()
        else:
            self.html_file = None
        self.json_data = None

    def segment(self, url, output_folder="output", is_output_images=False):
        self.url = url
        self.output_folder = self.remove_slash(output_folder)
        self.log = common.log()

        self.log.write("Crawl HTML Document from %s" % self.url)
        self.__crawler()

        self.log.write("Run Pruning on %s" % self.url)
        self.__pruning()
        self.log.write("Run Partial Tree Matching on %s" % self.url)
        self.__partial_tree_matching()
        self.log.write("Run Backtracking on %s" % self.url)
        self.__backtracking()

        self.log.write("Output Result JSON File on  %s" % self.url)
        self.__output()

        # if is_output_images:
        #     self.log.write("Output Images on  %s" % self.url)
        #     self.__output_images()
        #     self.drawAllBoundingBox(drawSegment=True, drawRecord=False)
        #     self.drawAllBoundingBox(drawSegment=False, drawRecord=True)
        #     self.drawAllBoundingBox(drawSegment=True, drawRecord=True)
        # self.log.write("Finished on  %s" % self.url)

    def __crawler(self):
        self.soup = BeautifulSoup(self.html_file, 'html.parser')

    def __pruning(self):
        tagbody = self.soup.find("body")
        tagbody["lid"] = str(-1)
        tagbody["sn"] = str(1)
        self.allnodes = [tagbody]
        i = 0
        while len(self.allnodes) > i:
            children = []
            for child in self.allnodes[i].children:
                if isinstance(child, bs4.element.Tag) and is_visible(child):
                    children.append(child)
            sn = len(children)

            for child in children:
                child["lid"] = str(i)
                child["sn"] = str(sn)
                self.allnodes.append(child)
            i += 1
        pass

    def __partial_tree_matching(self):
        self.blocks = []

        lid_old = -2

        i = 0
        while i < len(self.allnodes):

            node = self.allnodes[i]

            if 'extracted' in node.attrs:
                i += 1
                continue
            sn, lid = int(node["sn"]), int(node["lid"])

            if lid != lid_old:
                max_window_size = int(sn / 2)
                lid_old = lid

            for ws in range(1, max_window_size + 1):

                pew, cew, new = [], [], []

                for wi in range(i - ws, i + 2 * ws):

                    if wi >= 0 and wi < len(self.allnodes) and int(self.allnodes[wi]["lid"]) == lid:
                        cnode = self.allnodes[wi]
                        if wi >= i - ws and wi < i:
                            pew.append(cnode)
                        if wi >= i and wi < i + ws:
                            cew.append(cnode)
                        if wi >= i + ws and wi < i + 2 * ws:
                            new.append(cnode)

                        pass

                isle = self.__compare_nodes(pew, cew)
                isre = self.__compare_nodes(cew, new)

                if isle or isre:
                    self.blocks.append(cew)
                    i += ws - 1
                    max_window_size = len(cew)
                    self.__mark_extracted(cew)
                    break
            i += 1
        pass

    def __mark_extracted(self, nodes):
        for node in nodes:
            node["extracted"] = ""
            lid = node["lid"]
            parent = node
            while parent.parent is not None:
                parent = parent.parent
                parent["extracted"] = ""
                parent["sid"] = lid

            nodecols = [node]
            for nodecol in nodecols:
                for child in nodecol.children:
                    if isinstance(child, bs4.element.Tag):
                        nodecols.append(child)
                nodecol["extracted"] = ""

    def __compare_nodes(self, nodes1, nodes2):
        if len(nodes1) == 0 or len(nodes2) == 0:
            return False

        return self.__get_nodes_children_structure(nodes1) == self.__get_nodes_children_structure(nodes2)
        pass

    def __get_nodes_children_structure(self, nodes):
        structure = []
        for node in nodes:
            childStruct = self.__get_node_children_structure(node)
            # if last node has the same name, we dont need to add it
            if len(structure) > 0 and structure[-1] == childStruct:
                continue
            else:
                structure.append(childStruct)
        return structure

    def __get_node_children_structure(self, node):
        nodes = [node]
        structure = []
        for node in nodes:
            for child in node.children:
                if isinstance(child, bs4.element.Tag):
                    nodes.append(child)
            # if last node has the same name, we dont need to add it
            if len(structure) > 0 and structure[-1] == node.name:
                continue
            else:
                structure.append(node.name)
        return structure

    def __backtracking(self):

        for node in self.allnodes:
            if (node.name != "body") and (node.parent is not None) and ('extracted' not in node.attrs) and (
                    'extracted' in node.parent.attrs):
                self.blocks.append([node])
                self.__mark_extracted([node])
        pass

    def __get_element(self, node):
        # for XPATH we have to count only for nodes with same type!
        length = 1
        for previous_node in list(node.previous_siblings):
            if isinstance(previous_node, bs4.element.Tag) and previous_node.name == node.name:
                length += 1
        return '%s[%s]' % (node.name, length)
    
    def __get_css_selector(self, node):
        path = [self.__get_element(node)]
        for parent in node.parents:
            if parent.name == "[document]":
                break
            path.insert(0, self.__get_element(parent))
        return ' > '.join(path)

    def __get_css_background_image_urls(self, node):
        nodes = [node]
        image_urls = []
        structure = ""
        for node in nodes:
            for child in node.children:
                if isinstance(child, bs4.element.Tag):
                    nodes.append(child)
        for node in nodes:
            try:
                css_selector = self.__get_css_selector(node)
                url = self.browser.find_element_by_css_selector(css_selector).value_of_css_property("background-image")
                if url != "none":
                    url = url.replace('url(', '').replace(')', '').replace('\'', '').replace('\"', '')
                    url = urljoin(self.url, url)
                    image_urls.append(url)
            except:
                pass
        return image_urls

    def __get_xpath(self, node):
        path = [self.__get_element(node)]
        for parent in node.parents:
            if parent.name == "[document]":
                break
            path.insert(0, self.__get_element(parent))
        # xpath = '/'.join(path)
        # input("xpath: " + xpath)
        return '/'+'/'.join(path)

    def __rgba2RGBA(self, rgba):
        try:
            rgba = rgba.replace("rgba(", "").replace(")", "")
            (R, G, B, A) = tuple(rgba.split(","))
            return int(R), int(G), int(B), float(A)
        except:
            return 0, 0, 0, 0

    def __get_css_background_color(self, node):
        nodes = [node]
        for p in node.parents:
            nodes.append(p)

        (R, G, B) = (255, 255, 255)
        for node in nodes:
            try:
                css_selector = self.__get_css_selector(node)
                color = self.browser.find_element_by_css_selector(css_selector).value_of_css_property(
                    "background-color")

                Rn, Gn, Bn, A = self.__rgba2RGBA(color)

                if A == 1:
                    (R, G, B) = (Rn, Gn, Bn)
                    break
            except:
                pass
        return R, G, B

    def __output(self):

        segids = []
        rid = 0
        count = 0
        segs = dict()
        for i, block in enumerate(self.blocks):
            # texts
            texts, images, links, cssselectors = [], [], [], []
            xpaths = []

            for node in block:
                cssselectors.append(self.__get_css_selector(node))
                xpaths.append(self.__get_xpath(node))

            lid = block[0]["lid"]

            if lid not in segids:
                segids.append(lid)
            sid = str(segids.index(lid))

            if sid not in segs:
                segs[sid] = {"segment_id": int(sid), "xpath": self.__get_xpath(block[0].parent), "records": []}

            segs[sid]["records"].append(
                {"record_id": rid, "xpath": xpaths})
            rid += 1

        self.json_data = dict()
        self.json_data["segments"] = [value for key, value in segs.items()]
        self.json_data["url"] = self.url
        # self.json_data["title"] = self.browser.title

        common.save_json(self.output_folder + "/result.json", self.json_data, encoding=setting.OUTPUT_JSON_ENCODING)

        return self.json_data
    
    def remove_slash(self, path):
        for i in range(len(path)):
            if path.endswith('/'):
                path = path[:-1]
            if path.endswith('\\'):
                path = path[:-1]
        return path


def normalize_xpath(xpath):
    tags = xpath.split("/")[1:]
    for i, tag in enumerate(tags):
        if "[" in tag:
            tag_name, index = tag.split("[")
            tags[i] = tag_name.upper() + "[" + index
        else:
            tags[i] = tag.upper() + "[1]"
    result = "/" + "/".join(tags)
    return result
                

def is_visible(child):
    if child.get('style') and 'display:none' in child['style']:
        return False
    # Check if the Tag has visibility:hidden set
    elif child.get('style') and 'visibility:hidden' in child['style']:
        return False
    # Check if the Tag has opacity:0 set
    elif child.get('style') and 'opacity:0' in child['style']:
        return False
    # Check if the Tag has hidden attribute set to true
    elif child.get('hidden') and child['hidden'] == 'true':
        return False
    else:
        return True