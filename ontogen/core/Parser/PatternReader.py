import re


class PatternReader:
    def __init__(self):
        self.patterns = []
        self.token_dictionary = {
            'NP': 'S',
            'VP': 'V',
            'IN': 'PR',
            'ADJ': 'A'
        }

        self.special_tokens = {
            'N': r'\d+',
            ' ': r'\s*'
        }

        self.tokens_to_ignore = [
            'DETAIL'
        ]

        self.special_chars = [
            '(', ')'
        ]
        self.token_pattern = re.compile(r'(?P<token>\w+)<(?P<class>\w+)>')
        self.optional_token_pattern = re.compile(r'^\[.*\]$')

    def read(self, filename):
        source = open(filename, encoding='utf8')
        for line in source:
            if line.startswith('#'):
                continue
            if ':::' not in line:
                continue

            line_splits = line.split(':::')

            if len(line_splits) > 2:
                pattern_name = line_splits[0].strip()
                pattern_source = line_splits[1].strip()
                pattern_mappings = line_splits[2].strip()
            else:
                pattern_name = ''
                pattern_source = line_splits[0].strip()
                pattern_mappings = line_splits[1].strip()

            regex = self.parse_pattern(pattern_source)
            self.patterns.append(
                {'name': pattern_name,
                 'regex': regex,
                 'mappings': pattern_mappings})
        source.close()
        return self.patterns

    def parse_pattern(self, text):
        """translate pattern into regular expression"""
        text = re.sub(r'(\s+)', ' ', text)
        tokens = self.parse_tokens(text)
        return ''.join(
            [self.translate_pattern_item(token) for token in tokens])

    def translate_pattern_item(self, token):
        """translate pattern item into regular expression"""
        if self.is_optional(token):
            return '(?:' + self.parse_pattern(token[1:-1]) + ')?'

        match = self.token_pattern.search(token)
        if match:
            tr_token, token_type = self.translate_token_s(match.group('token'))
            if token_type == "ignore":
                return token
            elif token_type == 'common':
                return r'(?P<{0}>\w+)<{1}>' \
                    .format(match.group('class'), tr_token)
            else:
                return r'(?P<{0}>{1})' \
                    .format(match.group('class'), tr_token)

        if token in self.special_chars:
            return r'\{}'.format(token)

        tr_token, token_type = self.translate_token(token)
        if token_type == 'common':
            new_token = r'(\w+)<{0}>'.format(tr_token)
        elif token_type == 'special':
            new_token = r'({0})'.format(tr_token)
        else:
            new_token = tr_token

        return new_token

    def translate_token_s(self, token):
        if token in self.token_dictionary:
            return (self.token_dictionary[token], 'common')
        elif token in self.special_tokens:
            return (self.special_tokens[token], 'special')
        elif token in self.tokens_to_ignore:
            return token, 'ignore'
        else:
            raise Exception('Unknown token: {}'.format(token))

    def translate_token(self, token):
        if token in self.token_dictionary:
            return (self.token_dictionary[token], 'common')
        elif token in self.special_tokens:
            return (self.special_tokens[token], 'special')
        else:
            return (token, 'unknown')

    @staticmethod
    def parse_tokens(text):
        """Find all tokens from string. Nesting optional tokens ignored"""
        def find_end_of_brackets(text, start):
            i = start
            bracket_status = 0
            while i < len(text):
                if text[i] == ']':
                    if bracket_status == 0:
                        return i
                    else:
                        bracket_status -= 1
                        if bracket_status < 0:
                            raise Exception('unexpected ]')
                elif text[i] == '[':
                    bracket_status += 1
                i += 1
            raise Exception('expected ], end of text found')

        def find_end_of_token(text, start):
            i = start
            while i < len(text):
                if text[i] == ']':
                    raise Exception('unexpected ]')

                if text[i] == '[' or text[i] == ' ':
                    break
                else:
                    i += 1
            return i

        text = text.strip()
        text_length = len(text)
        tokens = []
        i = 0
        while i < text_length:
            if text[i] == ' ':
                tokens.append(' ')
                i += 1
                continue

            if text[i] == ']':
                raise Exception('unexpected ]')

            if text[i] == '[':
                j = find_end_of_brackets(text, i + 1)
                tokens.append(text[i:j + 1])
                i = j + 1
            else:
                j = find_end_of_token(text, i + 1)
                tokens.append(text[i:j])
                i = j
        return tokens

    def is_optional(self, token):
        return self.optional_token_pattern.match(token) is not None
