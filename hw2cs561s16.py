import sys
import collections

OPERATORS = ['&&', '=>']

KB = collections.OrderedDict()

parent_clauses = collections.OrderedDict()


class KnowledgeBase:
    def __init__(self, initial_clauses=[]):
        # we will use the operator of the clauses for indexing
        self.clauses = collections.OrderedDict()
        for clause in initial_clauses:
            self.tell(clause)

    def tell(self, clause):
        self.predicate_index(clause, clause)

    # def predicate_index(self, main_clause, inside_clause):
    #     if inside_clause.op[0] == '~':
    #         temp = str(inside_clause.op)
    #         if temp in self.clauses:
    #             if main_clause not in self.clauses[temp]:
    #                 self.clauses[temp].append(main_clause)
    #         else:
    #             # create a new entry
    #             self.clauses[temp] = [main_clause]
    #     elif is_predicate(inside_clause):
    #         # simply add the main clause to the kb giving the name of the
    #         # predicate as the key
    #         if inside_clause.op in self.clauses:
    #             # check if the clause already exists
    #             if main_clause not in self.clauses[inside_clause.op]:
    #                 self.clauses[inside_clause.op].append(main_clause)
    #         else:
    #             # create a new entry
    #             self.clauses[inside_clause.op] = [main_clause]
    #     # elif inside_clause.op[0] == '~':
    #     #     self.predicate_index(main_clause, str(inside_clause.op))
    #     else:
    #         # one of the other operators
    #         # add both its arguments to the dictionary
    #         print "INSIDE 0"
    #         print inside_clause.args[0]
    #         self.predicate_index(main_clause, inside_clause.args[0])
    #         print inside_clause.args[1]
    #         self.predicate_index(main_clause, inside_clause.args[1])

    def predicate_index(self, main_clause, inside_clause):

        """
        Indexes the clause by each predicate for efficient unification.
        main_clause will be the clause that we're asked to add to the knowledge base.
        inside_clause will be the clause that exists inside the main_clause
        """

        if is_predicate(inside_clause):
            # simply add the main clause to the kb giving the name of the
            # predicate as the key
            if inside_clause.op in self.clauses:
                # check if the clause already exists
                if main_clause not in self.clauses[inside_clause.op]:
                    self.clauses[inside_clause.op].append(main_clause)
            else:
                # create a new entry
                self.clauses[inside_clause.op] = [main_clause]
        elif inside_clause.op[0] == '~':
            self.predicate_index(main_clause, inside_clause.op)
        else:
            # one of the other operators
            # add both its arguments to the dictionary
            self.predicate_index(main_clause, inside_clause.args[0])
            self.predicate_index(main_clause, inside_clause.args[1])


    def fetch_rules_for_goal(self, goal):
        predicate = self.retrieve_predicate(goal)
        if predicate in self.clauses:
            return self.clauses[predicate]

    def retrieve_predicate(self, goal):
        if is_predicate(goal):
            return goal.op
        else:
            # works if op is '~' or any other symbol
            # because there is always one argument if the symbol is a logical symbol
            return self.retrieve_predicate(goal.args[0])

    def ask(self, query):
        return fol_bc_ask(self, query)

class Clause:
    def __init__(self, op, args=[], parents=None):
        """
        Op (operator) is a logical operator such as '&', '|' etc, or string, such
        as 'P' or 'Likes' (the proposition) stored as a string.
        Args are the arguments in the clause, for e.g. in Likes(X, Y) X and Y are
        the arguments.
        Parents are the clauses from which the current clause has been derived.
        This is helpful for showing the proof process. It defaults to None.
        """

        self.op = op
        self.parents = parents
        self.args = map(convert_to_clause, args)


    def __hash__(self):
        return hash(self.op) ^ hash(tuple(self.args))


    def __repr__(self):
        if len(self.args) == 0:
            # simple proposition, just print it out
            return self.op
        elif self.op not in OPERATORS:
            # again simple clause but with arguments like Strong(Superman)
            # again print it out as it is
            args = str(self.args[0])
            for arg in self.args[1:]:
                args = args + ', ' + str(arg)
            return self.op + '(' + args + ')'
        elif self.op == '~':
            if self.args[0].op not in OPERATORS:
                # statement like ~Loves(Batman, Joker)
                # so no need for parens after '~'
                return '~' + str(self.args[0])
            else:
                return '~' + '(' + str(self.args[0]) + ')'
        else:
            # binary operator like '&&', '|' or '=>'
            # check if argument clauses have logical operators
            str_repn = ''
            if self.args[0].op in OPERATORS:
                str_repn = '(' + str(self.args[0]) + ')'
            else:
                str_repn = str(self.args[0])
            str_repn += ' ' + self.op + ' '
            if self.args[1].op in OPERATORS:
                str_repn += '(' + str(self.args[1]) + ')'
            else:
                str_repn += str(self.args[1])
            return str_repn


    def __eq__(self, other):
        return isinstance(other, Clause) and self.op == other.op and \
               self.args == other.args


