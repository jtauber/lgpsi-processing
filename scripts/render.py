#!/usr/bin/env python3

from collections import defaultdict

import json

from pyuca import Collator
coll = Collator()

def html_header():
    header = """\
<head>
  <meta charset="utf-8">
  <style>
    body {
      font-size: 14pt;
      line-height: 1.6;
      max-width: 800px;
      margin: 50px auto;
    }
    nav a {
      font-family: sans-serif;
      font-size: 11pt;
      color: #69C;
      text-decoration: none;
    }
    nav a:hover {
      text-decoration: underline;
    }
    span.ref {
      font-family: sans-serif;
      font-size: 10pt;
      color: #69C;
    }
    span.new-lemma {
      border-bottom: 4px solid #0C3;
    }
    span.new-form {
      border-bottom: 2px dotted #0C3;
    }

    div.lemma-entry {
      margin-top: 2em;
    }
    div.lemma-entry h2 {
      margin: 0;
    }
    table.lemma-data {
      background: #EEE;
    }
    table.forms {
      margin-top: 1em;
    }
    table th {
      text-align: left;
      padding: 2px 10px;
    }
    table td {
      padding: 2px 10px;
    }
  </style>
</head>
<nav>
"""

    header += f'<div>'

    for chapter_num in range(1, 20):
        header += f'<a href="lgpsi_{chapter_num:03d}.html">{chapter_num:03d}</a>\n'

    header += f'</div><div>'

    for chapter_num in range(1, 20):
        header += f'<a href="lgpsi_{chapter_num:03d}_report.html">{chapter_num:03d}_report</a>\n'

    header += f'</div><div><a href="lgpsi_lemma_index.html">alphabetical index</a>\n'
    header += f'| <a href="lgpsi_ref_index.html">index by ref</a></div>\n'
    header += f'</nav>\n'

    return header


