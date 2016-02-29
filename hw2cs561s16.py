import sys
OPERATORS = ['&&', '~', '=>']

KB =[]


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
            fact = fact.replace(',', ', ')
            fact_list = fact.split()
            fact_list = parse_facts(fact_list)
            print fact_list
            input_sentences.append(fact_list)
            continue
    print "File Parsed\n\n\n"
    # for sen in input_sentences:
        # print sen
    #     a_clause = convert_list_to_clause(sen)
    #     KB.append(a_clause)
    # print "Final KB\n\n\n"
    # for k in KB:
    #     print k


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
