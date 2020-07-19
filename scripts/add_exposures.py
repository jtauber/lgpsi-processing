#!/usr/bin/env python3

"""
adds exposure counts for both lemmas and normalized forms to the interlinear.
"""

from collections import Counter

from utils import print_interlinear

seen_norm = Counter()
seen_lemma = Counter()

for chapter_num in range(1, 20):
    input_filename = f"analysis/lgpsi.sent.{chapter_num:03d}.lemma.txt"
    output_filename = f"analysis/lgpsi.sent.{chapter_num:03d}.exposures.txt"

    with open(input_filename) as f, open(output_filename, "w") as g:
        for line in f:

            if ".text" in line:
                text_list = line.strip().split()

            if ".norm" in line:
                ref = line.split(".norm")[0]
                norm_list = line.strip().split()
                normexp_list = [f"{ref}.normexp"]

                for norm in norm_list[1:]:
                    seen_norm[norm] += 1
                    normexp_list.append(str(seen_norm[norm]))

            if ".flags" in line:
                flags_list = line.strip().split()

            if ".lemma" in line:
                lemma_list = line.strip().split()
                ref = line.split(".lemma")[0]
                lemmaexp_list = [f"{ref}.lemmaexp"]

                for lemma in lemma_list[1:]:
                    seen_lemma[lemma] += 1
                    lemmaexp_list.append(str(seen_lemma[lemma]))

                print_interlinear([text_list, norm_list, flags_list, lemma_list, normexp_list, lemmaexp_list], g)
