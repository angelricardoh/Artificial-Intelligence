import os.path
from os import path
import collections
import collections.abc
from timeit import default_timer as timer
import copy


def resolution(kb, alpha):
    frontier = []
    loop_detector = []
    frontier.append(convert_to_cnf(~alpha))
    loop_detector.append(convert_to_cnf(~alpha))
    while frontier:
        current_sentence = frontier.pop()
        for clause in kb.clauses:
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
                    if di.operator == '~':
                        unsigned_di = (convert_to_cnf(~di))
                        di_neg = True
                    if dj.operator == '~':
                        unsigned_dj = (convert_to_cnf(~dj))
                        dj_neg = True

                    # print("original_di: " + str(di) + " original_dj: " + str(dj))
                    if unsigned_di.__equalOp__(unsigned_dj) and (di_neg != dj_neg):
                        phi = unify(di, convert_to_cnf(~dj))
                        if phi is not None:
                            new_clause = join_terms('|', unique(remove_all(di, enum_disjunctions(ci))) + remove_all(dj,
                                                                                                                    enum_disjunctions(
                                                                                                                        cj)))
                            resolvent = subst(phi, new_clause)
                            if resolvent is False:
                                print(len(loop_detector))
                                return True
                            resolvent = factorize(resolvent)
                            if resolvent not in loop_detector:
                                # print(resolvent)
                                frontier.append(resolvent)
                                loop_detector.append(resolvent)
                                if len(frontier) > MAX_SENTENCE_CAPACITY:
                                    return False
    print(len(loop_detector))
    return False


def factorize(s):
    # print("s + ", s)
    di = enum_disjunctions(s)
    mod_ci = s
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


def terms(x):
    yield x
    if isinstance(x, ComplexSentence):
        for arg in x.argumentList:
            yield from terms(arg)


def build_sentence(expression):
    def handle_implications_disjunctions(expression):
        implication = '=>'
        expression = expression.replace(implication, '|' + repr(implication) + '|')
        return expression

    if isinstance(expression, str):
        y = SentencesDictionary(ComplexSentence)
        return eval(handle_implications_disjunctions(expression), y)
    else:
        return expression


def first(iterable):
    if isinstance(iterable, list) or isinstance(iterable, tuple):
        return iterable[0]
    return None


def first(iterable, element=None):
    return next(iter(iterable), element)


def all_elements_from_second(iterable):
    return iterable[1:]


def remove_all(term, sequence):
    if isinstance(sequence, str):
        return sequence.replace(term, '')
    elif isinstance(sequence, set):
        sequence_copy = sequence.copy()
        sequence_copy.remove(term)
        return sequence_copy
    else:
        return [expression for expression in sequence if expression != term]


def unique(sequence):
    return list(set(sequence))


class SentencesDictionary(collections.defaultdict):
    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result


def convert_to_cnf(clause):
    def eliminate_implications_rec(sentence):
        sentence = build_sentence(sentence)
        if not sentence.argumentList or is_symbol(sentence.operator):
            return sentence
        argumentList = list(map(eliminate_implications_rec, sentence.argumentList))
        sentenceOne, sentenceTwo = first(argumentList), argumentList[-1]
        if sentence.operator == '=>':
            return sentenceTwo | ~sentenceOne
        else:
            assert sentence.operator in ('&', '|', '~')
            return ComplexSentence(sentence.operator, *argumentList)

    def NOT(b):
        return move_negation_inwards_rec(~b)

    def move_negation_inwards_rec(sentence):
        sentence = build_sentence(sentence)
        if sentence.operator == '~':
            partialSentence = first(sentence.argumentList)
            if partialSentence.operator == '~':
                return move_negation_inwards_rec(first(partialSentence.argumentList))
            if partialSentence.operator == '&':
                return join_terms('|', list(map(NOT, partialSentence.argumentList)))
            if partialSentence.operator == '|':
                return join_terms('&', list(map(NOT, partialSentence.argumentList)))
            return sentence
        elif is_symbol(sentence.operator) or not sentence.argumentList:
            return sentence
        else:
            return ComplexSentence(sentence.operator, *list(map(move_negation_inwards_rec, sentence.argumentList)))

    def distribute_rec(sentence):
        sentence = build_sentence(sentence)
        if sentence.operator == '|':
            sentence = join_terms('|', sentence.argumentList)
            args_num = len(sentence.argumentList)
            if sentence.operator != '|':
                return distribute_rec(sentence)
            if args_num == ZERO:
                return False
            if args_num == ONE:
                return distribute_rec(first(sentence.argumentList))
            conjuncts = first(arg for arg in sentence.argumentList if arg.operator == '&')
            if not conjuncts:
                return sentence
            others = [a for a in sentence.argumentList if a is not conjuncts]
            rest = join_terms('|', others)
            return join_terms('&', [distribute_rec(c | rest)
                                    for c in conjuncts.argumentList])
        elif sentence.operator == '&':
            return join_terms('&', list(map(distribute_rec, sentence.argumentList)))
        else:
            return sentence

    clause = build_sentence(clause)
    if isinstance(clause, str):
        clause = build_sentence(clause)

    # Eliminate implications

    clause = eliminate_implications_rec(clause)

    # Move negation inwards

    clause = move_negation_inwards_rec(clause)

    # Stardardize variables

    # s = standardize_variables_rec(s)

    # Distribute disjunctions over conjunctions

    clause = distribute_rec(clause)

    return clause


