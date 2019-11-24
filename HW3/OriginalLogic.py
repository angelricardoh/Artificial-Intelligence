import os.path
from os import path
import collections
import collections.abc
import itertools

class Expr:
    def __init__(self, op, *args):
        self.op = str(op)
        self.args = args

    def __invert__(self):
        return Expr('~', self)

    def __and__(self, rhs):
        return Expr('&', self, rhs)

    def __or__(self, rhs):
        if isinstance(rhs, Expr):
            return Expr('|', self, rhs)
        else:
            return PartialExpr(rhs, self)

    def __call__(self, *args):
        if self.args:
            raise ValueError('can only do a call for a Symbol, not an Expr')
        else:
            return Expr(self.op, *args)

    def __eq__(self, other):
        return isinstance(other, Expr) and self.op == other.op and self.args == other.args

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)

def Symbol(name):
    return Expr(name)


def symbols(names):
    return tuple(Symbol(name) for name in names.replace(',', ' ').split())


def subexpressions(x):
    yield x
    if isinstance(x, Expr):
        for arg in x.args:
            yield from subexpressions(arg)


def arity(expression):
    if isinstance(expression, Expr):
        return len(expression.args)
    else:  # expression is a number
        return 0


class PartialExpr:
    def __init__(self, op, lhs):
        self.op, self.lhs = op, lhs

    def __or__(self, rhs):
        return Expr(self.op, self.lhs, rhs)

    def __repr__(self):
        return "PartialExpr('{}', {})".format(self.op, self.lhs)


def expr(x):
    return eval(expr_handle_infix_ops(x), defaultkeydict(Symbol)) if isinstance(x, str) else x

def first(iterable, default=None):
    return next(iter(iterable), default)

def extend(self, items):
    for item in items:
        self.append(item)

def extend(s, var, val):
    s2 = s.copy()
    s2[var] = val
    return s2

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


def issequence(x):
    return isinstance(x, collections.abc.Sequence)


def expr_handle_infix_ops(x):
    for op in infix_ops:
        x = x.replace(op, '|' + repr(op) + '|')
    return x


class defaultkeydict(collections.defaultdict):
    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result


def is_symbol(s):
    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):
    return is_symbol(s) and s[0].islower()


def is_prop_symbol(s):
    return is_symbol(s) and s[0].isupper()


def variables(s):
    return {x for x in subexpressions(s) if is_variable(x)}


def to_cnf(s):
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
        return Expr(s.op, *args)


def move_not_inwards(s):
    s = expr(s)
    if s.op == '~':
        def NOT(b):
            return move_not_inwards(~b)

        a = s.args[0]
        if a.op == '~':
            return move_not_inwards(a.args[0])  # ~~A ==> A
        if a.op == '&':
            return associate('|', list(map(NOT, a.args)))
        if a.op == '|':
            return associate('&', list(map(NOT, a.args)))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return Expr(s.op, *list(map(move_not_inwards, s.args)))


def distribute_and_over_or(s):
    s = expr(s)
    if s.op == '|':
        s = associate('|', s.args)
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
        rest = associate('|', others)
        return associate('&', [distribute_and_over_or(c | rest)
                               for c in conj.args])
    elif s.op == '&':
        return associate('&', list(map(distribute_and_over_or, s.args)))
    else:
        return s


def associate(op, args):
    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)


def dissociate(op, args):
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result


def conjuncts(s):
    return dissociate('&', [s])


def disjuncts(s):
    return dissociate('|', [s])


def unify(x, y, s={}):
    if s is None:
        return None
    elif x == y:
        return s
    elif is_variable(x):
        return unify_var(x, y, s)
    elif is_variable(y):
        return unify_var(y, x, s)
    elif isinstance(x, Expr) and isinstance(y, Expr):
        return unify(x.args, y.args, unify(x.op, y.op, s))
    elif isinstance(x, str) or isinstance(y, str):
        return None
    elif issequence(x) and issequence(y) and len(x) == len(y):
        if not x:
            return s
        return unify(x[1:], y[1:], unify(x[0], y[0], s))
    else:
        return None


def is_variable(x):
    return isinstance(x, Expr) and not x.args and x.op[0].islower()


def unify_var(var, x, s):
    if var in s:
        return unify(s[var], x, s)
    elif x in s:
        return unify(var, s[x], s)
    elif occur_check(var, x, s):
        return None
    else:
        new_s = extend(s, var, x)
        cascade_substitution(new_s)
        return new_s


def occur_check(var, x, s):
    if var == x:
        return True
    elif is_variable(x) and x in s:
        return occur_check(var, s[x], s)
    elif isinstance(x, Expr):
        return (occur_check(var, x.op, s) or
                occur_check(var, x.args, s))
    elif isinstance(x, (list, tuple)):
        return first(e for e in x if occur_check(var, e, s))
    else:
        return False


def subst(s, x):
    if isinstance(x, list):
        return [subst(s, xi) for xi in x]
    elif isinstance(x, tuple):
        return tuple([subst(s, xi) for xi in x])
    elif not isinstance(x, Expr):
        return x
    elif is_var_symbol(x.op):
        return s.get(x, x)
    else:
        return Expr(x.op, *[subst(s, arg) for arg in x.args])


def cascade_substitution(s):
    for x in s:
        s[x] = subst(s, s.get(x))
        if isinstance(s.get(x), Expr) and not is_variable(s.get(x)):
            s[x] = subst(s, s.get(x))


def standardize_variables(sentence, dic=None):
    if dic is None:
        dic = {}
    if not isinstance(sentence, Expr):
        return sentence
    elif is_var_symbol(sentence.op):
        if sentence in dic:
            return dic[sentence]
        else:
            v = Expr('v_{}'.format(next(standardize_variables.counter)))
            dic[sentence] = v
            return v
    else:
        return Expr(sentence.op, *[standardize_variables(a, dic) for a in sentence.args])


class KB():
    def __init__(self, initial_clauses=None):
        self.clauses = []
        if initial_clauses:
            for clause in initial_clauses:
                self.tell(clause)

    def tell(self, sentence):
        self.clauses.append(sentence)

    def ask_if_true(self, query):
        return pl_resolution(self, query)

    def retract(self, sentence):
        self.clauses.remove(sentence)

    def fetch_rules_for_goal(self, goal):
        return self.clauses


def pl_resolution(kb, alpha):
    cnf_clauses = []
    for clause in kb.clauses:
        cnf_clauses.append(to_cnf(clause))
        # print(to_cnf(clause))
    clauses = cnf_clauses + conjuncts(to_cnf(~alpha))
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
    # print("ci = ", ci)
    # print("cj = ", cj)
    for di in disjuncts(ci):
        for dj in disjuncts(cj):
            # print("di = ", di)
            # print("dj = ", to_cnf(~dj))
            phi = unify(di, to_cnf(~dj))
            if phi or di == to_cnf(~dj):
                new_clause = associate('|', unique(remove_all(di, disjuncts(ci))) + remove_all(dj, disjuncts(cj)))
                norm_clause = subst(phi, new_clause)
                clauses.append(norm_clause)
    return clauses


# Global variables
infix_ops = '=>'.split()
_op_identity = {'&': True, '|': False}
standardize_variables.counter = itertools.count()

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