class HTMLRenderer:

    def __init__(self):

        self.header = html_header()
        self.index_by_ref = defaultdict(list)
        self.index_by_lemma = {}

    def render_all(self):

        self.render_chapters()
        self.render_ref_index()
        self.render_lemma_index()
        self.render_chapter_reports()

    def render_chapters(self):

        for chapter_num in range(1, 20):
            input_filename = f"analysis/lgpsi.sent.{chapter_num:03d}.exposures.txt"
            output_filename = f"docs/lgpsi_{chapter_num:03d}.html"

            with open(input_filename) as f, open(output_filename, "w") as g:

                prev_para_ref = None
                text = []

                print(self.header, file=g)

                for line in f:

                    if ".text " in line:
                        text_list = line.strip().split()

                    if ".norm " in line:
                        norm_list = line.strip().split()

                    if ".flags " in line:
                        flags_list = line.strip().split()

                    if ".lemma " in line:
                        lemma_list = line.strip().split()

                    if ".normexp " in line:
                        normexp_list = line.strip().split()

                    if ".lemmaexp " in line:
                        lemmaexp_list = line.strip().split()

                        para_ref = ".".join(line.split(".lemmaexp")[0].split(".")[:3])

                        if para_ref != prev_para_ref:
                            if text:
                                print(" ".join(text), file=g)
                                text = []
                            print(f'<p><span class="ref">{para_ref}</span>', file=g)
                            prev_para_ref = para_ref

                        for token, lemma, normexp, lemmaexp in zip(text_list[1:], lemma_list[1:], normexp_list[1:], lemmaexp_list[1:]):
                            if lemmaexp == "1":
                                text.append(f'<span class="new-lemma">{token}</span>')
                                self.index_by_ref[para_ref].append(lemma)
                            elif normexp == "1":
                                text.append(f'<span class="new-form">{token}</span>')
                            else:
                                text.append(f'{token}')

                print(" ".join(text), file=g)

    def render_ref_index(self):

        output_filename = f"docs/lgpsi_ref_index.html"

        with open(output_filename, "w") as g:

            print(self.header, file=g)

            print("<h1>New Lemma Exposures by Ref</h1>", file=g)
            for ref, lemma_list in self.index_by_ref.items():
                print(f'<div><span class="ref">{ref}</span> {" ".join(lemma_list)}</div>', file=g)
                for lemma in lemma_list:
                    self.index_by_lemma[lemma] = ref

    def render_lemma_index(self):

        output_filename = f"docs/lgpsi_lemma_index.html"

        with open(output_filename, "w") as g:

            print(self.header, file=g)

            print("<h1>New Lemma Exposures Alphabetically</h1>", file=g)
            for lemma in sorted(self.index_by_lemma, key=coll.sort_key):
                print(f'<div>{lemma} <span class="ref">{self.index_by_lemma[lemma]}</span></div>', file=g)

    def render_chapter_reports(self):

        for chapter_num in range(1, 20):
            input_filename = f"analysis/lgpsi.{chapter_num:03d}.json"
            output_filename = f"docs/lgpsi_{chapter_num:03d}_report.html"

            data = json.load(open(input_filename))
            with open(output_filename, "w") as g:

                print(self.header, file=g)

                print(f"<h1>Chapter {chapter_num} Report</h1>", file=g)

                print(f"""
        <table>
          <tr>
            <th>&nbsp;</th>
            <th>Lemma</th>
            <th>Form</th>
          </tr>
          <tr>
            <th>types</th>
            <td>{data['new_lemma_types']} / {data['lemma_types']}</td>
            <td>{data['new_form_types']} / {data['form_types']}</td>
          </tr>
          <tr>
            <th>tokens</th>
            <td>{data['new_lemma_tokens']} / {data['lemma_tokens']}</td>
            <td>{data['new_form_tokens']} / {data['form_tokens']}</td>
          </tr>
        </table>\n      """, file=g)

                for lemma, lemma_data in data["lemmas"].items():

                    print(f'<div class="lemma-entry">', file=g)
                    print(f'<h2>{lemma}</h2>', file=g)
                    print('<table class="lemma-data"><tr>', file=g)
                    if lemma_data["cumulative_last_seen"]:
                        print(f'<td>Last seen chapter: {lemma_data["cumulative_last_seen"]}</td>', file=g)
                        print(f'<td>Count before now: {lemma_data["cumulative_lemma_count"]}</td>', file=g)
                    else:
                        print(f'<td colspan="2">New in this chapter.</td>', file=g)
                    if lemma_data["chapter_lemma_count"]:
                        print(f'<td>Appears {lemma_data["chapter_lemma_count"]} time{"s" if lemma_data["chapter_lemma_count"] > 1 else ""} in this chapter.</td>', file=g)
                    else:
                        print(f'<td>Not in chapter {chapter_num}.</td>', file=g)
                    print('</tr></table>', file=g)

                    print('<table class="forms">', file=g)
                    for form, form_data in lemma_data["forms"].items():
                        print('<tr>', file=g)
                        print(f'<th>{form}</th>', file=g)
                        if form_data["cumulative_lemma_form_last_seen"]:
                            print(f'<td>Last seen chapter: {form_data["cumulative_lemma_form_last_seen"]}</td>', file=g)
                            print(f'<td>Count before now: {form_data["cumulative_lemma_form_count"]}</td>', file=g)
                        else:
                            print(f'<td colspan="2">New in this chapter.</td>', file=g)
                        if form_data["chapter_lemma_form_count"]:
                            print(f'<td>Appears {form_data["chapter_lemma_form_count"]} time{"s" if form_data["chapter_lemma_form_count"] > 1 else ""} in this chapter.</td>', file=g)
                        else:
                            print(f'<td>Not in chapter {chapter_num}.</td>', file=g)
                        print('</tr>', file=g)
                    print('</table>', file=g)

                    print('</div>', file=g)


# renderer = HTMLRenderer()
# renderer.render_all()


