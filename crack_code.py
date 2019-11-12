def exclude_number_from_place(possibilities, digit, place):
    possibilities[place].remove(digit)


def exclude_number(possibilities, digit):
    for place in range(len(possibilities)):
        exclude_number_from_place(possibilities, digit, place)


def exclude_digits_from_rows_where_nothing_is_right(possibilities, constraints):
    for row in constraints:
        if row['valid_on_invalid_places'] == 0 and row['valid_and_placed'] == 0:
            for digit in row['digits']:
                exclude_number(possibilities, digit)


def exclude_digits_existing_with_place_contradiction(possibilities, constraints):
    for index1 in range(len(constraints)):
        for index2 in range(len(constraints)):
            if index1 == index2:
                continue
            if constraints[index1]['valid_on_invalid_places'] > 0 and constraints[index1]['valid_and_placed'] == 0 and \
                    constraints[index2]['valid_on_invalid_places'] == 0 and constraints[index2]['valid_and_placed'] > 0:
                for index in range(len(constraints[index1]['digits'])):
                    if constraints[index1]['digits'][index] == constraints[index2]['digits'][index]:
                        exclude_number(possibilities, constraints[index1]['digits'][index])


def is_possible_combination(combination, constraint):
    valid_and_placed = 0
    valid_on_invalid_places = 0
    for index in range(len(combination)):
        if constraint['digits'][index] == combination[index]:
            valid_and_placed += 1
        elif constraint['digits'][index] in combination:
            valid_on_invalid_places += 1

    return constraint['valid_and_placed'] == valid_and_placed and constraint['valid_on_invalid_places'] == valid_on_invalid_places


def bruteforace_place(possibilities, constraints, partial_combination):
    if len(partial_combination) == len(constraints[0]['digits']):
        # Combination is full
        combination = partial_combination
        is_found = True
        for constraint in constraints:
            if not is_possible_combination(combination, constraint):
                is_found = False
                break

        return combination if is_found else None
    else:
        # Combination is partial
        place = len(partial_combination)
        for digit in possibilities[place]:
            combination = bruteforace_place(possibilities, constraints, partial_combination + [digit])
            if combination is not None:
                return combination

        return None


def crack_code(constraints):
    possibilities = []
    for place in range(len(constraints[0]['digits'])):
        possibilities.append([0,1,2,3,4,5,6,7,8,9])

    exclude_digits_from_rows_where_nothing_is_right(possibilities, constraints)

    exclude_digits_existing_with_place_contradiction(possibilities, constraints)

    return bruteforace_place(possibilities, constraints, [])

result = crack_code([
    {'digits': [6,8,2], 'valid_and_placed': 1, 'valid_on_invalid_places': 0},
    {'digits': [6,1,4], 'valid_and_placed': 0, 'valid_on_invalid_places': 1},
    {'digits': [2,0,6], 'valid_and_placed': 0, 'valid_on_invalid_places': 2},
    {'digits': [7,3,8], 'valid_and_placed': 0, 'valid_on_invalid_places': 0},
    {'digits': [8,7,0], 'valid_and_placed': 0, 'valid_on_invalid_places': 1}
])
print(result)