import json
import os.path
import sys

import requests


class Morpheus:

    ENDPOINT = "http://services.perseids.org/bsp/morphologyservice/analysis/word"

    def __init__(self, cache_filename):
        self.cache_filename = cache_filename
        self.cache = {}
        self.calls = 0
        self.cache_hits = 0

    def __enter__(self):
        self.load_cache()
        return self

    def __exit__(self, type, value, tb):
        self.save_cache()

    def load_cache(self):
        if os.path.exists(self.cache_filename):
            print("loading Morpheus cache...", end="", file=sys.stderr)
            with open(self.cache_filename) as f:
                self.cache = json.load(f)
            print(f"done with {len(self.cache)} items.", file=sys.stderr)
        else:
            print("No cache file so will create on save.")

    def save_cache(self):
        print("saving Morpheus cache...", end="", file=sys.stderr)
        with open(self.cache_filename, "w") as f:
            json.dump(self.cache, f)
        print(
            f"done with {len(self.cache)} items after {self.calls} calls"
            f" and {self.cache_hits} cache hits.",
            file=sys.stderr,
        )

    def lookup(self, form, **config):
        if form in self.cache:
            cache_hit = True
            self.cache_hits += 1
            lemmas = self.cache[form]
        else:
            lemmas = []
            cache_hit = False
            params = dict(word=form, **config)
            headers = dict(Accept="application/json")
            response = requests.get(self.ENDPOINT, params=params, headers=headers)
            self.calls += 1
            if response.ok:
                body = (
                    response.json().get("RDF", {}).get("Annotation", {}).get("Body", [])
                )
                if not isinstance(body, list):
                    body = [body]
            else:
                body = []

            for item in body:
                value = item["rest"]["entry"]["dict"]["hdwd"]["$"]
                if value == str(value):
                    lemmas.append(value)

            self.cache[form] = lemmas

        return lemmas, cache_hit
