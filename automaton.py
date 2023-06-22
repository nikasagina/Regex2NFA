from copy import deepcopy
from typing import Set, Dict

EPSILON = 'EP'  # since 'symbols' are a single characters, there will be no 'EP' input

state_count = -1  # will become 0 after first next_state_name function call


class NFA:
    def __init__(self, states: list[int], symbols: Set[str], transitions: Dict[int, Dict[str, Set[int]]],
                 start_state: int, accept_states: Set[int]) -> None:
        """
        Initializes a new NFA.

        :param states: A set of all the states in NFA
        :param symbols: A set of all input symbols (language)
        :param transitions: A dictionary containing transitions of NFA.
            The keys of the dictionary are the states, and the values are dictionaries
            that match the input symbol with a set of states the symbol transitions to.
            transitions form: {state: {symbol: {states}, ...}, ... }
        :param start_state: An integer representing the starting state of the NFA
        :param accept_states: A set of accepting states of the NFA
        """
        self.states = states
        self.symbols = symbols
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def alternation(self, other: 'NFA') -> None:
        # state names must be unique
        if set(self.states).intersection(other.states):
            raise RuntimeError("Name intersection in NFA alternation")

        # create new epsilon states
        start_epsilon = next_state_name()
        end_epsilon = next_state_name()

        # update states
        self.states.insert(0, start_epsilon)
        self.states.extend(other.states)
        self.states.append(end_epsilon)

        # add epsilon transitions
        self.transitions[start_epsilon] = {EPSILON: {self.start_state, other.start_state}}

        self.transitions[self.accept_states.pop()] = {EPSILON: {end_epsilon}}
        other.transitions[other.accept_states.pop()] = {EPSILON: {end_epsilon}}

        # add other NFA's transitions to the current one
        self.transitions.update(other.transitions)

        # update accept and start states
        self.start_state = start_epsilon
        self.accept_states.add(end_epsilon)

    def concatenation(self, other: 'NFA') -> None:
        # state names must be unique
        if set(self.states).intersection(other.states):
            raise RuntimeError("Name intersection in NFA concatenation")

        # there is always only 1 accept state in Thompson's construction so no need to iterate over accept states
        # just transfer other NFAs's transfer state to the current one and remove the old one
        final_state = other.accept_states.pop()
        old_final_state = self.accept_states.pop()
        self.accept_states.add(final_state)

        # middle point of the concatenation
        middle_state = other.start_state

        # make a copy of transitions to modify it while iterating over it
        new_transitions: Dict[int, Dict[str, Set[int]]] = deepcopy(self.transitions)
        for state in self.transitions:
            for symbol in self.transitions[state]:
                if old_final_state not in self.transitions[state][symbol]:
                    continue
                # if any state transitions to the old final state, replace it with transition to the middle state
                new_transitions[state][symbol].remove(old_final_state)
                new_transitions[state][symbol].add(middle_state)

        # add other NFA's states to the current one
        self.states.extend(other.states)

        # remove unused state
        self.states.remove(old_final_state)

        # add other NFA's transitions to the current's transitions
        new_transitions.update(other.transitions)
        self.transitions = new_transitions

    def kleene_star(self) -> None:
        # create new epsilon states and save the old ones
        start_epsilon = next_state_name()
        end_epsilon = next_state_name()
        old_start_state = self.states[0]
        old_final_state = self.states[-1]

        # update start state
        self.start_state = start_epsilon

        # update accept state
        assert self.accept_states.pop() == old_final_state
        self.accept_states.add(end_epsilon)

        # update states
        self.states.insert(0, start_epsilon)
        self.states.append(end_epsilon)

        # update transitions
        self.transitions[start_epsilon] = {EPSILON: {old_start_state, end_epsilon}}
        self.transitions[old_final_state] = {EPSILON: {old_start_state, end_epsilon}}

    def reduce(self) -> None:
        self._remove_unreachable_states()
        self._rename_removed_states()

    def remove_epsilon(self) -> None:
        # first, all states that transition into accept state with epsilon, become accepting themselves
        while True:
            accept_count = len(self.accept_states)

            # iterate over epsilon transitions
            for state in self.transitions:
                if EPSILON not in self.transitions[state]:
                    continue

                # if the state transitions to accepting state with epsilon symbol, the current state becomes accepting
                if self.transitions[state][EPSILON].intersection(self.accept_states):
                    self.accept_states.add(state)

            # if no new accept states were added in the iteration, break
            if len(self.accept_states) == accept_count:
                break

        # iterate over transitions while there is at least one epsilon transition
        while self._transitions_contain_epsilon():

            # create a copy of the transitions to change it while iterating over it
            temp: Dict[int, Dict[str, Set[int]]] = deepcopy(self.transitions)

            # loop over states that have epsilon transitions
            for state in self.transitions:
                if EPSILON not in self.transitions[state]:
                    continue

                # set up a stack to keep track of visited states and visit them
                visited = set()
                stack = [state]

                while stack:
                    curr_state = stack.pop()
                    if curr_state in visited:
                        continue
                    visited.add(curr_state)

                    # if current state does not have any transitions, move on to next state
                    if curr_state not in self.transitions:
                        continue

                    # iterate over all symbols and their transitions from the current state
                    for symbol in self.transitions[curr_state]:
                        if symbol == EPSILON:
                            # for epsilon transitions, add all transition states to the stack
                            for transition_state in self.transitions[curr_state][EPSILON]:
                                stack.append(transition_state)

                                # if the current state has an epsilon transition to a transition state, remove it
                                if curr_state in temp and EPSILON in temp[curr_state]:
                                    temp[curr_state][EPSILON].remove(transition_state)

                            # delete the epsilon transition from the current state
                            if curr_state in temp and EPSILON in temp[curr_state]:
                                del temp[curr_state][EPSILON]

                            # if the current state does not have any transitions left, delete it from temp
                            if curr_state in temp and not temp[curr_state]:
                                del temp[curr_state]
                        else:
                            # for non-epsilon transitions, add the transition states to the temp dictionary
                            if state not in temp:
                                temp[state] = dict()
                            if symbol not in temp[state]:
                                temp[state][symbol] = set()
                            for transition_state in self.transitions[curr_state][symbol]:
                                temp[state][symbol].add(transition_state)

            # update the transitions with the changes made in the temp dictionary
            self.transitions = temp

    def _transitions_contain_epsilon(self) -> bool:
        for state in self.transitions:
            if EPSILON in self.transitions[state]:
                return True
        return False

    def _remove_unreachable_states(self) -> None:
        unreachable_states = set(self.states) - self._reachable_states()

        # remove the bad state from the list of states
        for i in range(len(self.states) - 1, -1, -1):
            if self.states[i] in unreachable_states:
                del self.states[i]

        # remove the bad state from the set of accept states
        for bad_state in unreachable_states:
            if bad_state in self.accept_states:
                self.accept_states.remove(bad_state)

        # remove the bad state from the keys of the transitions
        for state in unreachable_states:
            if state in self.transitions:
                del self.transitions[state]

        # remove the bad state from the values of the transitions
        for state in self.transitions:
            for symbol in self.transitions[state]:
                self.transitions[state][symbol] = self.transitions[state][symbol].difference(unreachable_states)

    def _reachable_states(self) -> Set[int]:
        # Perform a depth-first search from the start state to find all reachable states
        visited = set()
        stack = [self.start_state]
        while stack:
            state = stack.pop()
            if state in visited:
                continue
            visited.add(state)
            if state not in self.transitions:
                continue
            for symbol in self.transitions[state]:
                for dest_state in self.transitions[state][symbol]:
                    stack.append(dest_state)
        return visited

    def _rename_removed_states(self) -> None:
        for i in range(len(self.states)):
            if self.states[i] == i:
                continue

            old_index = self.states[i]

            # rename in states list
            self.states[i] = i

            # rename in accept states
            if old_index in self.accept_states:
                self.accept_states.remove(old_index)
                self.accept_states.add(i)

            # rename in transition keys
            if old_index in self.transitions:
                value = self.transitions.pop(old_index)
                self.transitions[i] = value

            # rename in transition values
            for state in self.transitions:
                for symbol in self.transitions[state]:
                    if old_index in self.transitions[state][symbol]:
                        self.transitions[state][symbol].remove(old_index)
                        self.transitions[state][symbol].add(i)

    def _transitions_count(self, state: int) -> int:
        res: int = 0
        for symbol in self.transitions[state]:
            res += len(self.transitions[state][symbol])
        return res

    def _total_transitions_count(self) -> int:
        res: int = 0
        for state in self.transitions:
            res += self._transitions_count(state)
        return res

    def __str__(self) -> str:
        res: str = f"{len(self.states)} {len(self.accept_states)} {self._total_transitions_count()}\n"

        for accept_state in self.accept_states:
            res += f"{accept_state} "

        res = res[:-1] + '\n'

        for state in self.states:
            if state not in self.transitions.keys():
                res += '0'
            else:
                res += str(self._transitions_count(state)) + ' '
                for symbol in self.transitions[state]:
                    for destination in self.transitions[state][symbol]:
                        res += f"{symbol} {destination} "
            res += '\n'

        return res


def next_state_name() -> int:
    global state_count
    state_count += 1
    return state_count


def get_states_list(size: int) -> list[int]:
    return [next_state_name() for _ in range(size)]
