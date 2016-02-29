import sys
import collections

OPERATORS = ['&&', '~', '=>']

KB = collections.OrderedDict()

query = []

def process_input(fn):
    file_handle = open(fn, "r")
    line_counter = 0
    input_sentences = []

    for line in file_handle:
        if line_counter == 0:
            q = line.strip('\n\r')
            query = pre_parse_facts(q)
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
            fact_list = pre_parse_facts(fact)
            print fact_list
            input_sentences.append(fact_list)
            continue
    print "File Parsed\n\n\n"
    for sen in input_sentences:
        print sen

    construct_KB(input_sentences)
    #     a_clause = convert_list_to_clause(sen)
    #     KB.append(a_clause)
    # print "Final KB\n\n\n"
    # for k in KB:
    #     print k


def construct_KB(input_sentences):
    print "Constructing KB\n\n\n"
    for sen in input_sentences:
        if '=>' in sen:
            implication_pos = sen.index('=>')
            lhs = sen[:implication_pos]
            rhs = sen[implication_pos + 1:]
            KB[rhs[0]] = [rhs[1], lhs]
        else:
            var = sen[1:]
            print var
            KB[sen[0]] = sen[1:]

    print "Final KB\n\n\n"
    for k, v in KB.items():
        print k, ': ', v

    print 'Test\n'
    if 'Traitor' in KB:
        items = KB['Traitor']
        print len(items)
        # if len is 2 then implication
        # else it is a fact
        for i in range(len(items)):
            # if isinstance(i,list):
            for j in range(len(items[i])):
                # check if j is in dict if yes its a function
                # else its a parameter list
                print i, ', ', j
                print items[i][j]
                if 'z' in items[i][j]:
                    p = items[i][j].index('z')
                    items[i][j][p] = 'p'
                    print 'Success', items[i][j]





def pre_parse_facts(fact):
    fact = '(' + fact + ')'
    fact = fact.replace('(', ' ( ')
    fact = fact.replace(')', ' ) ')
    fact = fact.replace(',', ', ')
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


def main():
    file_name = sys.argv[2]
    process_input(file_name)

    # process_input('sample01.txt')


if __name__ == '__main__':
    main()