def convert_to_clause(item):
    if isinstance(item, Clause):
        # already a clause
        # happens with cases like negate
        return item

    # something like the precedence of operators is implicit in the order we process the symbols
    # I say 'something like' because implication is checked for first
    # This is because people tend to say P & Q ==> R by which they mean
    # (P & Q) ==> R rather than P & (Q ==> R)
    # For this to work implication has to be checked for first

    # the check for the symbol with the highest precedence comes at the end
    # only then will the nesting take place properly
    # take a moment to wrap your head around this

    # check for implication
    if '=>' in item:
        implication_posn = item.index('=>')
        lhs = item[:implication_posn]
        rhs = item[implication_posn + 1:]
        impl_clause = Clause('=>', [lhs, rhs])
        print impl_clause
        return impl_clause
    elif '&&' in item:
        and_posn = item.index('&&')
        first_conjunct = item[:and_posn]
        second_conjunct = item[and_posn + 1:]
        and_clause = Clause('&&', [first_conjunct, second_conjunct])
        print and_clause
        return and_clause
    # check for not
    elif '~' in item:
        # get the remaining clause and simply not it
        not_posn = item.index('~')
        not_clause = Clause('~', [item[not_posn + 1:]])
        print not_clause
        return not_clause
    elif isinstance(item, str):
        print item
        return Clause(item)
    if len(item) == 1:
        # for statements such as ['P']
        # this also helps get rid of unnecessary parens in statements such as
        # ((P & Q))
        print item
        return convert_to_clause(item[0])
    # for statements such as ['Loves',['Aashish', 'Chocolate']]
    print item
    simple_clause = Clause(item[0], item[1:][0])  # [0] because [1:] produces a [[list]]
    return simple_clause


def is_predicate(clause):
    if clause.op[0] == '~':
        return True
    return clause.op not in OPERATORS and clause.op[0].isupper()


def process_input(fn):
    # global ip_query
    # global KB
    test_kb = KnowledgeBase()
    file_handle = open(fn, "r")
    line_counter = 0
    input_sentences = []

    for line in file_handle:
        if line_counter == 0:
            q = line.strip('\n\r')
            query = pre_parse_facts(q)
            i_query = convert_to_clause(query)

            print i_query
            # if len(query) > 2 then multiple constants functions, several facts
            # if len = 2 then check if for each query[1] is a constant then fact else variable
            line_counter += 1
            continue
        if line_counter == 1:
            fact_count = int(line.strip('\n\r'))
            line_counter += 1
            continue
        if line_counter >= 2:
            # Parse the facts here
            fact = line.strip('\n\r')
            # Pre-process line for easier processing
            fact_list = pre_parse_facts(fact)
            print "Fact List"
            print fact_list
            print "Converting to clause"
            a_clause = convert_to_clause(fact_list)
            # test_kb.tell(a_clause)
            input_sentences.append(a_clause)
            continue
    print "File Parsed Clauses\n\n\n"
    for sen in input_sentences:
        i = 0
        print sen.op
        print sen.args
        # print sen.args[0]
        # print sen.args[1]

        for a in sen.args:
            # t = list(a)
            print i, a
            i += 1

    print "Constructing KB\n\n\n"
    for sen in input_sentences:
        print sen
        test_kb.tell(sen)

    return test_kb, i_query


# to build KB if clause.op == implication add args[1] as key
# construct_KB(input_sentences)
#     a_clause = convert_list_to_clause(sen)
#     KB.append(a_clause)
# print "Final KB\n\n\n"
# for k in KB:
#     print k


