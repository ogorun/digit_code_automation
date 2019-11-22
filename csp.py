from collections import namedtuple
import queue

# function BACKTRACKING-SEARCH(csp) returns a solution, or failure
#    return RECURSIVE-BACKTRACKING({ }, csp)
# function RECURSIVE-BACKTRACKING(assignment, csp) returns a solution, or failure
#   if assignment is complete then return assignment
#   var ← SELECT-UNASSIGNED-VARIABLE(VARIABLES[csp], assignment, csp)
#   for each value in ORDER-DOMAIN-VALUES(var , assignment, csp) do
#     if value is consistent with assignment according to CONSTRAINTS[csp] then
#        add {var = value} to assignment
#        result ← RECURSIVE-BACKTRACKING(assignment, csp)
#        if result != failure then return result
#        remove {var = value} from assignment
#     return failure

CSP = namedtuple('CSP', 'constraints variables domains')


def is_constraint_satisfied(constraint, assignment, vars_num):
    valid_and_placed = 0
    valid_on_invalid_places = 0
    for index in range(len(assignment)):
        if constraint['digits'][index] == assignment[index]:
            valid_and_placed += 1
        elif constraint['digits'][index] in assignment.values():
            valid_on_invalid_places += 1

    if len(assignment) == vars_num:
        return constraint['valid_and_placed'] == valid_and_placed and constraint['valid_on_invalid_places'] == valid_on_invalid_places
    else:
        return constraint['valid_and_placed'] >= valid_and_placed and constraint['valid_on_invalid_places'] >= valid_on_invalid_places


def is_conflict(csp: CSP, assignment):
    for constraint in csp.constraints:
        if not is_constraint_satisfied(constraint, assignment, len(csp.variables)):
            return True

    return False


def first_unassigned_var(csp, assignment):
    assigned_vars = list(assignment.keys())
    for var in csp.variables:
        if var not in assigned_vars:
            return var


def ordered_domain_vals(csp, assignment, var):
    return csp.domains[var]


def print_assignment(assignment):
    return
    if assignment is None:
        print(None)
    else:
        out = ', '.join([str(assignment.get(i, ' ')) for i in range(len(assignment))])
        print(out)


def backtrace_search(csp: CSP, assignment, get_next_var = first_unassigned_var, possible_vals = ordered_domain_vals):
    print_assignment(assignment)
    if is_conflict(csp, assignment):
        return None
    else:
        if len(assignment) == len(csp.variables):
            return assignment
        else:
            var = get_next_var(csp, assignment)
            for val in possible_vals(csp, assignment, var):
                assignment[var] = val
                result = backtrace_search(csp, assignment)
                if result is not None:
                    return assignment
            del assignment[var]



# function AC-3(csp) returns the CSP, possibly with reduced domains
#    inputs: csp, a binary CSP with variables {X1, X2, . . . , Xn}
#    local variables: queue, a queue of arcs, initially all the arcs in csp
#
#    while queue is not empty do
#      (Xi, Xj ) ← REMOVE-FIRST(queue)
#      if REMOVE-INCONSISTENT-VALUES(Xi, Xj ) then
#        for each Xk in NEIGHBORS[Xi] do
#           add (Xk, Xi) to queue
#
# function REMOVE-INCONSISTENT-VALUES(Xi , Xj ) returns true iff we remove a value
#    removed ←false
#    for each x in DOMAIN[Xi] do
#        if no value y in DOMAIN[Xj ] allows (x ,y) to satisfy the constraint between Xi and Xj
#        then delete x from DOMAIN[Xi]; removed ←true
#    return removed


def ac3(csp: CSP):
    q = queue.Queue()


if __name__ == '__main__':
    csp = CSP([
        {'digits': [6,8,2], 'valid_and_placed': 1, 'valid_on_invalid_places': 0},
        {'digits': [6,1,4], 'valid_and_placed': 0, 'valid_on_invalid_places': 1},
        {'digits': [2,0,6], 'valid_and_placed': 0, 'valid_on_invalid_places': 2},
        {'digits': [7,3,8], 'valid_and_placed': 0, 'valid_on_invalid_places': 0},
        {'digits': [8,7,0], 'valid_and_placed': 0, 'valid_on_invalid_places': 1}
    ], [0, 1, 2], {
        0: [0,1,2,3,4,5,6,7,8,9],
        1: [0,1,2,3,4,5,6,7,8,9],
        2: [0,1,2,3,4,5,6,7,8,9]
    })

    result = backtrace_search(csp, {})
    print('----------')
    print_assignment(result)