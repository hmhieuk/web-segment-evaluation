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
        # read html file from html_file_name
        if html_file_name is not None:
            with open(html_file_name, 'r', encoding="utf-8", errors="ignore") as f:
                self.html_file = f.read()
        else:
            self.html_file = None
        self.json_data = None

    def segment(self, url, output_folder="output", is_output_images=False, nodes_dict=None, screenshot_file=None):
        self.url = url
        self.output_folder = self.remove_slash(output_folder)
        self.log = common.log()
        self.nodes_dict = nodes_dict
        self.found = 0
        self.not_found = 0
        self.log.write("Crawl HTML Document from %s" % self.url)
        self.__crawler()

        self.log.write("Run Pruning on %s" % self.url)
        self.__pruning()

        self.log.write("Traverse and update bbox on %s" % self.url)
        self.traverse(self.soup.find("body"), '/HTML[1]', "BODY", 1)

        self.log.write("Run Partial Tree Matching on %s" % self.url)
        self.__partial_tree_matching()

        self.log.write("Run Backtracking on %s" % self.url)
        self.__backtracking()
        # self.setIsBlockNode(self.soup.find("body"))

        self.log.write("Output Result JSON File on  %s" % self.url)
        self.__output()
        return self.found, self.not_found

        # if is_output_images:
        #     self.log.write("Output Images on  %s" % self.url)
        #     self.__output_images()
        #     self.drawAllBoundingBox(drawSegment=True, drawRecord=False)
        #     self.drawAllBoundingBox(drawSegment=False, drawRecord=True)
        #     self.drawAllBoundingBox(drawSegment=True, drawRecord=True)
        # self.log.write("Finished on  %s" % self.url)

    def __crawler(self):
        self.soup = BeautifulSoup(self.html_file, 'html.parser')
        [x.extract() for x in self.soup.findAll('script')]

    def __pruning(self):
        tagbody = self.soup.find("body")
        tagbody["lid"] = str(-1)
        tagbody["sn"] = str(1)
        tagbody['isSegment'] = False
        self.allnodes = [tagbody]
        i = 0
        while len(self.allnodes) > i:
            children = []
            for child in self.allnodes[i].children:
                if isinstance(child, bs4.element.Tag) and is_visible(child):
                    child['isSegment'] = False
                    children.append(child)
            sn = len(children)

            for child in children:
                child["lid"] = str(i)
                child["sn"] = str(sn)
                child['isSegment'] = False
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
                self.markBlockNode([node])
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
                url = self.browser.find_element_by_css_selector(
                    css_selector).value_of_css_property("background-image")
                if url != "none":
                    url = url.replace('url(', '').replace(')', '').replace(
                        '\'', '').replace('\"', '')
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
        segs = dict()
        for i, block in enumerate(self.blocks):
            if len(block) == 0:
                continue
            if 'xpath' in block[0].parent.attrs and 'bbox' in block[0].parent.attrs:
                cssselectors = []
                xpaths = []

                for node in block:
                    cssselectors.append(self.__get_css_selector(node))
                    if 'xpath' not in node.attrs:
                        continue
                    xpaths.append(node['xpath'])
                lid = block[0]["lid"]

                if lid not in segids:
                    segids.append(lid)
                sid = str(segids.index(lid))

                if sid not in segs:
                    self.found += 1
                    segs[sid] = {"segment_id": int(
                        sid), "xpath": block[0].parent['xpath'], "bounding_box": block[0].parent['bbox'], 'level': block[0].parent['level'], "records": []}
                    block[0].parent['isSegment'] = True
                segs[sid]["records"].append(
                    {"record_id": rid, "xpath": xpaths})
                rid += 1
            else:
                self.not_found += 1

        self.json_data = dict()
        self.json_data["segments"] = [value for key, value in segs.items()]
        self.json_data["url"] = self.url

        common.save_json(self.output_folder + "/result.json",
                         self.json_data, encoding=setting.OUTPUT_JSON_ENCODING)

        return self.json_data

    def remove_slash(self, path):
        for i in range(len(path)):
            if path.endswith('/'):
                path = path[:-1]
            if path.endswith('\\'):
                path = path[:-1]
        return path

    def update_bbox(self, node, path):
        for child in self.allnodes:
            if child == node:
                child["xpath"] = path
                text = node.get_text()
                if normalize_xpath(path) in self.nodes_dict:
                    child["bbox"] = self.nodes_dict[normalize_xpath(path)][0]
                else:
                    bbox = search_xpath(path, self.nodes_dict, text)
                    if bbox:
                        child["bbox"] = bbox
                    else:
                        return False
                return True
        return False

    def traverse(self, node, parent_path, node_name, node_name_number, level=0):
        node_path = f"{parent_path}/{node_name}[{node_name_number}]"
        updated = self.update_bbox(node, node_path)
        if isinstance(node, bs4.element.Tag):
            counts = {}
            children = node.children
            for child in children:
                if is_visible(child):
                    if isinstance(child, bs4.element.NavigableString):
                        child_name = "text()"
                    elif isinstance(child, bs4.element.Tag):
                        child_name = child.name.upper()

                    counts[child_name] = counts.get(child_name, 0) + 1
                    self.traverse(child, node_path, child_name,
                                  counts[child_name], level+1)
            node['level'] = level

    def setIsBlockNode(self, node):
        if 'isSegment' not in node.attrs:
            node['isSegment'] = False
        if len(list(node.children)) == 0 or node['isSegment']:
            return True
        all_block_nodes = True
        for child in node.children:
            if not isinstance(child, bs4.element.NavigableString):
                child_block_node = self.setIsBlockNode(child)
                all_block_nodes = all_block_nodes and child_block_node
        if all_block_nodes:
            node['isSegment'] = True
            self.blocks.append([node])
            self.markBlockNode([node])
            for child in node.children:
                if isinstance(child, bs4.element.Tag):
                    self.setIsNotBlockNode(child)
        return node['isSegment']

    def setIsNotBlockNode(self, node):
        if len(list(node.children)) == 0:
            return 'isSegment' in node.attrs and node['isSegment']

        for child in node.children:
            if isinstance(child, bs4.element.Tag):
                self.setIsNotBlockNode(child)
        node['isSegment'] = False
        for block in self.blocks:
            if node in block:
                block.remove(node)
        return node['isSegment']

    def markBlockNode(self, nodes):
        for node in nodes:
            node['isSegment'] = True


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
    if isinstance(child, bs4.element.NavigableString):
        return child.strip() != ""
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


