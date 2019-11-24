import os.path
from os import path
import collections
import collections.abc
from timeit import default_timer as timer
import copy


class ComplexSentence:
    def __init__(self, op, *args):
        self.op = str(op)
        # print("type:" + str(type(args)))
        # if len(args) == 1:
        #     print("type args[0]:" + str(type(args[0])))
        # if len(args) == 2:
        #     print("type args[1]:" + str(type(args[1])))
        self.args = args

    def __invert__(self):
        return ComplexSentence('~', self)

    def __add__(self, rhs):
        return ComplexSentence('+', self, rhs)

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

    def __equalOp__(self, other):
        return isinstance(other, ComplexSentence) and self.op == other.op

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)

    # def __repr__(self):
    #     op = self.op
    #     args = [str(arg) for arg in self.args]
    #     if op.isidentifier():
    #         return '{}({})'.format(op, ', '.join(args)) if args else op
    #     elif len(args) == 1:
    #         return op + args[0]
    #     else:
    #         opp = (' ' + op + ' ')
    #         return '(' + opp.join(args) + ')'


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


def Symbol(name):
    return ComplexSentence(name)


def symbols(names):
    return tuple(Symbol(name) for name in names.replace(',', ' ').split())


class Sentence:
    def __init__(self, op, lhs):
        self.op, self.lhs = op, lhs

    def __or__(self, rhs):
        return ComplexSentence(self.op, self.lhs, rhs)

    def __repr__(self):
        return "Sentence('{}', {})".format(self.op, self.lhs)


def expr(x):
    if isinstance(x, str):
        y = SentencesDictionary(Symbol)
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


def handle_implications_disjuncts(x):
    op = '=>'
    x = x.replace(op, '|' + repr(op) + '|')
    return x


class SentencesDictionary(collections.defaultdict):
    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result


def variables(s):
    return {x for x in subexpressions(s) if is_variable(x)}


def convert_to_cnf(s):
    s = expr(s)
    if isinstance(s, str):
        s = expr(s)

    # Eliminate implications

    s = eliminate_implications(s)

    # Move negation inwards

    s = move_negation_inwards_rec(s)

    # Stardardize variables

    # s = standardize_variables_rec(s)

    # Distribute disjunctions over conjunctions

    s = distribute_rec(s)

    return s


def eliminate_implications(s):
    s = expr(s)
    if not s.args or is_symbol(s.op):
        return s
    args = list(map(eliminate_implications, s.args))
    a, b = args[0], args[-1]
    if s.op == '=>':
        return b | ~a
    else:
        assert s.op in ('&', '|', '~')
        return ComplexSentence(s.op, *args)


def NOT(b):
    return move_negation_inwards_rec(~b)


def move_negation_inwards_rec(s):
    s = expr(s)
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


def standardize_variables_rec(sentence, dic=None):
    if dic is None:
        dic = {}
    if not isinstance(sentence, ComplexSentence):
        return sentence
    elif is_var_symbol(sentence.op):
        if sentence in dic:
            return dic[sentence]
        else:
            standardize_variables_rec.counter += 1
            v = ComplexSentence('v_' + str(standardize_variables_rec.counter))
            dic[sentence] = v
            return v
    else:
        return ComplexSentence(sentence.op, *[standardize_variables_rec(a, dic) for a in sentence.args])


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
            if arg.op == op:
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
    if theta is None:
        return None
    elif x == y:
        return theta
    elif is_variable(x):
        return unify_var(x, y, theta)
    elif is_variable(y):
        return unify_var(y, x, theta)
    elif is_compound(x) and is_compound(y):
        return unify(x.args, y.args, unify(x.op, y.op, theta))
    elif isinstance(x, str) or isinstance(y, str):
        return None
    elif is_sequence(x) and is_sequence(y) and len(x) == len(y):
        if not x:
            return theta
        return unify(x[1:], y[1:], unify(x[0], y[0], theta))
    else:
        return None


def is_variable(x):
    return isinstance(x, ComplexSentence) and not x.args and x.op[0].islower()


def is_compound(x):
    return isinstance(x, ComplexSentence)


def is_list(x):
    return isinstance(x, list) or isinstance(x, tuple)


def is_sequence(x):
    return isinstance(x, collections.abc.Sequence)


def is_symbol(s):
    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):
    return is_symbol(s) and s[0].islower()


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
    elif is_variable(x) and x in s:
        return occur_check(var, s[x], s)
    elif isinstance(x, ComplexSentence):
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
    elif not isinstance(x, ComplexSentence):
        return x
    elif is_var_symbol(x.op):
        return s.get(x, x)
    else:
        return ComplexSentence(x.op, *[subst(s, arg) for arg in x.args])


def subst_rec(s):
    for x in s:
        s[x] = subst(s, s.get(x))
        if isinstance(s.get(x), ComplexSentence) and not is_variable(s.get(x)):
            s[x] = subst(s, s.get(x))


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


