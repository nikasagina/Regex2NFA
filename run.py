from automaton import NFA
from typing import Set, Dict


def read_nfa() -> NFA:
    # read the number of states, the number of accept states, and the number of transitions
    input_list = input().split()
    state_count: int = int(input_list[0])
    accept_count: int = int(input_list[1])
    transition_count: int = int(input_list[2])

    # create list of states
    states: list[int] = list(range(state_count))

    # read the accept states
    input_list = input().split()
    accept_states: set[int] = set()
    for i in range(accept_count):
        accept_states.add(int(input_list[i]))

    # read transitions
    transitions: Dict[int, Dict[str, Set[int]]] = {}
    for i in range(state_count):
        input_list = input().split()

        # read the number of transitions for this state
        state_transitions_count: int = int(input_list[0])
        transition_count -= state_transitions_count

        if state_transitions_count == 0:
            continue

        # create a dictionary to store the transitions for this state
        transitions[i] = {}

        # read the transitions for this state
        for j in range(state_transitions_count):
            symbol: str = input_list[j * 2 + 1]
            transition_state: int = int(input_list[(j + 1) * 2])

            # add the transition to the dictionary
            if symbol not in transitions[i]:
                transitions[i][symbol] = set()
            transitions[i][symbol].add(transition_state)

    # ensure that all transitions were read
    assert transition_count == 0

    # create and return an NFA object
    return NFA(states, set(), transitions, 0, accept_states)


def simulate(input_string: str, nfa: NFA) -> str:
    result: str = ''
    current_states = {nfa.start_state}

    # loop over the input string
    for ch in input_string:
        next_states = set()

        # for each current state, find the set of states that can be reached by consuming the input character
        for state in current_states:
            if state in nfa.transitions:
                if ch in nfa.transitions[state]:
                    next_states.update(nfa.transitions[state][ch])

        # set the next set of current states to the set of reachable states
        current_states = next_states

        # check if any of the current states are accepting states
        if current_states.intersection(nfa.accept_states):
            result += 'Y'
        else:
            result += 'N'

    # return the result string
    return result


def main():
    # read the input string and the NFA definition, and simulate the input string on the NFA
    input_string: str = input()
    nfa: NFA = read_nfa()
    result: str = simulate(input_string, nfa)

    # print the result
    print(result)


if __name__ == '__main__':
    main()
