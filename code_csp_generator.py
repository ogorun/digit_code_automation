import random, json, glob
from csp import CSP, backtrace_search, print_assignment, is_conflict
from sentence_parsing import constraint2sentence
from test_detection_and_recognition import constraint2image


def n_digits(n):
    return [random.randint(0,9) for i in range(n)]


def generate_constraint(code):
    digits_num = len(code)
    constraint_digits = n_digits(digits_num)
    valid_and_placed = 0
    valid_on_invalid_places = 0
    for index in range(digits_num):
        if constraint_digits[index] == code[index]:
            valid_and_placed += 1
        elif constraint_digits[index] in code:
            valid_on_invalid_places += 1

    return  {'digits': constraint_digits, 'valid_and_placed': valid_and_placed, 'valid_on_invalid_places': valid_on_invalid_places}


def generate_code_csp(code = None, constraints = None):
    if code is None:
        code = n_digits(random.randint(3, 4))

    if constraints is None:
        constraints_num = random.randint(4, 6)
        constraints = [generate_constraint(code) for i in range(constraints_num)]

    digits_num = len(code)
    domains = {i: list(range(10)) for i in range(digits_num)}
    return CSP(constraints, list(range(digits_num)), domains), code


def generate_image(constraints):
    a = 1

if __name__ == '__main__':
    to_generate = True

    if to_generate:
        for i in range(10):
            csp, code = generate_code_csp()
            print(code, csp)

            right_assignment = {index: digit for index, digit in enumerate(code)}
            assert not is_conflict(csp, right_assignment)

            # generate sentences
            for constraint in csp.constraints:
                constraint['sentence'] = constraint2sentence(constraint)
                print(constraint)

            file_base_name = ''.join([str(digit) for digit in code])
            image_file = constraint2image(csp.constraints, file_base_name)
            result = backtrace_search(csp, {})
            print('----------')
            print(code)
            print_assignment(result)
            with open(f"generated/{file_base_name}.json", 'w') as fh:
                json.dump({"code":code, "constraints": csp.constraints, "image": image_file, "result": result}, fh)



    else:
        for filepath in glob.glob('generated/*.json'):
            problem = json.load(open(filepath))
            print(problem)
            csp, code = generate_code_csp(problem['code'], problem['constraints'])
            result = backtrace_search(csp, {})
            print(result)