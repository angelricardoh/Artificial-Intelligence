import os.path
from os import path
import collections
import collections.abc


class ComplexSentence:

    sentences_dict = {}
    def __init__(self, op, *args):
        self.op = str(op)
        self.args = args
        self.sentenceNumber = ComplexSentence.counter
        ComplexSentence.sentences_dict[self.sentenceNumber] = self
        ComplexSentence.counter += 1

    def __invert__(self):
        return ComplexSentence('~', self)

    def __and__(self, rhs):
        return ComplexSentence('&', self, rhs)

    def __or__(self, rhs):
        if isinstance(rhs, ComplexSentence):
            return ComplexSentence('|', self, rhs)
        else:
            return Sentence(rhs, self)

    def __call__(self, *args):
        if self.args:
            print("Error element should not contain args")
        else:
            return ComplexSentence(self.op, *args)

    def __eq__(self, other):
        return isinstance(other, ComplexSentence) and self.op == other.op and self.args == other.args

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)

    def __repr__(self):
        op = self.op
        args = [str(arg) for arg in self.args]
        if op.isidentifier():  # f(x) or f(x, y)
            return '{}({})'.format(op, ', '.join(args)) if args else op
        elif len(args) == 1:  # -x or -(x + 1)
            return op + args[0]
        else:  # (x - y)
            opp = (' ' + op + ' ')
            return '(' + opp.join(args) + ')'


def subexpressions(x):
    yield x
    if isinstance(x, ComplexSentence):
        for arg in x.args:
            yield from subexpressions(arg)


def arity(expression):
    if isinstance(expression, ComplexSentence):
        return len(expression.args)
    else:
        return 0


class Sentence:
    def __init__(self, op, lhs):
        self.op, self.lhs = op, lhs

    def __or__(self, rhs):
        return ComplexSentence(self.op, self.lhs, rhs)

    def __repr__(self):
        return "Sentence('{}', {})".format(self.op, self.lhs)


def Symbol(name):
    return ComplexSentence(name)


def expr(x):
    if isinstance(x, str):
        # print(expr_handle_infix_ops(x))
        # something = eval(expr_handle_infix_ops(x), DefaultKeyDict(ComplexSentence))
        # print(type(something))
        default_dict = {Symbol : {}}
        # print(default_dict)
        y = SentencesDictionary(Symbol)
        # print(y)
        return eval(handle_implications_disjuncts(x), y)
    else:
        return x


def first(iterable, default=None):
    return next(iter(iterable), default)


def remove_all(item, seq):
    if isinstance(seq, str):
        return seq.replace(item, '')
    elif isinstance(seq, set):
        rest = seq.copy()
        rest.remove(item)
        return rest
    else:
        return [x for x in seq if x != item]


def unique(seq):
    return list(set(seq))


def is_sequence(x):
    return isinstance(x, collections.abc.Sequence)


def handle_implications_disjuncts(x):
    op = '=>'
    x = x.replace(op, '|' + repr(op) + '|')
    return x


class SentencesDictionary(collections.defaultdict):
    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result


def is_symbol(s):
    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):
    return is_symbol(s) and s[0].islower()


def variables(s):
    return {x for x in subexpressions(s) if isvariable(x)}


def convert_to_cnf(s):
    s = expr(s)
    if isinstance(s, str):
        s = expr(s)
    s = eliminate_implications(s)
    s = move_not_inwards(s)
    return distribute_and_over_or(s)


def eliminate_implications(s):
    s = expr(s)
    if not s.args or is_symbol(s.op):
        return s
    args = list(map(eliminate_implications, s.args))
    a, b = args[0], args[-1]
    if s.op == '=>':
        return b | ~a
    elif s.op == '<=':
        return a | ~b
    elif s.op == '<=>':
        return (a | ~b) & (b | ~a)
    elif s.op == '^':
        assert len(args) == 2  # TODO: relax this restriction
        return (a & ~b) | (~a & b)
    else:
        assert s.op in ('&', '|', '~')
        return ComplexSentence(s.op, *args)


