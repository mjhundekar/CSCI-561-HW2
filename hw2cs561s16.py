import sys
OPERATORS = ['&&', '~', '=>']

KB =[]

class Clause:
    def __init__(self, op, args=[], parents = None):

        self.op = op
        self.parents = parents
        self.args = map(convert_list_to_clause, args)

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
            # binary operator like '&&' or '=>'
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


def convert_list_to_clause(item):
    print "Converting to Clause::\n"
    print item
    print '\n'
    # check for implication
    if '=>' in item:
        implication_pos = item.index('=>')
        lhs = item[:implication_pos]
        rhs = item[implication_pos + 1:]
        impl_clause = Clause('=>', [lhs, rhs])
        print impl_clause
        return impl_clause
    # check for and
    elif '&&' in item:
        and_count = item.count('&&')
        if and_count == 1:
            and_pos = item.index('&&')
            first_conjunct = item[:and_pos]
            second_conjunct = item[and_pos + 1:]
            and_clause = Clause('&&', [first_conjunct, second_conjunct])
        else:
            all_conjuncts = []
            for i in range(and_count):
                and_pos = item.index('&&')
                conjunct = item[:and_pos]
                all_conjuncts.append(conjunct)
                item = item[and_pos + 1:]
            and_clause = Clause('&&', all_conjuncts)
        print and_clause
        return and_clause
    # check for not
    elif '~' in item:
        # get the remaining clause and simply not it
        not_posn = item.index('~')
        not_clause = Clause('~', [item[not_posn + 1:]])
        return not_clause
    elif isinstance(item, str):
        print item
        return Clause(item)

    # for statements such as ['Function',['J', 'M']]
    simple_clause = Clause(item[0], item[1:][0])  # [0] because [1:] produces a [[list]]
    print simple_clause
    return simple_clause


def process_input(fn):
    file_handle = open(fn, "r")
    line_counter = 0
    input_sentences = []

    for line in file_handle:
        if line_counter == 0:
            query = line.strip('\n\r')
            line_counter += 1
            continue
        if line_counter ==1:
            fact_count = int(line.strip('\n\r'))
            line_counter +=1
            continue
        if line_counter >= 2:
            # Parse the facts here
            fact = line.strip('\n\r')
            # Pre-process line for easier processing
            fact = '(' + fact + ')'
            fact = fact.replace('(', ' ( ')
            fact = fact.replace(')', ' ) ')
            fact = fact.replace(', ', ' ')
            fact_list = fact.split()
            sen = parse_facts(fact_list)
            print str(sen)
            input_sentences.append(sen)
            continue
    print "File Parsed\n\n\n"
    for sen in input_sentences:
        # print sen
        a_clause = convert_list_to_clause(sen)
        KB.append(a_clause)
    print "Final KB\n\n\n"
    for k in KB:
        print k


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


def main():
    # file_name = sys.argv[2]
    # process_input(file_name)

    process_input('sample01.txt')


if __name__ == '__main__':
    main()
