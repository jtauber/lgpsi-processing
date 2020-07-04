#!/usr/bin/env python3

"""
converts the original files from Seumas into a textpart-per-paragraph format.
"""

import unicodedata


for chapter_num in range(1, 20):
    input_filename = f"orig/{chapter_num:03d}.md"
    output_filename = f"text/lgpsi.para.{chapter_num:03d}.txt"

    with open(input_filename) as f, open(output_filename, "w") as g:
        chapter = None
        section = None
        for line in f:
            line = unicodedata.normalize("NFC", line.strip())
            if line == "":  # blank line
                pass
            elif line.startswith("# "):
                assert chapter is None
                chapter = chapter_num
                section = 0
                paragraph = 0
                print(f"{chapter:03d}.{section}.{paragraph:02d}", line.split(maxsplit=1)[1], file=g)
            elif line.startswith("## "):
                assert chapter is not None
                section += 1
                paragraph = 0
                print(f"{chapter:03d}.{section}.{paragraph:02d}", line.split(maxsplit=1)[1], file=g)
            else:
                assert chapter is not None
                assert section is not None
                paragraph += 1
                print(f"{chapter:03d}.{section}.{paragraph:02d}", line, file=g)