def move_not_inwards(s):
    s = expr(s)
    if s.op == '~':
        def NOT(b):
            return move_not_inwards(~b)

        a = s.args[0]
        if a.op == '~':
            return move_not_inwards(a.args[0])  # ~~A ==> A
        if a.op == '&':
            return join_terms('|', list(map(NOT, a.args)))
        if a.op == '|':
            return join_terms('&', list(map(NOT, a.args)))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return ComplexSentence(s.op, *list(map(move_not_inwards, s.args)))


def distribute_and_over_or(s):
    s = expr(s)
    if s.op == '|':
        s = join_terms('|', s.args)
        if s.op != '|':
            return distribute_and_over_or(s)
        if len(s.args) == 0:
            return False
        if len(s.args) == 1:
            return distribute_and_over_or(s.args[0])
        conj = first(arg for arg in s.args if arg.op == '&')
        if not conj:
            return s
        others = [a for a in s.args if a is not conj]
        rest = join_terms('|', others)
        return join_terms('&', [distribute_and_over_or(c | rest)
                               for c in conj.args])
    elif s.op == '&':
        return join_terms('&', list(map(distribute_and_over_or, s.args)))
    else:
        return s


def NOT(b):
    return move_negation_inwards_rec(~b)

def move_negation_inwards_rec(s):
    if s.op == '~':
        a = s.args[0]
        if a.op == '~':
            return move_negation_inwards_rec(a.args[0])
        if a.op == '&':
            return join_terms('|', list(map(NOT, a.args)))
        if a.op == '|':
            return join_terms('&', list(map(NOT, a.args)))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return ComplexSentence(s.op, *list(map(move_negation_inwards_rec, s.args)))


def distribute_rec(s):
    s = expr(s)
    if s.op == '|':
        s = join_terms('|', s.args)
        if s.op != '|':
            return distribute_rec(s)
        if len(s.args) == 0:
            return False
        if len(s.args) == 1:
            return distribute_rec(s.args[0])
        conjuncts = first(arg for arg in s.args if arg.op == '&')
        if not conjuncts:
            return s
        others = [a for a in s.args if a is not conjuncts]
        rest = join_terms('|', others)
        return join_terms('&', [distribute_rec(c | rest)
                                for c in conjuncts.args])
    elif s.op == '&':
        return join_terms('&', list(map(distribute_rec, s.args)))
    else:
        return s



def join_terms(op, args):
    args = disjoint_terms(op, args)
    if len(args) == 0:
        if op == '&':
            return True
        else:
            return False
    elif len(args) == 1:
        return args[0]
    else:
        return ComplexSentence(op, *args)


def disjoint_terms(op, args):
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg is not None and arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)


    collect(args)

    return result


def enum_conjunctions(s):
    return disjoint_terms('&', [s])


def enum_disjunctions(s):
    return disjoint_terms('|', [s])


def unify(x, y, theta={}):
    if theta is None or theta == '':
        return None
    elif x == y:
        return theta
    elif isvariable(x):
        return unify_var(x, y, theta)
    elif isvariable(y):
        return unify_var(y, x, theta)
    elif iscompound(x) and iscompound(y):
        return unify(x.args, y.args, unify(x.op, y.op, theta))
    elif isinstance(x, str) or isinstance(y, str):
        return None
    elif is_sequence(x) and is_sequence(y):
        if not x:
            return theta
        return unify(x[1:], y[1:], unify(x[0], y[0], theta))
    else:
        return None


def isvariable(x):
    return isinstance(x, ComplexSentence) and not x.args and x.op[0].islower()


def iscompound(x):
    return isinstance(x, ComplexSentence)


def islist(x):
    return isinstance(x, list)


def unify_var(var, x, theta):
    if var in theta:
        return unify(theta[var], x, theta)
    elif x in theta:
        return unify(var, theta[x], theta)
    elif occur_check(var, x, theta):
        return None
    else:
        return add(theta, var, x)


def add(theta, var, x):
    theta_temp = theta.copy()
    theta_temp[var] = x
    subst_rec(theta_temp)
    return theta_temp