def join_terms(operator, argumentList):
    argumentList = disjoint_terms(operator, argumentList)
    if len(argumentList) == ZERO:
        if operator == '&':
            return True
        else:
            return False
    elif len(argumentList) == ONE:
        return first(argumentList)
    else:
        return ComplexSentence(operator, *argumentList)


def disjoint_terms(operator, argumentList):
    result = []

    def get_arguments(argsList):
        for arg in argsList:
            # print(type(operator))
            # print(type(arg.operator))
            if arg.operator == operator:
                get_arguments(arg.argumentList)
            else:
                result.append(arg)

    get_arguments(argumentList)
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
        return unify(x.argumentList, y.argumentList, unify(x.operator, y.operator, theta))
    elif isinstance(x, str) or isinstance(y, str):
        return None
    elif is_sequence(x) and is_sequence(y) and len(x) == len(y):
        if not x:
            return theta
        return unify(all_elements_from_second(x), all_elements_from_second(y), unify(first(x), first(y), theta))
    return None


def is_variable(expression):
    return isinstance(expression, ComplexSentence) and not expression.argumentList and expression.operator[0].islower()


def is_compound(expression):
    return isinstance(expression, ComplexSentence)


def is_list(expression):
    return isinstance(expression, list) or isinstance(expression, tuple)


def is_sequence(expression):
    return isinstance(expression, collections.abc.Sequence)


def is_symbol(string):
    return isinstance(string, str) and string[:1].isalpha()


def is_var_symbol(expression):
    return is_symbol(expression) and expression[0].islower()


def unify_var(var, expression, theta):
    def add(inner_theta, var, x):
        new_theta = inner_theta.copy()
        new_theta[var] = x
        for term in new_theta:
            new_theta[term] = subst(new_theta, new_theta.get(term))
            if isinstance(new_theta.get(term), ComplexSentence) and not is_variable(new_theta.get(term)):
                new_theta[term] = subst(new_theta, new_theta.get(term))
        return new_theta

    if var in theta:
        return unify(theta[var], expression, theta)
    elif expression in theta:
        return unify(var, theta[expression], theta)
    elif occur_check(var, expression, theta):
        return None
    else:
        return add(theta, var, expression)


def occur_check(var, expression, sentence):
    if var == expression:
        return True
    elif is_variable(expression) and expression in sentence:
        return occur_check(var, sentence[expression], sentence)
    elif isinstance(expression, ComplexSentence):
        return (occur_check(var, expression.operator, sentence) or
                occur_check(var, expression.argumentList, sentence))
    elif isinstance(expression, (list, tuple)):
        return first(x for x in expression if occur_check(var, x, sentence))
    else:
        return False