def normalize_xpath(xpath):
    # input(xpath)
    tags = xpath.split("/")[1:]
    for i, tag in enumerate(tags):
        if "[" in tag:
            tag_name, index = tag.split("[")
            tags[i] = tag_name.upper() + "[" + index
        else:
            tags[i] = tag.upper() + "[1]"
    result = "/" + "/".join(tags)
    # return result to upper case
    return result.upper()


def search_xpath(xpath, nodes_dict, text):
    posible_nodes = {}
    posible_bboxes = []
    for _xpath, value in nodes_dict.items():
        if _xpath.startswith(xpath):
            posible_bboxes.append(value[0])
    if len(posible_bboxes) > 0:
        merged_bbox = merge_bbox_list(posible_bboxes)
        return merged_bbox

    for _xpath, value in nodes_dict.items():
        # if they have the same length of nodes
        if len(_xpath.split("/")) == len(xpath.split("/")):
            elements = xpath.split("/")
            _elements = _xpath.split("/")
            # filter xpath that has the same skeleton
            same_skeleton = True
            for e, _e in zip(elements, _elements):
                name = e.split("[")[0]
                _name = _e.split("[")[0]
                if name != _name:
                    same_skeleton = False
                    break
            if same_skeleton:
                posible_nodes[_xpath] = value[0]

    if len(posible_nodes) == 1:
        return posible_nodes[list(posible_nodes.keys())[0]]
    elif len(posible_nodes) > 1:
        smallest_distance = distance(xpath, list(posible_nodes.keys())[0])
        smallest_xpath = list(posible_nodes.keys())[0]
        for _xpath in posible_nodes.keys():
            _distance = distance(xpath, _xpath)
            if _distance < smallest_distance:
                smallest_distance = _distance
                smallest_xpath = _xpath
        return nodes_dict[smallest_xpath][0]
    else:
        return None


def distance(xpath1, xpath2):
    ids1 = [int(x.split("[")[1].split("]")[0]) for x in xpath1.split("/")[1:]]
    ids2 = [int(x.split("[")[1].split("]")[0]) for x in xpath2.split("/")[1:]]
    distance = 0
    for i, j, count in zip(ids1, ids2, range(1, len(ids1)+1)):
        distance += abs(i-j) / count
    return distance


def merge_bbox_list(bboxes):
    if len(bboxes) == 1:
        return bboxes[0]
    else:
        return merge_bbox(bboxes[0], merge_bbox_list(bboxes[1:]))


def merge_bbox(bbox1, bbox2):
    # the bbox is a list of 4 values, the first is the x, the second is the y, the third is the width and the fourth is the height
    if 'x' not in bbox1 or 'y' not in bbox1 or 'width' not in bbox1 or 'height' not in bbox1:
        return bbox2
    if 'x' not in bbox2 or 'y' not in bbox2 or 'width' not in bbox2 or 'height' not in bbox2:
        return bbox1
    x1, y1, w1, h1 = bbox1['x'], bbox1['y'], bbox1['width'], bbox1['height']
    x2, y2, w2, h2 = bbox2['x'], bbox2['y'], bbox2['width'], bbox2['height']
    x = min(x1, x2)
    y = min(y1, y2)
    w = max(x1+w1, x2+w2) - x
    h = max(y1+h1, y2+h2) - y

    return {'x': x, 'y': y, 'width': w, 'height': h}

def bbox_coverage_ratio(bbox1, bbox2):
    # the bbox is a list of 4 values, the first is the x, the second is the y, the third is the width and the fourth is the height
    if 'x' not in bbox1 or 'y' not in bbox1 or 'width' not in bbox1 or 'height' not in bbox1:
        return 0
    if 'x' not in bbox2 or 'y' not in bbox2 or 'width' not in bbox2 or 'height' not in bbox2:
        return 0
    x1, y1, w1, h1 = bbox1['x'], bbox1['y'], bbox1['width'], bbox1['height']
    x2, y2, w2, h2 = bbox2['x'], bbox2['y'], bbox2['width'], bbox2['height']
    x = min(x1, x2)
    y = min(y1, y2)
    w = max(x1+w1, x2+w2) - x
    h = max(y1+h1, y2+h2) - y

    return (w*h)/(w1*h1)