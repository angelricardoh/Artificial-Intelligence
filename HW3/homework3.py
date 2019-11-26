import os.path
from os import path
import collections
import collections.abc
from timeit import default_timer as timer
import copy
import enum

# Global variables
ZERO = 0
ONE = 1
MAX_TIME_PER_QUERY = 40


class Operator(enum.Enum):
    negation = '~'
    or_op = '|'
    and_op = '&'
    implication = '=>'


class ComplexSentence:
    def __init__(self, operator, *arguments):
        self.operator = str(operator)
        # print("type:" + str(type(argumentList)))
        # if len(argumentList) == 1:
        #     print("type argumentList[0]:" + str(type(argumentList[0])))
        # if len(argumentList) == 2:
        #     print("type argumentList[1]:" + str(type(argumentList[1])))
        self.argument_list = arguments

    def __invert__(self):
        return ComplexSentence(Operator.negation.value, self)

    def __add__(self, right_node):
        return ComplexSentence('+', self, right_node)

    def __and__(self, right_node):
        return ComplexSentence(Operator.and_op.value, self, right_node)

    def __or__(self, right_node):
        class Sentence:
            def __init__(self, op, left_node):
                self.operator, self.left_node = op, left_node

            def __or__(self, right_inner_node):
                return ComplexSentence(self.operator, self.left_node, right_inner_node)

        if isinstance(right_node, ComplexSentence):
            return ComplexSentence(Operator.or_op.value, self, right_node)
        else:
            return Sentence(right_node, self)

    def __call__(self, *argument_list):
        if self.argument_list:
            print("Error element should not contain argument_list")
        else:
            return ComplexSentence(self.operator, *argument_list)

    def __eq__(self, other):
        return isinstance(other,
                          ComplexSentence) and self.operator == other.operator and \
               self.argument_list == other.argument_list

    def __equalOp__(self, other):
        return isinstance(other, ComplexSentence) and self.operator == other.operator

    def __hash__(self):
        return hash(self.operator) % hash(self.argument_list)


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
        unique_items = unique(eliminate(visited[i], enum_disjunctions(mod_ci)))
        unique_items.append(visited[i])
        mod_ci = join_terms(Operator.or_op.value, unique_items)
    return mod_ci


def terms(x):
    yield x
    if isinstance(x, ComplexSentence):
        for arg in x.argument_list:
            yield from terms(arg)


def build_sentence(expression):
    def handle_implications_disjunctions(inner_expression):
        implication = Operator.implication.value
        inner_expression = inner_expression.replace(implication, Operator.or_op.value + repr(implication) +
                                                    Operator.or_op.value)
        return inner_expression

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


def eliminate(term, sequence):
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


def convert_to_cnf(expression):
    def __eliminate_implications_rec(sentence):
        sentence = build_sentence(sentence)
        if not sentence.argument_list or is_symbol(sentence.operator):
            return sentence
        argument_list = list(map(__eliminate_implications_rec, sentence.argument_list))
        sentence_one, sentence_two = first(argument_list), argument_list[-1]
        if sentence.operator == Operator.implication.value:
            return sentence_two | ~sentence_one
        else:
            assert sentence.operator in [op.value for op in Operator]
            return ComplexSentence(sentence.operator, *argument_list)

    def __not(b):
        return __move_negation_inwards_rec(~b)

    def __move_negation_inwards_rec(sentence):
        sentence = build_sentence(sentence)
        if sentence.operator == Operator.negation.value:
            partial_sentence = first(sentence.argument_list)
            if partial_sentence.operator == Operator.negation.value:
                return __move_negation_inwards_rec(first(partial_sentence.argument_list))
            if partial_sentence.operator == Operator.and_op.value:
                return join_terms(Operator.or_op.value, list(map(__not, partial_sentence.argument_list)))
            if partial_sentence.operator == Operator.or_op.value:
                return join_terms(Operator.and_op.value, list(map(__not, partial_sentence.argument_list)))
            return sentence
        elif is_symbol(sentence.operator) or not sentence.argument_list:
            return sentence
        else:
            return ComplexSentence(sentence.operator, *list(map(__move_negation_inwards_rec, sentence.argument_list)))

    def __distribute_rec(sentence):
        sentence = build_sentence(sentence)
        if sentence.operator == Operator.or_op.value:
            sentence = join_terms(Operator.or_op.value, sentence.argument_list)
            args_num = len(sentence.argument_list)
            if sentence.operator != Operator.or_op.value:
                return __distribute_rec(sentence)
            if args_num == ZERO:
                return False
            if args_num == ONE:
                return __distribute_rec(first(sentence.argument_list))
            conjuncts = first(arg for arg in sentence.argument_list if arg.operator == Operator.and_op.value)
            if not conjuncts:
                return sentence
            others = [a for a in sentence.argument_list if a is not conjuncts]
            rest = join_terms(Operator.or_op.value, others)
            return join_terms(Operator.and_op.value, [__distribute_rec(c | rest)
                                    for c in conjuncts.argument_list])
        elif sentence.operator == Operator.and_op.value:
            return join_terms(Operator.and_op.value, list(map(__distribute_rec, sentence.argument_list)))
        else:
            return sentence

    # Build clause from string

    clause = build_sentence(expression)
    if isinstance(clause, str):
        clause = build_sentence(clause)

    # Eliminate implications

    clause = __eliminate_implications_rec(clause)

    # Move negation inwards

    clause = __move_negation_inwards_rec(clause)

    # Stardardize variables

    # clause = standardize_variables_rec(clause)

    # Distribute disjunctions over conjunctions

    clause = __distribute_rec(clause)

    return clause