def subst(sentence, expression):
    if isinstance(expression, list):
        return [subst(sentence, term) for term in expression]
    elif isinstance(expression, tuple):
        return tuple([subst(sentence, term) for term in expression])
    elif not isinstance(expression, ComplexSentence):
        return expression
    elif is_var_symbol(expression.operator):
        return sentence.get(expression, expression)
    else:
        return ComplexSentence(expression.operator, *[subst(sentence, arg) for arg in expression.argumentList])


def standardize_variables_rec(sentence, variables_dict=None):
    if variables_dict is None:
        variables_dict = {}
    if not isinstance(sentence, ComplexSentence):
        return sentence
    elif is_var_symbol(sentence.operator):
        if sentence in variables_dict:
            return variables_dict[sentence]
        else:
            standardize_variables_rec.counter += 1
            v = ComplexSentence('v_' + str(standardize_variables_rec.counter))
            variables_dict[sentence] = v
            return v
    else:
        return ComplexSentence(sentence.operator,
                               *[standardize_variables_rec(a, variables_dict) for a in sentence.argumentList])


class KB:
    def __init__(self, sentences=None):
        self.clauses = []
        if sentences:
            for clause in sentences:
                clause = standardize_variables_rec(clause)
                clause = convert_to_cnf(clause)
                self.tell(clause)

    def tell(self, sentence):
        self.clauses.append(sentence)

    def ask_if_true(self, query):
        return resolution(self, query)


class ComplexSentence:
    sentenceId = 0

    def __init__(self, operator, *arguments):
        self.operator = str(operator)
        # print("type:" + str(type(argumentList)))
        # if len(argumentList) == 1:
        #     print("type argumentList[0]:" + str(type(argumentList[0])))
        # if len(argumentList) == 2:
        #     print("type argumentList[1]:" + str(type(argumentList[1])))
        self.argumentList = arguments

    def __invert__(self):
        return ComplexSentence('~', self)

    def __add__(self, rightNode):
        return ComplexSentence('+', self, rightNode)

    def __and__(self, rightNode):
        return ComplexSentence('&', self, rightNode)

    def __or__(self, rightNode):
        class Sentence:
            def __init__(self, op, leftNode):
                self.op, self.leftNode = op, leftNode

            def __or__(self, rightInnerNode):
                return ComplexSentence(self.op, self.leftNode, rightInnerNode)

            # def __repr__(self):
            #     return "Sentence('{}', {})".format(self.op, self.lhs)

        if isinstance(rightNode, ComplexSentence):
            return ComplexSentence('|', self, rightNode)
        else:
            return Sentence(rightNode, self)

    def __call__(self, *argumentList):
        if self.argumentList:
            print("Error element should not contain argumentList")
        else:
            return ComplexSentence(self.operator, *argumentList)

    def __eq__(self, other):
        return isinstance(other,
                          ComplexSentence) and self.operator == other.operator and self.argumentList == other.argumentList

    def __equalOp__(self, other):
        return isinstance(other, ComplexSentence) and self.operator == other.operator

    def __hash__(self):
        return hash(self.operator) % hash(self.argumentList)

    # def __repr__(self):
    #     op = self.operator
    #     argumentList = [str(arg) for arg in self.argumentList]
    #     if op.isidentifier():
    #         return '{}({})'.format(op, ', '.join(argumentList)) if argumentList else op
    #     elif len(argumentList) == 1:
    #         return op + argumentList[0]
    #     else:
    #         opp = (' ' + op + ' ')
    #         return '(' + opp.join(argumentList) + ')'


# Global variables
standardize_variables_rec.counter = 0
ZERO = 0
ONE = 1
MAX_SENTENCE_CAPACITY = 15000


def main():
    start_time = timer()
    input_f = open("input.txt", "r")
    number_of_queries = int(input_f.readline().rstrip())
    queries = []
    for i in range(number_of_queries):
        queries.append(build_sentence(input_f.readline().rstrip()))
    number_of_sentences = int(input_f.readline().rstrip())
    sentences = []
    for i in range(number_of_sentences):
        sentences.append(build_sentence(input_f.readline().rstrip()))

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
    for result in results:
        print(result)
    print("total current logic iteration " + str(end_time - start_time) + " seg")


if __name__ == '__main__':
    main()
