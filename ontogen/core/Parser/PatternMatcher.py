import re
from pymystem3 import Mystem

from ontogen.models import Pattern
from ontogen.core.constants import MATCHED_TEXT_ATTR, MATCH_START_ATTR


class PatternMatcher:
    def __init__(self):
        self.analyzer = Mystem()
        self.known_issues = {
            'гайк': 'гайка'
        }

    def parse_text_from_file(self, filename, patterns):
        with open(filename, 'r', encoding='utf8') as source:
            text = source.read()
        return self.parse_text(text, patterns)

    def parse_text(self, text, patterns):
        text = self.preprocess_text(text)
        results = DictSet()
        for pattern in patterns:
            results.add_range(self.apply_pattern(text, pattern))

        results.items.sort(key=lambda item: item[MATCH_START_ATTR])

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
        analysis = self.analyzer.analyze(text)
        return self.format_analysis(analysis)

    def format_analysis(self, analysis):
        strings = []
        for item in analysis:
            if 'analysis' in item:
                gramar = next(iter(
                    re.findall(r'(\w+)', self.get_gr(item) or "") or []), "")
                lex = self.get_lex(item)
                if lex in self.known_issues:
                    lex = self.known_issues[lex]

                strings.append(lex + '<' + gramar + '>')
            else:
                strings.append(item['text'])
        return ''.join(strings)

    @staticmethod
    def apply_pattern(text, pattern):
        regex = re.compile(pattern['regex'])
        matches = [(pattern['mappings'].format(**match.groupdict()), match)
                   for match in regex.finditer(text)]
        results = []
        for mapping, match in matches:
            items = [
                (MATCHED_TEXT_ATTR, match.group(0).strip()),
                (MATCH_START_ATTR, match.start(0)),
            ]
            
            for pair in mapping.split(Pattern.MAPPING_SEPARATOR):
                name, value = pair.split('=')

                # clear mapping
                for opt_arg in re.findall(r'(\[.*?\])', value):
                    if 'None' in opt_arg:
                        target = ""
                    else:
                        target = opt_arg.lstrip('[').rstrip(']')
                    value = value.replace(opt_arg, target)

                items.append((name, value))
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


class DictSet:
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
