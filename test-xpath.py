from lxml import html

# Load the HTML file
filename = "000000/dom.html"
with open(filename, 'r') as f:
    content = f.read()

# Parse the HTML content
tree = html.fromstring(content)

# Get the element you want to find the XPath for
element = tree.xpath('//*')[0]

# Get the XPath for the element
xpath = tree.getpath(element)
print(xpath)
