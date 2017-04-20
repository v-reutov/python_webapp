import re
from Parser.PatternReader import PatternReader


def main():
    text = """
    взять<V> вал<S>.
    крыльчатка<S> (1) надевать<V> на<PR> вал<S>.
    вал<S> вставлять<V> в<PR> корпус<S> (1).
    крыльчатка<S> (2) надевать<V> на<PR> вал<S>.
    шнек<S> надевать<V> на<PR> вал<S>.
    вал<S> вставлять<V> в<PR> корпус<S> (2).
    """

    pattern = "(?P<object_1>\w+)<S>(\s)(?:(?:\()?(?P<number_1>\d+)(?:\))?)?(\s)(?P<action>\w+)<V>(\s*)(?P<loc>\w+)<PR>(\s)(?P<object_2>\w+)<S>(\s)(?:(?:\()?(?P<number_2>\d+)(?:\))?)?"

    regex = re.compile(pattern)
    matches = [match.groupdict() for match in regex.finditer(text)]
    print(matches)


if __name__ == "__main__":
    main()
