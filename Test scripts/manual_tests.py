from automaton import NFA, EPSILON, get_states_list
import build
import run


def test_nfa_to_string():
    nfa = NFA([0, 1], {'a', 'b', 'c'}, {0: {'a': {0}, 'b': {0}, 'c': {1}}}, 0, {0, 1})
    print(nfa)

    nfa = NFA([0, 1, 2], {'a', 'b', 'c', '0', '1'},
              {0: {'a': {1}}, 1: {'b': {1}, 'c': {2}}, 2: {'0': {2}, '1': {2}, 'a': {1}}}, 0, {0, 2})
    print(nfa)


def test_nfa_remove_epsilon():
    nfa = NFA([0, 1, 2], {'a'}, {0: {EPSILON: {1}}, 1: {'a': {2}}}, 0, {0})
    nfa.remove_epsilon()
    # expect:
    # 3 1 2
    # 0
    # 1 a 2
    # 1 a 2
    print(nfa)

    nfa = NFA([0, 1, 2], {'a', 'b', EPSILON}, {0: {'a': {1}, EPSILON: {2}}, 1: {'b': {1}, EPSILON: {2}},
                                               2: {'b': {1}}}, 0, {1})
    nfa.remove_epsilon()
    # expect:
    # 3 1 4
    # 1
    # 2 a 1 b 1
    # 1 b 1
    # 1 b 1
    print(nfa)

    nfa = NFA([0, 1, 2], {'a', 'b', EPSILON}, {0: {EPSILON: {1, 2}}, 1: {'b': {1}, EPSILON: {2}},
                                               2: {'b': {1}}}, 0, {1})
    nfa.remove_epsilon()
    # expect:
    # 3 2 3
    # 0 1
    # 1 b 1
    # 1 b 1
    # 1 b 1
    print(nfa)

    nfa = NFA([0, 1, 2], {'a', EPSILON}, {0: {EPSILON: {1}}, 1: {EPSILON: {2}}, 2: {'a': {0}}}, 0, {2})
    nfa.remove_epsilon()
    # 3 3 3
    # 0 1 2
    # 1 a 0
    # 1 a 0
    # 1 a 0
    print(nfa)

    nfa = NFA([0, 1, 2, 3], {'a', EPSILON}, {0: {EPSILON: {1}}, 1: {EPSILON: {2}}, 2: {'a': {3}}}, 0, {3})
    nfa.remove_epsilon()
    # 4 1 3
    # 3
    # 1 a 3
    # 1 a 3
    # 1 a 3
    # 0
    print(nfa)


def test_nfa_reachable_states():
    nfa = NFA([0, 1, 2], {'a', EPSILON}, {0: {'a': {1}}, 1: {EPSILON: {0}}}, 0, {2})
    # expect {0, 1}
    print(nfa._reachable_states())

    nfa = NFA([0, 1, 2], {'a', EPSILON}, {0: {'a': {1}}, 1: {EPSILON: {0}}, 2: {'a': {0, 1}, EPSILON: {0, 1}}}, 0, {2})
    # expect {0, 1}
    print(nfa._reachable_states())


def test_nfa_remove_unreachable_states():
    nfa = NFA([0, 1, 2], {'a', EPSILON}, {0: {'a': {1}}, 1: {EPSILON: {0}}}, 0, {2})
    nfa._remove_unreachable_states()
    # 2 0 2
    #
    # 1 a 1
    # 1 EP 0
    print(nfa)

    nfa = NFA([0, 1, 2, 3], {'0', '1'}, {0: {'0': {1}}, 1: {'1': {0}}, 2: {'0': {3}}, 3: {'1': {2}}}, 0, {1, 3})
    nfa._remove_unreachable_states()
    # 2 1 2
    # 1
    # 1 0 1
    # 1 1 0
    print(nfa)


def test_nfa_remove_epsilon_and_unreachable():
    nfa = NFA([0, 1, 2], {'a', EPSILON}, {0: {'a': {1}}, 1: {EPSILON: {0}}}, 0, {2})
    nfa.remove_epsilon()
    nfa._remove_unreachable_states()

    # 2 0 2
    #
    # 1 a 1
    # 1 a 1
    print(nfa)

    nfa = NFA([0, 1, 2, 3], {'a', EPSILON}, {0: {EPSILON: {2}}, 1: {'a': {0, 2}}, 2: {'a': {3}}}, 0, {2})
    nfa.remove_epsilon()
    nfa._remove_unreachable_states()

    # 2 1 1
    # 0
    # 1 a 3
    # 0
    print(nfa)


def test_nfa_reduce():
    nfa = NFA([0, 1, 2, 3], {'a'}, {0: {'a': {3}}, 1: {'a': {0, 2}}}, 0, {3})
    nfa.reduce()

    # 2 1 1
    # 1
    # 1 a 1
    # 0
    print(nfa)


