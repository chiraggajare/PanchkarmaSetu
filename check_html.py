from html.parser import HTMLParser
import sys

class MyHTMLParser(HTMLParser):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.tags = []
        self.void_elements = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
        
    def handle_starttag(self, tag, attrs):
        if tag not in self.void_elements:
            self.tags.append((tag, self.getpos()))
            
    def handle_endtag(self, tag):
        if tag not in self.void_elements:
            if not self.tags:
                print(f"[{self.filename}] Unmatched end tag </{tag}> at line {self.getpos()[0]}")
            else:
                last_tag, pos = self.tags.pop()
                if last_tag != tag:
                    print(f"[{self.filename}] Unmatched end tag </{tag}> at line {self.getpos()[0]} (expected </{last_tag}> from line {pos[0]})")
                    # Try to recover by popping again if it matches the one before
                    if len(self.tags) > 0 and self.tags[-1][0] == tag:
                        self.tags.pop()

for file in sys.argv[1:]:
    parser = MyHTMLParser(file)
    with open(file, "r") as f:
        parser.feed(f.read())
    for tag, pos in parser.tags:
        print(f"[{file}] Unclosed start tag <{tag}> at line {pos[0]}")