def occur_check(var, x, s):
    if var == x:
        return True
    elif isvariable(x) and x in s:
        return occur_check(var, s[x], s)
    elif isinstance(x, ComplexSentence):
        return (occur_check(var, x.op, s) or
                occur_check(var, x.args, s))
    elif isinstance(x, list):
        return first(e for e in x if occur_check(var, e, s))
    else:
        return False


def subst(s, x):
    if isinstance(x, list):
        return [subst(s, xi) for xi in x]
    elif not isinstance(x, ComplexSentence):
        return x
    elif is_var_symbol(x.op):
        # print(type(s.get(x, x)))
        return s.get(x, x)
    else:
        return ComplexSentence(x.op, *[subst(s, arg) for arg in x.args])


def subst_rec(s):
    for x in s:
        s[x] = subst(s, s.get(x))
        if isinstance(s.get(x), ComplexSentence) and not isvariable(s.get(x)):
            # print(type(subst(s.get(x, x))))
            s[x] = subst(s, s.get(x))


def standardize_variables(sentence, dic=None):
    if dic is None:
        dic = {}
    if not isinstance(sentence, ComplexSentence):
        return sentence
    elif is_var_symbol(sentence.op):
        if sentence in dic:
            return dic[sentence]
        else:
            standardize_variables.counter += 1
            v = ComplexSentence('v_' + str(standardize_variables.counter))
            dic[sentence] = v
            return v
    else:
        return ComplexSentence(sentence.op, *[standardize_variables(a, dic) for a in sentence.args])


class KB:
    def __init__(self, initial_clauses=None):
        self.clauses = []
        if initial_clauses:
            for clause in initial_clauses:
                self.tell(clause)

    def tell(self, sentence):
        self.clauses.append(sentence)

    def ask_if_true(self, query):
        return pl_resolution(self, query)


def pl_resolution(kb, alpha):
    cnf_clauses = []
    for clause in kb.clauses:
        cnf_clauses.append(convert_to_cnf(clause))
    clauses = cnf_clauses + enum_conjunctions(convert_to_cnf(~alpha))
    new = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if False in resolvents:
                return True
            new = new.union(set(resolvents))
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)


def pl_resolve(ci, cj):
    clauses = []
    for di in enum_disjunctions(ci):
        for dj in enum_disjunctions(cj):
            cnf_dj_inverse = convert_to_cnf(~dj)
            phi = unify(di, cnf_dj_inverse)
            if phi or di == cnf_dj_inverse:
                new_clause = join_terms('|', unique(remove_all(di, enum_disjunctions(ci))) + remove_all(dj, enum_disjunctions(cj)))
                norm_clause = subst(phi, new_clause)
                clauses.append(norm_clause)
    return clauses


# Global variables
ComplexSentence.counter = 0

# Main program
kb1 = KB([expr('Take(x,Warfarin) => ~Take(x,NSAIDs)'), expr('Take(Alice,Warfarin)')])
print(kb1.ask_if_true(expr('Take(Alice,NSAIDs)')))

kb2 = KB([expr('Take(x,Warfarin) => ~Take(x,NSAIDs)'), expr('HighBP(x) => Alert(x,NSAIDs)'),
          expr('Take(Bob,Antacids)'), expr('Take(Bob,VitA)'), expr('HighBP(Bob)')])
print("\n")

print(kb2.ask_if_true(expr('Alert(Bob,NSAIDs)')))
print(kb2.ask_if_true(expr('Alert(Bob,VitC)')))

kb3 = KB(
    [expr('Migraine(x) & HighBP(x) => Take(x,Timolol)'), expr('Take(x,Warfarin) & Take(x,Timolol) => Alert(x,VitE)'),
     expr('Migraine(Alice)'), expr('Migraine(Bob)'), expr('HighBP(Bob)'), expr('OldAge(John)'), expr('HighBP(John)'),
     expr('Take(John,Timolol)'), expr('Take(Bob,Warfarin)')])

print("\n")

print(kb3.ask_if_true(expr('Alert(Alice,VitE)')))
print(kb3.ask_if_true(expr('Alert(Bob,VitE)')))
print(kb3.ask_if_true(expr('Alert(John,VitE)')))