class LaTeXRenderer:

    def __init__(self):

        self.header = r"""
\documentclass[a4paper,12pt]{scrartcl}
\begin{document}
"""
        self.trailer = r"""
\end{document}
"""
        self.index_by_ref = defaultdict(list)
        self.index_by_lemma = {}

    def render_all(self):

        self.render_chapters()
        self.render_ref_index()
        self.render_lemma_index()
        self.render_chapter_reports()

    def render_chapters(self):

        for chapter_num in range(1, 20):
            input_filename = f"analysis/lgpsi.sent.{chapter_num:03d}.exposures.txt"
            output_filename = f"tex/lgpsi_{chapter_num:03d}.tex"

            with open(input_filename) as f, open(output_filename, "w") as g:

                prev_para_ref = None
                text = []

                print(self.header, file=g)

                for line in f:

                    if ".text " in line:
                        text_list = line.strip().split()

                    if ".norm " in line:
                        norm_list = line.strip().split()

                    if ".flags " in line:
                        flags_list = line.strip().split()

                    if ".lemma " in line:
                        lemma_list = line.strip().split()

                    if ".normexp " in line:
                        normexp_list = line.strip().split()

                    if ".lemmaexp " in line:
                        lemmaexp_list = line.strip().split()

                        para_ref = ".".join(line.split(".lemmaexp")[0].split(".")[:3])

                        if para_ref != prev_para_ref:
                            if text:
                                print(" ".join(text), file=g)
                                text = []
                            print(f'<p><span class="ref">{para_ref}</span>', file=g)
                            prev_para_ref = para_ref

                        for token, lemma, normexp, lemmaexp in zip(text_list[1:], lemma_list[1:], normexp_list[1:], lemmaexp_list[1:]):
                            if lemmaexp == "1":
                                text.append(f'<span class="new-lemma">{token}</span>')
                                self.index_by_ref[para_ref].append(lemma)
                            elif normexp == "1":
                                text.append(f'<span class="new-form">{token}</span>')
                            else:
                                text.append(f'{token}')

                print(" ".join(text), file=g)

    def render_ref_index(self):

        output_filename = f"tex/lgpsi_ref_index.tex"

        with open(output_filename, "w") as g:

            print(self.header, file=g)

            print("<h1>New Lemma Exposures by Ref</h1>", file=g)
            for ref, lemma_list in self.index_by_ref.items():
                print(f'<div><span class="ref">{ref}</span> {" ".join(lemma_list)}</div>', file=g)
                for lemma in lemma_list:
                    self.index_by_lemma[lemma] = ref

            print(self.trailer, file=g)

    def render_lemma_index(self):

        output_filename = f"tex/lgpsi_lemma_index.tex"

        with open(output_filename, "w") as g:

            print(self.header, file=g)

            print("<h1>New Lemma Exposures Alphabetically</h1>", file=g)
            for lemma in sorted(self.index_by_lemma, key=coll.sort_key):
                print(f'<div>{lemma} <span class="ref">{self.index_by_lemma[lemma]}</span></div>', file=g)

    def render_chapter_reports(self):

        for chapter_num in range(1, 20):
            input_filename = f"analysis/lgpsi.{chapter_num:03d}.json"
            output_filename = f"tex/lgpsi_{chapter_num:03d}_report.tex"

            data = json.load(open(input_filename))
            with open(output_filename, "w") as g:

                print(self.header, file=g)

                print(f"<h1>Chapter {chapter_num} Report</h1>", file=g)

                print(f"""
        <table>
          <tr>
            <th>&nbsp;</th>
            <th>Lemma</th>
            <th>Form</th>
          </tr>
          <tr>
            <th>types</th>
            <td>{data['new_lemma_types']} / {data['lemma_types']}</td>
            <td>{data['new_form_types']} / {data['form_types']}</td>
          </tr>
          <tr>
            <th>tokens</th>
            <td>{data['new_lemma_tokens']} / {data['lemma_tokens']}</td>
            <td>{data['new_form_tokens']} / {data['form_tokens']}</td>
          </tr>
        </table>\n      """, file=g)

                for lemma, lemma_data in data["lemmas"].items():

                    print(f'<div class="lemma-entry">', file=g)
                    print(f'<h2>{lemma}</h2>', file=g)
                    print('<table class="lemma-data"><tr>', file=g)
                    if lemma_data["cumulative_last_seen"]:
                        print(f'<td>Last seen chapter: {lemma_data["cumulative_last_seen"]}</td>', file=g)
                        print(f'<td>Count before now: {lemma_data["cumulative_lemma_count"]}</td>', file=g)
                    else:
                        print(f'<td colspan="2">New in this chapter.</td>', file=g)
                    if lemma_data["chapter_lemma_count"]:
                        print(f'<td>Appears {lemma_data["chapter_lemma_count"]} time{"s" if lemma_data["chapter_lemma_count"] > 1 else ""} in this chapter.</td>', file=g)
                    else:
                        print(f'<td>Not in chapter {chapter_num}.</td>', file=g)
                    print('</tr></table>', file=g)

                    print('<table class="forms">', file=g)
                    for form, form_data in lemma_data["forms"].items():
                        print('<tr>', file=g)
                        print(f'<th>{form}</th>', file=g)
                        if form_data["cumulative_lemma_form_last_seen"]:
                            print(f'<td>Last seen chapter: {form_data["cumulative_lemma_form_last_seen"]}</td>', file=g)
                            print(f'<td>Count before now: {form_data["cumulative_lemma_form_count"]}</td>', file=g)
                        else:
                            print(f'<td colspan="2">New in this chapter.</td>', file=g)
                        if form_data["chapter_lemma_form_count"]:
                            print(f'<td>Appears {form_data["chapter_lemma_form_count"]} time{"s" if form_data["chapter_lemma_form_count"] > 1 else ""} in this chapter.</td>', file=g)
                        else:
                            print(f'<td>Not in chapter {chapter_num}.</td>', file=g)
                        print('</tr>', file=g)
                    print('</table>', file=g)

                    print('</div>', file=g)

renderer = LaTeXRenderer()
renderer.render_all()
