from nfa_org import NfaList, Nfa
import sys

EMPTY = -1
NFA_STATE_MAX = 256
NFA_VECTOR_SIZE = int(NFA_STATE_MAX / 8)
DFA_STATE_MAX = 100

class NfaStateSet:
    # merely bit vector
    def __init__(self):
        self.vec = [0 for _ in range(NFA_VECTOR_SIZE)]

class Dlist:
    def __init__(self):
        self.char = None
        self.dst = NfaStateSet()
        self.next = None

class Dslist:
    def __init__(self):
        self.char = None
        self.dst = Dstate()
        self.next = None

class Dstate:
    def __init__(self):
        self.state = None
        self.visited = None
        self.accepted = None
        self.next = None
        self.to = None

class Dfa:
    def __init__(self, regex, debug=False):
        self.regex = regex
        self.dfa = [Dstate() for _ in range(DFA_STATE_MAX)]
        self.initial_state = NfaStateSet()
        self.initial_dfa_state = Dstate()
        self.state = 0
        self.nfa_state = None
        self.nfa = None
        self.nfa_entry = None
        self.nfa_exit = None
        self.debug = debug

    def check_nfa_state(self, state, s):
        # merely checking bit vector
        return state.vec[int(s/8)] & (1 << (s%8))

    def dump_state_set(self, p):
        for i in range(self.nfa_state):
            if self.check_nfa_state(p, i):
                print("{} ".format(i), end="")

    def dump_dfa(self):
        for i in range(self.state):
            s = 'A' if self.dfa[i].accepted else ' '
            print("{:2}{}: ".format(i, s), end="")
            l = self.dfa[i].next
            while l:
                print("{}=>{} ".format(l.char, l.dst.to), end="")
                l = l.next
            print()
        for i in range(self.state):
            s = 'A' if self.dfa[i].accepted else ' '
            print("state {:2}{} = {}".format(i, s, "{"), end="")
            self.dump_state_set(self.dfa[i].state)
            print("}")

    def add_nfa_state(self, state, s):
        # merely sign on bit vector
        state.vec[int(s/8)] |= (1 << (s%8))

    def mark_empty_transition(self, state, s):
        self.add_nfa_state(state, s)
        p = self.nfa[s]
        while p:
            if p.char == EMPTY and not self.check_nfa_state(state, p.to):
                self.mark_empty_transition(state, p.to)
            p = p.next

    def collect_empty_transition(self, state):
        for i in range(self.nfa_state):
            if self.check_nfa_state(state, i):
                self.mark_empty_transition(state, i)

    def equal_nfa_state_set(self, a, b):
        for i in range(NFA_VECTOR_SIZE):
            if a.vec[i] != b.vec[i]:
                return 0
        return 1

    def register_dfa_state(self, s):
        for i in range(self.state):
            if self.equal_nfa_state_set(self.dfa[i].state, s):
                return self.dfa[i]
        if self.state > DFA_STATE_MAX:
            print("Too many DFA state.")
            sys.exit(1)

        self.dfa[self.state].state = s
        self.dfa[self.state].visited = 0
        accepted = 1 if self.check_nfa_state(s, self.nfa_exit) else 0
        self.dfa[self.state].accepted = accepted
        self.dfa[self.state].next = None
        self.dfa[self.state].to = self.state
        p = self.dfa[self.state]
        self.state += 1
        return p

    def fetch_unvisited_dfa_state(self):
        for i in range(self.state):
            if self.dfa[i].visited == 0:
                return self.dfa[i]
        return None

    def compute_reachable_nfa_state(self, dstate):
        state = dstate.state
        result = None
        goto = False
        for i in range(self.nfa_state):
            if self.check_nfa_state(state, i):
                p = self.nfa[i]
                while p:
                    if p.char != EMPTY:
                        a = result
                        while a:
                            if a.char == p.char:
                                self.add_nfa_state(a.dst, p.to)
                                goto = True
                                break
                            a = a.next
                        if goto:
                            goto = False
                            p = p.next
                            continue
                        b = Dlist()
                        b.char = p.char
                        self.add_nfa_state(b.dst, p.to)
                        b.next = result
                        result = b
                    p = p.next
        return result

    def init_nfa(self):
        nfa = Nfa(self.regex, self.debug)
        nfa.build_nfa()
        self.nfa_entry = nfa.entry
        self.nfa_exit = nfa.exit
        self.nfa_state = nfa.state
        self.nfa = nfa.nfa

    def convert_nfa_to_dfa(self):
        self.init_nfa()
        self.add_nfa_state(self.initial_state, self.nfa_entry)
        self.collect_empty_transition(self.initial_state)
        self.initial_dfa_state = self.register_dfa_state(self.initial_state)

        t = self.fetch_unvisited_dfa_state()

        while t:
            t.visited = 1
            x = self.compute_reachable_nfa_state(t)
            while x:
                self.collect_empty_transition(x.dst)
                p = Dslist()
                p.char = x.char
                p.dst = self.register_dfa_state(x.dst)
                p.next = t.next
                t.next = p
                x = x.next
            t = self.fetch_unvisited_dfa_state()
        if self.debug:
            print("---- DFA ----")
            self.dump_dfa()

regex = 'a(a|b)*a'
print('regex = {}'.format(regex))

dfa = Dfa(regex, debug=True)
dfa.convert_nfa_to_dfa()