def construct_KB(input_sentences):
    global KB
    print "Constructing KB\n\n\n"
    for sen in input_sentences:

        if '=>' in sen:  # if a rule store at items[1]
            implication_pos = sen.index('=>')
            lhs = sen[:implication_pos]
            rhs = sen[implication_pos + 1:]
            if rhs[0] in KB:  # append
                KB[rhs[0]][1].append(lhs)
            else:  # insert the clause
                KB[rhs[0]] = [[], [rhs[1], lhs]]
        else:  # if a fact store at items[0]
            var = sen[1:]
            print var
            if sen[0] in KB:
                for i in var:
                    KB[sen[0]][0].append(i)
            else:
                KB[sen[0]] = [sen[1:], []]

    print "Final KB\n\n\n"
    for k, v in KB.items():
        print k, ': ', v

    print 'Test\n'
    if 'Enemy' in KB:
        items = KB['Enemy']
        print len(items)
        # i = 0 facts; j = Constants
        # i = 1 rules; j = 1, implication parameters; j >= 2 lhs (functions[z]) z parameters of functions

        for i in range(len(items)):
            # if isinstance(i,list):
            for j in range(len(items[i])):
                print len(items[i])
                # check if j is in dict if yes its a function
                # else its a parameter list
                print i, ', ', j
                print items[i][j]
                if 'Peter' in items[i][j]:
                    p = items[i][j].index('Peter')
                    items[i][j][p] = 'p'
                    print 'Success', items[i][j]


def is_variable(var):
    if var.islower():
        return True
    else:
        return False


def is_variable(item):
    # an item is a variable if it is of type Clause, its operator is a string
    # and starts with a small case letter, and has no args

    return isinstance(item, Clause) and item.op.islower() and item.args == []


def unify(x, y, subst = {}):
    if subst is None:
        # failure is denoted by None (default is {})
        return None
    elif x == y:
        # happens if both x and y are operators like '&'
        # or same-name variables, return the most general unifier
        return subst
    # the following two cases are the only cases that can cause a binding
    elif is_variable(x):
        return unify_vars(x, y, subst)
    elif is_variable(y):
        return unify_vars(y, x, subst)
    elif isinstance(x, Clause) and isinstance(y, Clause):
        # to merge two clauses the operands must be the same
        # if they are then unify their arguments
        return unify(x.args, y.args, unify(x.op, y.op, subst))
    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        # this is the case when we're unifying the arguments of a clause
        # see preceding line
        return unify(x[1:], y[1:], unify(x[0], y[0], subst))
    else:
        # does not match any case, so no substitution
        return None


def substitute(theta, clause):
    assert isinstance(clause, Clause)

    if is_variable(clause):
        # check if the variable already has a binding
        if clause in theta:
            return theta[clause]
        else:
            return clause
    else:
        # compound clause with operators such as '&&'
        # check if any of the arguments are bound, and substitute
        return Clause(clause.op, (substitute(theta, arg) for arg in clause.args))


def fol_bc_and(kb, goals, theta):
    if theta is None:
        pass
    elif isinstance(goals, list) and len(goals) == 0:
        # this happens when lhs ==> rhs is [] ==> rhs
        yield theta
    else:
        if goals.op == '&&':
            # operator can only be '&' because the clause is definite (we've broken the nesting)
            first_arg = goals.args[0]
            second_arg = goals.args[1]
            if first_arg.op == '&&':
                # il problemo!
                # fol_bc_or can only prove definite clauses, a conjunction of two literals alone is not one
                # so we strip each second conjunct off, club it with the second arg until the first_arg is a literal
                while not is_predicate(first_arg):
                    second_arg = Clause('&&', [first_arg.args[1], second_arg])
                    first_arg = first_arg.args[0]
        else:
            # clause is a simple clause of kind 'Has(X, Y)'
            # so we need to prove just this i.e. there IS no second clause to prove
            # hence make the second clause [] so it is picked up by fol_bc_and
            first_arg = goals
            second_arg = []
        for theta1 in fol_bc_or(kb, substitute(theta, first_arg), theta):
            # notice that it is substitute(theta, first_arg) that will get a parent and not first_arg
            # second_arg will also get substituted by the theta (i.e. theta1) obtained on running fol_bc_or on the first arg
            # hence it is substitute(thetaONE, second_arg) that will get a parent, not substitute(theta, second_arg) or
            # just second arg
            if isinstance(second_arg, Clause):
                parent_clauses[substitute(theta, goals)] = ([substitute(theta, first_arg), substitute(theta1, second_arg)], 'Rule of conjunction', None)
            # the first argument goes to fol_bc_or because only ONE of the literals
            # in that clause need be proved (and hence the clause becomes true)
            for theta2 in fol_bc_and(kb, second_arg, theta1):
                yield theta2

#______________________________________________________________________________

