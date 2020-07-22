#!/usr/bin/env python3

"""
generates cummulative data about each chapter
"""

from collections import Counter, defaultdict
import json

from pyuca import Collator
coll = Collator()


cumulative_lemma_last_seen = {}
cumulative_lemma_form_last_seen = {}
cumulative_lemma_count = Counter()
cumulative_lemma_form_count = defaultdict(Counter)

for chapter_num in range(1, 20):
    input_filename = f"analysis/lgpsi.sent.{chapter_num:03d}.lemma.txt"
    output_filename = f"analysis/lgpsi.{chapter_num:03d}.json"

    chapter_lemma_count = Counter()
    chapter_lemma_form_count = defaultdict(Counter)

    with open(input_filename) as f:
        for line in f:

            if ".norm " in line:
                norm_list = line.strip().split()

            if ".lemma " in line:
                lemma_list = line.strip().split()

                for norm, lemma in zip(norm_list[1:], lemma_list[1:]):
                    chapter_lemma_count[lemma] += 1
                    chapter_lemma_form_count[lemma][norm] += 1

    data = {}

    for lemma in sorted(chapter_lemma_count.keys() | cumulative_lemma_count.keys(), key=coll.sort_key):
        lemma_data = {}
        lemma_data["cumulative_last_seen"] = cumulative_lemma_last_seen.get(lemma, 0)
        lemma_data["cumulative_lemma_count"] = cumulative_lemma_count[lemma]
        lemma_data["chapter_lemma_count"] = chapter_lemma_count[lemma]
        lemma_data["forms"] = {}

        for form in cumulative_lemma_form_count[lemma].keys() | chapter_lemma_form_count[lemma].keys():
            form_data = {}
            form_data["cumulative_lemma_form_last_seen"] = cumulative_lemma_form_last_seen.get((lemma, form), 0)
            form_data["cumulative_lemma_form_count"] = cumulative_lemma_form_count[lemma][form]
            form_data["chapter_lemma_form_count"] = chapter_lemma_form_count[lemma][form]
            lemma_data["forms"][form] = form_data
        data[lemma] = lemma_data

    with open(output_filename, "w") as g:
        json.dump(data, g, ensure_ascii=False)

    for lemma in chapter_lemma_count:
        cumulative_lemma_last_seen[lemma] = chapter_num
        for form in chapter_lemma_form_count[lemma]:
            cumulative_lemma_form_last_seen[(lemma, form)] = chapter_num
            cumulative_lemma_form_count[lemma][form] += chapter_lemma_form_count[lemma][form]
        cumulative_lemma_count[lemma] += chapter_lemma_count[lemma]
