from automaton import NFA, EPSILON, get_states_list


def format_epsilon(regex: list) -> list:
    """
    Replaces epsilon identifier () with the epsilon symbol.
    """
    for i in range(len(regex) - 1):
        if regex[i] == '(' and regex[i + 1] == ')':
            # replace empty parentheses with epsilon symbol
            regex[i] = EPSILON
            regex.pop(i + 1)
    return regex


def format_list(tokens: list) -> list:
    """
    Turns list with parenthesis into a nested python list.
    First end last parenthesis must be inserted before calling this function.
    Example: ['(', '1', '(', '2', '3'), '4', ')'] -> ['1', ['2', '3'], '4']
    """
    token = tokens.pop(0)
    if token == '(':
        inside = []
        # parse the inside of the parenthesis recursively
        while tokens[0] != ')':
            inside.append(format_list(tokens))
        tokens.pop(0)
        return inside
    return token


def evaluate(regex: list) -> NFA:
    """
    Evaluates list with NFAs and regular operations. recursively calls itself
    on nested lists and replaces it with equivalent epsilon-NFA.
    :param regex: list containing NFAs, regular operations and nested lists
    :return: corresponding NFA
    """
    for i in range(len(regex)):
        if isinstance(regex[i], list):
            regex[i] = evaluate(regex[i])

    if len(regex) == 1:
        return regex[0]

    # kleene star operations first
    for i in range(len(regex) - 1, -1, -1):
        if regex[i] == '*':
            regex[i - 1].kleene_star()
            regex.pop(i)

    # concatenation second
    for i in range(len(regex) - 2, -1, -1):
        if regex[i] != '|' and regex[i + 1] != '|':
            regex[i].concatenation(regex.pop(i + 1))

    # alternation last
    for i in range(len(regex) - 1, -1, -1):
        if regex[i] == '|':
            regex.pop(i)
            regex[i - 1].alternation(regex[i])
            regex.pop(i)

    return regex[0]


def regex_to_nfa(regex: str) -> NFA:
    """
    Takes string representing regular expression and returns epsilon-NFA
    which accepts the same language as the regular expression.
    :param regex: regular expression
    :return: corresponding epsilon-NFA
    """
    regex = format_epsilon(list(regex))

    # replace each symbols with corresponding NFA
    for i in range(len(regex)):
        if regex[i] != '(' and regex[i] != ')' and regex[i] != '|' and regex[i] != '*':
            states = get_states_list(2)
            regex[i] = NFA([states[0], states[1]], regex[i],
                           {states[0]: {regex[i]: {states[1]}}}, states[0], {states[1]})

    # adding parenthesis at the beginning and the end is needed for the formatting to work
    regex.insert(0, '(')
    regex.append(')')
    regex_list = format_list(regex)

    return evaluate(regex_list)


def main():
    regex: str = input()
    nfa: NFA = regex_to_nfa(regex)
    nfa.remove_epsilon()
    nfa.reduce()
    print(nfa)


if __name__ == '__main__':
    main()