def fol_bc_or(kb, goal, theta):

    """
    Helper functions that support fol_bc_ask as in AIMA
    """

    possible_rules = kb.fetch_rules_for_goal(goal)
    for rule in possible_rules:
        stdized_rule = standardize_vbls(rule)
        print stdized_rule
        if stdized_rule.op == '=>':
            lhs = stdized_rule.args[0]
            rhs = stdized_rule.args[1]
            # lhs, rhs = convert_to_implication(stdized_rule)
            rhs_unify_try = unify(rhs, goal, theta)
            if rhs_unify_try is not None:
                # some successful unification was obtained
                if lhs != []:
                    # checking for and declaring parent for '&'
                    if lhs.op == '&&':
                        substituted_lhs_args = [substitute(rhs_unify_try, arg) for arg in lhs.args]
                        parent_clauses[substitute(rhs_unify_try, lhs)] = (substituted_lhs_args, 'Rule of conjunction', None)
                    # actually we're supposed to substitute for the rhs
                    # but this will anyway be the goal, so we can go with goal as the child
                    # instead of substitute(rhs, rhs_unify_try)
                    parent_clauses[goal] = ([substitute(rhs_unify_try, rule)], 'Modus Ponens', None)
                    parent_clauses[substitute(rhs_unify_try, rule)] = ([substitute(rhs_unify_try, lhs)], 'Rule of universal instantiation', rule)
            # lhs goes to fol_bc_AND because ALL clauses in the lhs needs to be proved
            for theta1 in fol_bc_and(kb, lhs, rhs_unify_try):
                yield theta1

#______________________________________________________________________________

def fol_bc_ask(kb, query):
    # simple one-liner.
    return fol_bc_or(kb, query, {})


def unify_vars(var, x, subst):
    if var in subst:
        # if binding is already in the dict simply return it
        return unify(subst[var], x, subst)
    # occur check is eliminated
    subst_copy = subst.copy()
    subst_copy[var] = x
    return subst_copy


def pre_parse_facts(fact):
    fact = '(' + fact + ')'
    fact = fact.replace('(', ' ( ')
    fact = fact.replace(')', ' ) ')
    fact = fact.replace(', ', ' ')
    fact_list = fact.split()
    fact_list = parse_facts(fact_list)
    return fact_list


def parse_facts(fact_list):
    first_token = fact_list.pop(0)

    if first_token == '(':
        # start of a new expression
        new_expression = []
        while fact_list[0] != ')':
            # keep appending values to the new expression list
            new_expression.append(parse_facts(fact_list))
        # remove  the ')'
        fact_list.pop(0)
        return new_expression
    else:
        # code is here means token is not the start of a new expression
        return first_token


# def fol_bc_ask(query):
#     global KB
#     q_eval = []
#     if len(query) > 2:  # then multiple constants functions, several facts
#         for i in range(len(query)):
#             fact_eval = fol_bc_or(query[i], query[i + 1], [])
#             i += 2
#             if fact_eval:  # if true evaluate next query
#                 continue
#             else:
#                 return False
#         return True
#     else:  # single atomic query with or with or without variable
#         fact_eval = fol_bc_or(query[0], query[1], [])
#         return fact_eval


# def write_ask(funct, parameters):
#     print 'ASK:',
#     p_len = len(parameters)
#     for i in range(p_len):
#         s = funct + '('
#         if parameters[i].islower():
#             if i < p_len - 1:
#                 s += '_, '
#             else:
#                 s += '_)'
#         else:
#             if i < p_len - 1:
#                 s += parameters[i] + ', '
#             else:
#                 s += parameters[i] + ')'
#     print s


def write_t_f(val, funct, par, subst):
    print val + ':',

    p_len = len(par)
    for i in range(p_len):
        s = funct + '('
        if par[i].islower():
            if i < p_len - 1:
                s += subst[par[i]] + ', '
            else:
                s += subst[par[i]] + ')'
        else:
            if i < p_len - 1:
                s += par[i] + ', '
            else:
                s += par[i] + ')'
    print s


# def fol_bc_or(funct, parameters, parent_funct, subst={}):
#     global KB
#     write_ask(funct, parameters)
#
#     # find all rules such that goal is on the RHS
#     all_facts_rules = KB[funct]
#     facts = all_facts_rules[0]
#     rules = all_facts_rules[1]
#
#     # i = 0 facts; j = Constants
#     # i = 1 rules; j = 1, implication parameters; j >= 2 lhs (functions[z]) z parameters of functions
#
#     if len(facts) > 0:  # direct question
#         for i in range(len(facts)):  # number of facts with same function
#             for j in range(len(facts[i])):  # number of parameters in each fact
#                 if parameters[j].islower:
#                     # subst.append([parameters[j], facts[i][j]])
#                     subst[parameters[j]] = facts[i][j]
#                     # write_t_f('True',funct,facts[i][j])
#                     # print 'True:', funct + '(' + facts[i][j] + ')'
#                     # print true
#                     # propagate to parents
#                 else:
#                     if not parameters[j] == facts[i][j]:
#                         # Print false
#                         return False
#         write_t_f('True', funct, parameters, subst)
#         return True  # and subst
#         pass
#     pass


