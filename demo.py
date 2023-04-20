from segment import Segment
import datetime
if __name__ == "__main__":
    spliter = Segment("000000/dom.html")
    print(datetime.datetime.now())
    localUrl = "file:///Users/hieu.huynh/Documents/Projects/web-segmentation/web-segment/web.archive.org.html"
    # spliter.segment(url="https://katalon.com/testops",
    #                 output_folder="data/katalon", is_output_images=True)
    # spliter.segment(url="https://www.ups.com/us/en/Home.page",
    #                 output_folder="data/ups", is_output_images=True)
    # spliter.segment(url="https://www.amazon.com/",
    #                 output_folder="data/amazon", is_output_images=True)
    # spliter.segment(url="https://www.walmart.com/",
    #                 output_folder="data/walmart", is_output_images=True)
    # spliter.segment(url="https://www.target.com/",
    #                 output_folder="data/target", is_output_images=True)
    # spliter.segment(url="https://www.bestbuy.com/",
    #                 output_folder="data/bestbuy", is_output_images=True)
    # spliter.segment(url="https://www.ebay.com/",
    #                 output_folder="data/ebay", is_output_images=True)
    # spliter.segment(url="https://github.com/triquocle/DOM-Trees-Comparator",
    #                 output_folder="data/github", is_output_images=True)
    spliter.segment(url="",
                    output_folder="data/wikipedia")
    print(spliter.json_data)
    # spliter.segment(url=localUrl,
    #                 output_folder="data/local", is_output_images=True)
    print(datetime.datetime.now())
