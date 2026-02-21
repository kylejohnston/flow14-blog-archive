#!/usr/bin/env python3
"""
Cleanup script for blog-archive static site.
Removes dead WordPress and Google Analytics artifacts from all HTML files.
"""

import os
import re
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))

# Patterns to remove entirely (matched as whole lines, stripped with newline)
LINE_PATTERNS = [
    # WordPress XFN profile link
    re.compile(r'^\t*<link rel=[\'"]profile[\'"]\s+href=[\'"]https://gmpg\.org/xfn/11[\'"]\s*/?\s*>\n', re.MULTILINE),
    # DNS prefetch to s.w.org (both correct spelling and the typo "prefetich")
    re.compile(r'^<link rel=[\'"]dns-prefetch[\'"] href=[\'"]//s\.w\.org[\'"]\s*/>\n', re.MULTILINE),
    re.compile(r"^<link rel='dns-prefetich' href='//s\.w\.org' />\n", re.MULTILINE),
    # WordPress shortlink
    re.compile(r"^<link rel='shortlink' href='[^']*'\s*/>\n", re.MULTILINE),
    # WordPress oEmbed discovery links
    re.compile(r'^<link rel="alternate" type="application/json\+oembed"[^\n]*\n', re.MULTILINE),
    re.compile(r'^<link rel="alternate" type="text/xml\+oembed"[^\n]*\n', re.MULTILINE),
]

# Multi-line block to remove: Google Analytics tag
# Matches from the comment through the closing </script>, tolerating any
# mix of tabs and spaces for indentation inside the block.
GA_BLOCK = re.compile(
    r'[ \t]*<!-- Global site tag \(gtag\.js\) - Google Analytics -->\n'
    r'[ \t]*<script[^>]*></script>\n'   # async loader (inline self-close)
    r'[ \t]*<script>\n'                 # opening of config script
    r'(?:[ \t]*[^\n]*\n|\n)*?'          # any lines inside (non-greedy)
    r'[ \t]*</script>\n',               # closing tag
    re.MULTILINE
)

html_files = glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
modified = 0

for path in sorted(html_files):
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    content = original

    # Remove GA block
    content = GA_BLOCK.sub('', content)

    # Remove line-level artifacts
    for pattern in LINE_PATTERNS:
        content = pattern.sub('', content)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        modified += 1

print(f"Done. Modified {modified} of {len(html_files)} HTML files.")