def find_variables(clause):
    if is_variable(clause):
        return [clause]
    elif is_predicate(clause):
        return clause.args
    elif clause.op == '~':
        return find_variables(clause.args[0])
    else:
        first_arg_vbls = find_variables(clause.args[0])
        second_arg_vbls = find_variables(clause.args[1])
        return first_arg_vbls + second_arg_vbls


x_count = 0

def replace_with_variables(clause, theta = {}):

    """
    Replaces constants in clause with variables and return the substitutions
    that on substitution will yield the statement to prove.
    """

    global x_count

    assert isinstance(clause, Clause)
    if is_predicate(clause):
        # replace arguments of the clause with a variable
        theta_copy = theta.copy()
        new_args = []
        for arg in clause.args:
            if not is_variable(arg):
                new_arg_clause = Clause('x_' + str(x_count))
                theta_copy[new_arg_clause] = arg
                new_args.append(new_arg_clause)
                x_count += 1
        return Clause(clause.op, new_args), theta_copy



def complete_substitute(theta, clause):

    """
    Keeps substituting for variables in clause until there
    are no variables to substitute for or all variables in
    theta have been substituted.
    This is needed for displaying the proof.
    """

    for i in range(0, len(theta.keys())):
        clause = substitute(theta, clause)
    return clause

#______________________________________________________________________________

def print_parent(theta, clause):

    """
    Prints the parents of the clause one by one
    """

    if clause not in parent_clauses:
        # last statement, must have already been given in kb
        print 'We know', complete_substitute(theta, clause), '(given)'
        return
    parents, law_used, clause_used = parent_clauses[clause]
    for parent in parents:
        print_parent(theta, parent)
    print 'which leads to', complete_substitute(theta, clause),
    if clause_used is not None:
        # clause was of the implication form
        print '(' + law_used, 'on', str(clause_used) + ')'
    else:
        print '(' + law_used + ')'

VARIABLE_COUNTER = 0

def standardize_vbls(clause, already_stdized = None):

    """
    Returns the given clause after standardizing the given variables.
    'clause' is an object of type Clause
    'already_stdized' stands for already standardized variables. It is this dict
    that the program will check first to ensure that a (new) binding has already been
    given to the variable. This is needed for statements such as 'F(x) & G(x)' --
    we need them to be standardized as 'F(v_0) & G(v_0)' and not as 'F(v_0) & G(v_1)'
    """

    global VARIABLE_COUNTER

    if already_stdized is None:
        already_stdized = {}

    if not isinstance(clause, Clause):
        return clause

    if is_variable(clause):
        # check if variable has already been standardized
        if clause in already_stdized:
            return already_stdized[clause]
        else:
            new_vbl = Clause('v_' + str(VARIABLE_COUNTER))
            VARIABLE_COUNTER += 1
            # add new binding to the dict
            already_stdized[clause] = new_vbl
            return new_vbl
    else:
        # simply create a new clause mapping the same function to all the args
        return Clause(clause.op, (standardize_vbls(arg, already_stdized) for arg in clause.args))

def main():
    file_name = sys.argv[2]
    i_KB, query_input = process_input(file_name)

    # i_KB = process_input('sample01.txt')
    print "Final KB\n\n\n"
    for k, v in i_KB.clauses.items():
        print k, ': ', v

    query, reqd_theta = replace_with_variables(query_input)

    proof_flag = False

    vbls_in_query = find_variables(query)
    print query
    for answer in i_KB.ask(query):
        # comment the below part out if you're using the program as a query-based system
        if all(reqd_theta[key] == answer[key] for key in reqd_theta.keys()):
            # all keys match
            print '\nProof:\n'
            print_parent(answer, query)
            proof_flag = True
            break
        # uncomment this and run to see all proofs obtained by the query-based system
    ##    print '\nProof:\n'
    ##    print_parent(answer, query)

    if not proof_flag:
        print '\nSorry, your statement could not be proved.\n'
    else:
        print ''



        # process_input('sample01.txt')


if __name__ == '__main__':
    main()
