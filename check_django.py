import re
import sys

def check_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Check for {% without %} or {{ without }}
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # find single { followed by % or { that isn't matched
        # this is just a very basic check
        for match in re.finditer(r'\{[%{]', line):
            start = match.start()
            if match.group(0) == '{%':
                end = line.find('%}', start)
                if end == -1:
                    print(f"[{filename}:{i+1}] Unclosed {{% in line: {line.strip()}")
            elif match.group(0) == '{{':
                end = line.find('}}', start)
                if end == -1:
                    print(f"[{filename}:{i+1}] Unclosed {{{{ in line: {line.strip()}")

for f in sys.argv[1:]:
    check_file(f)
