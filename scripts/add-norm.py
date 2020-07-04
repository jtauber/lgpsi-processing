#!/usr/bin/env python3

"""
converts the textpart-per-paragraph to textpart-per-sentence.
"""

from utils import print_interlinear

from greek_normalisation.normalise import Normaliser, Norm

config = (
    Norm.GRAVE
    | Norm.ELISION
    | Norm.MOVABLE
    | Norm.EXTRA
    | Norm.PROCLITIC
    | Norm.ENCLITIC
)


def format_flags(flags):
    s = ""
    if flags & Norm.PROCLITIC:
        s += "p"
    if flags & Norm.ENCLITIC:
        s += "n"
    if flags & Norm.GRAVE:
        s += "g"
    if flags & Norm.EXTRA:
        s += "x"
    if flags & Norm.ELISION:
        s += "l"
    if flags & Norm.MOVABLE:
        s += "m"

    if s == "":
        s = "."

    return s


normalise = Normaliser(config).normalise

for chapter_num in range(1, 20):
    input_filename = f"text/lgpsi.sent.{chapter_num:03d}.txt"
    output_filename = f"analysis/lgpsi.sent.{chapter_num:03d}.norm.txt"

    with open(input_filename) as f, open(output_filename, "w") as g:
        for line in f:
            line = line.strip()
            ref, *text = line.split()
            text_list = [f"{ref}.text", *text]
            norm = [f"{ref}.norm"]
            flags = [f"{ref}.flags"]
            for token in text:
                norm_token, norm_flags = normalise(token.strip(",.;·«»()"))
                norm.append(norm_token)
                flags.append(format_flags(norm_flags))

            print_interlinear([text_list, flags, norm], g)