def test_nfa_remove_epsilon_and_reduce():
    # public test #1
    nfa = NFA([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], {1, 0, EPSILON, 'o', 'r', 'y'}, {
        0: {EPSILON: {1, 12}},
        1: {EPSILON: {2, 7}},
        2: {1: {3}},
        3: {'o': {4}},
        4: {'r': {5}},
        5: {0: {6}},
        6: {EPSILON: {11}},
        7: {EPSILON: {8, 10}},
        8: {'y': {9}},
        9: {EPSILON: {8, 10}},
        10: {EPSILON: {11}},
        11: {EPSILON: {1, 12}}
    }, 0, {12})

    nfa.remove_epsilon()
    nfa.reduce()

    # 6 3 9
    # 0 4 5
    # 2 1 1 y 5
    # 1 o 2
    # 1 r 3
    # 1 0 4
    # 2 1 1 y 5
    # 2 y 5 1 1
    print(nfa)


def test_nfa_concatenation():
    nfa1 = NFA([0, 1], {'a', 'b'}, {0: {'a': {1}}}, 0, {1})
    nfa2 = NFA([2, 3], {'a', 'b'}, {2: {'b': {3}}}, 2, {3})
    nfa1.concatenation(nfa2)
    # 3 1 2
    # 3
    # 1 a 2
    # 1 b 3
    # 0
    print(nfa1)

    nfa1 = NFA([0, 1, 2, 3], {'a', 'b'}, {0: {'a': {1}, 'b': {2}}, 1: {'b': {3}}, 2: {'a': {3}}}, 0, {3})
    nfa2 = NFA([4, 5, 6, 7], {'a', 'b'}, {4: {'a': {5}, 'b': {6}}, 5: {'b': {7}}, 6: {'a': {7}}}, 4, {7})
    nfa1.concatenation(nfa2)
    # 7 1 8
    # 7
    # 2 a 1 b 2
    # 1 b 4
    # 1 a 4
    # 2 a 5 b 6
    # 1 b 7
    # 1 a 7
    # 0
    print(nfa1)


def test_nfa_kleene_star():
    names = get_states_list(2)
    nfa = NFA(names, {'a'}, {names[0]: {'a': {names[1]}}}, names[0], {names[1]})
    nfa.kleene_star()
    nfa.remove_epsilon()
    nfa.reduce()
    # expect:
    # 2 2 2
    # 0 1
    # 1 a 1
    # 1 a 1
    print(nfa)


def test_nfa_alternation():
    names1 = get_states_list(2)
    nfa1 = NFA(names1, {'a'}, {names1[0]: {'a': {names1[1]}}}, names1[0], {names1[1]})
    names2 = get_states_list(2)
    nfa2 = NFA(names2, {'b'}, {names2[0]: {'b': {names2[1]}}}, names2[0], {names2[1]})
    nfa1.alternation(nfa2)
    nfa1.remove_epsilon()
    nfa1.reduce()
    # expect:
    # 3 2 2
    # 1 2
    # 2 a 1 b 2
    # 0
    # 0
    print(nfa1)


def test_nfa():
    test_nfa_to_string()
    test_nfa_remove_epsilon()
    test_nfa_reachable_states()
    test_nfa_remove_unreachable_states()
    test_nfa_remove_epsilon_and_unreachable()
    test_nfa_reduce()
    test_nfa_remove_epsilon_and_reduce()
    test_nfa_concatenation()
    test_nfa_kleene_star()
    test_nfa_alternation()


def test_build_format_epsilon():
    assert build.format_epsilon(['(', 'a', '|', '(', ')', ')']) == ['(', 'a', '|', EPSILON, ')']
    assert build.format_epsilon(['a', '(', ')', 'b']) == ['a', EPSILON, 'b']
    assert build.format_epsilon(['a', 'b', 'c']) == ['a', 'b', 'c']
    assert build.format_epsilon([]) == []
    assert build.format_epsilon(['(']) == ['(']
    assert build.format_epsilon([')', '(']) == [')', '(']


def test_build():
    test_build_format_epsilon()


def test_run():
    nfa = NFA([0, 1, 2], {'a', 'b'}, {0: {'a': {1}}, 1: {'b': {2}}, 2: {'a': {2}}}, 0, {2})
    assert run.simulate("aba", nfa) == "NYY"
    assert run.simulate("abaaaaa", nfa) == "NYYYYYY"
    assert run.simulate("b", nfa) == "N"
    assert run.simulate("ba", nfa) == "NN"
    assert run.simulate("a", nfa) == "N"
    assert run.simulate("", nfa) == ""

    nfa = NFA([0, 1], {'a', 'b', 'c'}, {0: {'a': {0}, 'b': {0}, 'c': {1}}}, 0, {0, 1})
    assert run.simulate("aababacab", nfa) == "YYYYYYYNN"
    assert run.simulate("aaaaaaaca", nfa) == "YYYYYYYYN"
    assert run.simulate("abcab", nfa) == "YYYNN"

    nfa = NFA([0, 1, 2], {'a', 'b', 'c', '0', '1'}, {0: {'a': {1}}, 1: {'b': {1}, 'c': {2}},
                                                     2: {'a': {1}, '0': {2}, '1': {2}}}, 0, {0, 2})
    assert run.simulate("abbc1acabbbbc001cabc", nfa) == "NNNYYNYNNNNNYYYYNNNN"


def main():
    test_nfa()
    test_build()
    test_run()


if __name__ == '__main__':
    main()