# def pl_resolution(kb, alpha):
#     cnf_clauses = []
#     # subexpression_n = 0
#     for clause in kb.clauses:
#         clause = standardize_variables_rec(clause)
#         clause = convert_to_cnf(clause)
#         # for exp in subexpressions(clause):
#         #     print(exp)
#         #     subexpression_n += 1
#         # print(subexpression_n)
#         cnf_clauses.append(clause)
#         # print(convert_to_cnf(clause))
#     clauses = cnf_clauses + enum_conjunctions(convert_to_cnf(~alpha))
#     new = set()
#     iterations = 1
#     while True:
#         n = len(clauses)
#         # print(n)
#         # for c in clauses:
#         #     print(c)
#
#         pairs = [(clauses[i], clauses[j])
#                  for i in range(n) for j in range(i + 1, n)]
#         for (ci, cj) in pairs:
#             resolvents = pl_resolve(ci, cj)
#             if False in resolvents:
#                 return True
#             new = new.union(set(resolvents))
#             # print(len(new) + len(clauses))
#
#
#         if new.issubset(set(clauses)):
#             return False
#         for c in new:
#             if c not in clauses:
#                 clauses.append(c)
#
#
# def pl_resolve(ci, cj):
#     clauses = []
#     # print("ci = ", ci)
#     # print("cj = ", cj)
#     for di in enum_disjunctions(ci):
#         for dj in enum_disjunctions(cj):
#             # print("di = ", di)
#             # print("dj = ", to_cnf(~dj))
#             original_di = di
#             original_dj = dj
#             # print("origin_di " + str(original_di))
#             # print("original_dj " + str(original_dj))
#             di_neg = False
#             dj_neg = False
#             if di.op == '~':
#                 di = (convert_to_cnf(~di))
#                 di_neg = True
#             if dj.op == '~':
#                 dj = (convert_to_cnf(~dj))
#                 dj_neg = True
#
#             if di.__equalOp__(dj) and (di_neg != dj_neg):
#                 phi = unify(original_di, convert_to_cnf(~original_dj))
#                 if phi is not None:
#                     new_clause = join_terms('|',
#                                             unique(remove_all(original_di, enum_disjunctions(ci))) + remove_all(
#                                                 original_dj,
#                                                 enum_disjunctions(
#                                                     cj)))
#                     resolvent = subst(phi, new_clause)
#                     resolvent = factorize(resolvent)
#                     print(resolvent)
#                     if resolvent not in clauses:
#                         clauses.append(resolvent)
#     return clauses


def pl_resolution(kb, alpha):
    cnf_clauses = []
    for clause in kb.clauses:
        clause = standardize_variables_rec(clause)
        clause = convert_to_cnf(clause)
        cnf_clauses.append(clause)
    frontier = []
    loop_detector = []
    frontier.append(convert_to_cnf(~alpha))
    loop_detector.append(convert_to_cnf(~alpha))
    while frontier:
        current_sentence = frontier.pop()
        for clause in cnf_clauses:
            ci = current_sentence
            cj = clause
            # print("ci: " + str(ci))
            # print("cj: " + str(cj))
            for di in enum_disjunctions(ci):
                for dj in enum_disjunctions(cj):
                    unsigned_di = copy.deepcopy(di)
                    unsigned_dj = copy.deepcopy(dj)
                    di_neg = False
                    dj_neg = False
                    if di.op == '~':
                        unsigned_di = (convert_to_cnf(~di))
                        di_neg = True
                    if dj.op == '~':
                        unsigned_dj = (convert_to_cnf(~dj))
                        dj_neg = True

                    # print("original_di: " + str(di) + " original_dj: " + str(dj))
                    if unsigned_di.__equalOp__(unsigned_dj) and (di_neg != dj_neg):
                        phi = unify(di, convert_to_cnf(~dj))
                        if phi is not None:
                            new_clause = join_terms('|', unique(remove_all(di, enum_disjunctions(ci))) + remove_all(dj,
                                                        enum_disjunctions(cj)))
                            resolvent = subst(phi, new_clause)
                            if resolvent is False:
                                return True
                            resolvent = factorize(resolvent)
                            if resolvent not in loop_detector:
                                # print(resolvent)
                                frontier.append(resolvent)
                                loop_detector.append(resolvent)
    return False


def factorize(s):
    ci = s
    # print("s + ", s)
    di = enum_disjunctions(s)
    mod_ci = ci
    visited = []
    # print("di + " + str(di))
    for i in range(0, len(di)):
        for j in range(i + 1, len(di)):
            if di[i] == di[j] and di[i] not in visited:
                visited.append(di[i])
    # print("visited + " + str(visited))
    for i in range(0, len(visited)):
        # print("visited " + str(i) + " : " + str(visited[i]))
        # print(unique(remove_all(visited[i], enum_disjunctions(mod_ci))))
        unique_items = unique(remove_all(visited[i], enum_disjunctions(mod_ci)))
        unique_items.append(visited[i])
        mod_ci = join_terms('|', unique_items)
    return mod_ci


# Global variables
standardize_variables_rec.counter = 0


def main():
    start_time = timer()
    input_f = open("input.txt", "r")
    number_of_queries = int(input_f.readline().rstrip())
    queries = []
    for i in range(number_of_queries):
        queries.append(expr(input_f.readline().rstrip()))
    number_of_sentences = int(input_f.readline().rstrip())
    sentences = []
    for i in range(number_of_sentences):
        sentences.append(expr(input_f.readline().rstrip()))

    kb = KB(sentences)
    results = []
    for query in queries:
        results.append(kb.ask_if_true(query))

    if path.exists("output.txt"):
        os.remove("output.txt")

    output_f = open("output.txt", 'w')
    for i in range(0, len(results)):
        output_f.write(str(results[i]).upper())
        if i != len(results) - 1:
            output_f.write("\n")
    output_f.close()
    end_time = timer()

    # Comment before submitting
    # for result in results:
    #     print(result)
    # print("total current logic iteration " + str(end_time - start_time) + " seg")


if __name__ == '__main__':
    main()
