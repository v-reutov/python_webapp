import re
from pymystem3 import Mystem

from ontogen.models import Pattern

class PatternMatcher:
    def __init__(self):
        self.analyzer = Mystem()

    def parse_text_from_file(self, filename, patterns):
        with open(filename, 'r', encoding='utf8') as source:
            text = source.read()
        return self.parse_text(text, patterns)

    def parse_text(self, text, patterns):
        text = self.preprocess_text(text)
        results = DictSet()
        for pattern in patterns:
            results.add_range(self.apply_pattern(text, pattern))

        return results.items

    def match(self, source_text, pattern):
        matches = DictSet()
        for line in source_text:
            text = self.preprocess_text(line)
            for match in self.apply_pattern(text, pattern):
                matches.add(match)

        return matches.items

    def match_from_file(self, filename, pattern):
        source = open(filename, encoding='utf8')
        matches = self.match(source.readlines(), pattern)
        source.close()
        return matches

    def preprocess_text(self, text):
        text = text.strip().replace('\n', ' ').replace('  ', ' ')
        analyzis = self.analyzer.analyze(text)
        return self.format_analyzis(analyzis)

    def format_analyzis(self, analyzis):
        strings = []
        for item in analyzis:
            if 'analysis' in item:
                gramar = next(iter(
                    re.findall(r'(\w+)', self.get_gr(item) or "") or []), "")
                strings.append(self.get_lex(item) + '<' + gramar + '>')
            else:
                strings.append(item['text'])
        return ''.join(strings)

    @staticmethod
    def apply_pattern(text, pattern):
        def clear_mapping(mapping):
            for opt_arg in re.findall(r'(\[.*?\])', mapping):
                if 'None' in opt_arg:
                    target = ""
                else:
                    target = opt_arg.lstrip('[').rstrip(']')
                mapping = mapping.replace(opt_arg, target)
            return mapping

        regex = re.compile(pattern['regex'])
        matches = [(pattern['mappings'].format(**match.groupdict()), match.group(0))
                   for match in regex.finditer(text)]
        results = []
        for match, matched_text in matches:
            items = [('matched_text', matched_text)]
            
            for pair in match.split(Pattern.MAPPING_SEPARATOR):
                name, mapping = pair.split('=')
                items.append((name, clear_mapping(mapping)))
            results.append(dict(items))
        return results

    @staticmethod
    def get_item(word, item):
        try:
            return word["analysis"][0][item]
        except (TypeError, KeyError, IndexError):
            return None

    def get_lex(self, word):
        return self.get_item(word, "lex") or word['text']

    def get_gr(self, word):
        return self.get_item(word, "gr")


class DictSet():
    def __init__(self):
        self.items = []

    def add(self, new_item):
        if not self.contains(new_item):
            self.items.append(new_item)

    def add_range(self, new_items):
        for new_item in new_items:
            self.add(new_item)

    def contains(self, new_item):
        for item in self.items:
            if item == new_item:
                return True
        return False