def join_terms(operator, argument_list):
    argument_list = disjoint_terms(operator, argument_list)
    if len(argument_list) == ZERO:
        if operator == Operator.and_op.value:
            return True
        else:
            return False
    elif len(argument_list) == ONE:
        return first(argument_list)
    else:
        return ComplexSentence(operator, *argument_list)


def disjoint_terms(operator, argument_list):
    result = []

    def get_arguments(args_list):
        for arg in args_list:
            # print(type(operator))
            # print(type(arg.operator))
            if arg.operator == operator:
                get_arguments(arg.argument_list)
            else:
                result.append(arg)

    get_arguments(argument_list)
    return result


def enum_conjunctions(sentence):
    return disjoint_terms(Operator.and_op.value, [sentence])


def enum_disjunctions(sentence):
    return disjoint_terms(Operator.or_op.value, [sentence])


def is_variable(expression):
    return isinstance(expression, ComplexSentence) and not expression.argument_list and expression.operator[0].islower()


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
            x_var = ComplexSentence('x' + str(standardize_variables_rec.counter))
            variables_dict[sentence] = x_var
            return x_var
    else:
        return ComplexSentence(sentence.operator,
                               *[standardize_variables_rec(a, variables_dict) for a in sentence.argument_list])


class KB:
    def __init__(self, sentences=None):
        self.clauses = []
        if sentences:
            for clause in sentences:
                clause = standardize_variables_rec(clause)
                clause = convert_to_cnf(clause)
                clause = factorize(clause)
                self.tell(clause)

    def tell(self, sentence):
        self.clauses.append(sentence)

    def ask_if_true(self, query):
        return self.__binary_resolution(query)

    def __binary_resolution(self, alpha):
        start_time = timer()
        frontier = []
        loop_detector = []
        frontier.append(convert_to_cnf(~alpha))
        loop_detector.append(convert_to_cnf(~alpha))
        while frontier:
            current_sentence = frontier.pop()
            for clause in self.clauses:
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
                        if di.operator == Operator.negation.value:
                            unsigned_di = (convert_to_cnf(~di))
                            di_neg = True
                        if dj.operator == Operator.negation.value:
                            unsigned_dj = (convert_to_cnf(~dj))
                            dj_neg = True

                        # print("original_di: " + str(di) + " original_dj: " + str(dj))
                        if unsigned_di.__equalOp__(unsigned_dj) and (di_neg != dj_neg):
                            phi = self.__unify(di, convert_to_cnf(~dj))
                            if phi is not None:
                                new_clause = join_terms(Operator.or_op.value,
                                                        unique(eliminate(di, enum_disjunctions(ci))) + eliminate(dj,
                                                                                                                 enum_disjunctions(
                                                                                                                       cj)))
                                resolvent = self.__subst(phi, new_clause)
                                # print(len(loop_detector))
                                if resolvent is False:
                                    return True
                                resolvent = factorize(resolvent)
                                if resolvent not in loop_detector:
                                    # print(resolvent)
                                    frontier.append(resolvent)
                                    loop_detector.append(resolvent)
            elapsed_time = timer()
            if (elapsed_time - start_time) > MAX_TIME_PER_QUERY:
                return False
        return False

    def __unify(self, x, y, theta={}):
        if theta is None:
            return None
        elif x == y:
            return theta
        elif is_variable(x):
            return self.__unify_var(x, y, theta)
        elif is_variable(y):
            return self.__unify_var(y, x, theta)
        elif is_compound(x) and is_compound(y):
            return self.__unify(x.argument_list, y.argument_list, self.__unify(x.operator, y.operator, theta))
        elif isinstance(x, str) or isinstance(y, str):
            return None
        elif is_sequence(x) and is_sequence(y) and len(x) == len(y):
            if not x:
                return theta
            return self.__unify(all_elements_from_second(x), all_elements_from_second(y), self.__unify(first(x), first(y), theta))
        return None

    def __unify_var(self, var, x, theta):
        def occur_check(inner_var, expression, sentence):
            if inner_var == expression:
                return True
            elif is_variable(expression) and expression in sentence:
                return occur_check(inner_var, sentence[expression], sentence)
            elif isinstance(expression, ComplexSentence):
                return (occur_check(inner_var, expression.operator, sentence) or
                        occur_check(inner_var, expression.argument_list, sentence))
            elif isinstance(expression, (list, tuple)):
                return first(x for x in expression if occur_check(inner_var, x, sentence))
            else:
                return False

        def add(inner_theta, inner_var, x):
            new_theta = inner_theta.copy()
            new_theta[inner_var] = x
            for term in new_theta:
                new_theta[term] = self.__subst(new_theta, new_theta.get(term))
                if isinstance(new_theta.get(term), ComplexSentence) and not is_variable(new_theta.get(term)):
                    new_theta[term] = self.__subst(new_theta, new_theta.get(term))
            return new_theta

        if var in theta:
            return self.__unify(theta[var], x, theta)
        elif x in theta:
            return self.__unify(var, theta[x], theta)
        elif occur_check(var, x, theta):
            return None
        else:
            return add(theta, var, x)

    def __subst(self, sentence, expression):
        if isinstance(expression, list):
            return [self.__subst(sentence, term) for term in expression]
        elif isinstance(expression, tuple):
            return tuple([self.__subst(sentence, term) for term in expression])
        elif not isinstance(expression, ComplexSentence):
            return expression
        elif is_var_symbol(expression.operator):
            return sentence.get(expression, expression)
        else:
            return ComplexSentence(expression.operator, *[self.__subst(sentence, arg) for arg in expression.argument_list])


standardize_variables_rec.counter = 0


def main():
    # start_time = timer()
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
    # end_time = timer()

    # Comment before submitting
    # for result in results:
    #     print(result)
    # print("total current logic iteration " + str(end_time - start_time) + " seg")


if __name__ == '__main__':
    main()
