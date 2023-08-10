#!/usr/bin/env python3

import sys
import doctest

sys.setrecursionlimit(10_000)

### HELPER FUNCTIONS ###
 
## Board Helper functions ##
def get_cell(board, r, c):
    """
    Given a board and r,c indices, return the val at the position in the board.
    >>> board = [
    ...         [1,2,3,4],
    ...         [5,6,7,8],
    ...         [9,10,11,12],
    ...         [13,14,15,16]
    ...         ]
    >>> [get_cell(board, r,c) for r in range(0,3) for c in range(0,3) ]
    [1, 2, 3, 5, 6, 7, 9, 10, 11]
    """
    
    assert 0 <= r < len(board) and 0 <= c < len(board[0])
    val = board[r][c] 
    return val

def get_row(board, r):
    """"
    >>> board = [
    ...         [1,2,3,4],
    ...         [5,6,7,8],
    ...         [9,10,11,12],
    ...         [13,14,15,16]
    ...         ]
    >>> [get_row(board, r) for r in range(0,2)]
    [[1, 2, 3, 4], [5, 6, 7, 8]]
    """
    return [num for num in board[r] if num != 0]

def get_column(board, c):
    """
    >>> board = [
    ...         [1,2,3,4],
    ...         [5,6,7,8],
    ...         [9,10,11,12],
    ...         [13,14,15,16]
    ...         ]
    >>> [get_column(board, c) for c in range(1,3)]
    [[2, 6, 10, 14], [3, 7, 11, 15]]
    """
    return [row[c] for row in board if row[c] != 0]


def convert_to_sub_grid(n, r, c):
    """
    Given a cell's coordinates, return the equivalent coordinates of the cell's subgrid.
    """

    sqrt_n = int(n**(1/2))
    sr, sc = int(r/sqrt_n), int(c/sqrt_n)
    return (sr,sc)


def get_sub_grid(board, sr, sc):
    """"
    Given a board and a subgrids's coordinates, return all non-empty values in the sub-grid
    >>> board = [
    ...         [0,2,3,4],
    ...         [5,6,7,8],
    ...         [9,10,11,12],
    ...         [13,14,15,16]
    ...         ]
    >>> [get_sub_grid(board, r,c) for r in range(2) for c in range(2)]
    [[2, 5, 6], [3, 4, 7, 8], [9, 10, 13, 14], [11, 12, 15, 16]]
    """
    sqrt_n = int(len(board)**(1/2))
    sub_rows, sub_columns = range(sr*sqrt_n, (sr+1)*sqrt_n), range(sc*sqrt_n, (sc+1)*sqrt_n)
    return [board[r][c] for r in sub_rows for c in sub_columns if get_cell(board, r,c)]


def sub_grid_empty(board, sr, sc):
    """"
    Given a board and a cell.
    Returns the the a tuple of the row and column index of other empty cells in the same grid as the given cell
    """
    n = len(board)
    sqrt_n = int(n**(1/2))
    sub_rows, sub_columns = range(sr*sqrt_n, (sr+1)*sqrt_n), range(sc*sqrt_n, (sc+1)*sqrt_n)
    return [(new_r, new_c) for new_r in sub_rows for new_c in sub_columns if not get_cell(board, new_r, new_c)]

def all_possible_pairs_rule(array, val, pair_bool):
    """
    Given a list of all empty cells, a value and a default boolean True/False
    Returns a rule where each clause is a pair of all possible pairing of the empty cells with given val set to default boolean
    """
    result = []
    for i, main in enumerate(array):
        sample_space = array[i+1:]
        for other in sample_space:
            result.append([((main, val), pair_bool), ((other, val), pair_bool)])
    return result



# # Rules Helper Functions # #

def taboo_vals_rule(board, cell):
    """
    Given a board an cell coordinates tuple. Returns a list of clauses specifying rules of what numbers should not be there.
    The return rule is a list of clauses where each clause is of the form  [((cell, num), False)].
    the rules imply that  a the given cell must not be assigned the given num
    >>> board = [
    ...         [1,0,3,2],
    ...         [3,2,1,4],
    ...         [4,1,2,0],
    ...         [2,3,4,0],
    ...         ]
    >>> taboo_vals_rule(board, (0,1))
    [[(((0, 1), 1), False)], [(((0, 1), 2), False)], [(((0, 1), 3), False)]]
    >>> taboo_vals_rule(board, (3,3))
    [[(((3, 3), 2), False)], [(((3, 3), 3), False)], [(((3, 3), 4), False)]]

    """

    r,c = cell
    n = len(board)
    sr, sc = convert_to_sub_grid(n, r, c)
    #row #column #subgrid
    all_vals = get_row(board, r) + get_column(board, c) + get_sub_grid(board, sr, sc)

    ## --> union of all sets must all be false
    all_vals = set(all_vals)
    return [[((cell, val), False)] for val in all_vals]
    
def cell_must_be_filled_rule(board, cell):
    """
    Give a baord and empty cell coordinates. Returns a rule that at least one of the allowed numbers must be assinged to the cell.
    The Returned rule is a list of one clause where the clause is in the form [((cell, val1)), ((cell, val2)), ...]
    The clause is true is there exists at least one literal --> ((cell, valx), True).
    >>> board = [
    ...         [1,0,3,2],
    ...         [3,2,1,4],
    ...         [4,1,2,0],
    ...         [2,3,4,0],
    ...         ]
    >>> cell_must_be_filled_rule(board, (0,1))
    [[(((0, 1), 4), True), (((0, 1), 5), True), (((0, 1), 6), True), (((0, 1), 7), True), (((0, 1), 8), True), (((0, 1), 9), True)]]
    >>> cell_must_be_filled_rule(board, (3,3))
    [[(((3, 3), 1), True), (((3, 3), 5), True), (((3, 3), 6), True), (((3, 3), 7), True), (((3, 3), 8), True), (((3, 3), 9), True)]]
    """
    r, c = cell
    n = len(board)
    sr, sc = convert_to_sub_grid(n, r, c)

    #allowed vals from row#allowed vals from column#allowed vals from grid
    taboo_vals = set(get_row(board, r) + get_column(board, c) + get_sub_grid(board, sr, sc))
    allowed_cell_vals = [num for num in range(1,n+1) if num not in taboo_vals]

    # at least one allowed_value must be true
    return [[((cell, val), True) for val in allowed_cell_vals]]

def fill_cell_at_most_once(board, cell):
    """
    Given a board and a cell coordinates. Returns rules such that for each empty cell is filled with at most one valid value.
    The rule is set up such that if any two different valid values are assinged to the same cell, the whole formula is false.
    >>> board = [
    ...         [0,7,5,9],
    ...         [3,6,1,8],
    ...         [4,1,6,0],
    ...         [2,3,4,0],
    ...         ]
    >>> fill_cell_at_most_once(board, (0,0))   
    [[(((0, 0), 1), False), (((0, 0), 8), False)]]
    """ 
    n = len(board)
    r,c = cell
    sr, sc = convert_to_sub_grid(n, r, c)
    ## intersection of allowed vals from row, column, and subgrid
    taboo_vals = set(get_row(board, r) + get_column(board, c) + get_sub_grid(board, sr, sc))
    valid_cell_vals = [num for num in range(1,n+1) if num not in taboo_vals]
    # no possible pair of all allowed values can both be true, but they can both be false.
    result = []

    for i, main_val in enumerate(valid_cell_vals):
        sample_space = valid_cell_vals[i+1:]
        for other_val in sample_space:
            result.append([((cell, main_val), False), ((cell, other_val), False)])
    return result

def no_row_duplicates_rules(board, r):
    """
    Given a board and row index. Return a rule such that each allowed number is assigned to at most one empty cell.
    The returned rule is a list of clauses where each clause is of the form [((cell_1, val_i), False),((cell_2, val_i))].
    For all valid values to be assinged, there is such a clause for every possible pair of empty cells.
    Any clause in the above rule is False if the same value is assinged to more than one cell in the same column and True otherwise.
    >>> board = [
    ...         [0,0,3,2],
    ...         [3,2,1,4],
    ...         [4,1,2,0],
    ...         [2,3,4,0],
    ...         ]

    >>> no_row_duplicates_rules(board, 0)
    [[(((0, 0), 1), False), (((0, 1), 1), False)], [(((0, 0), 4), False), (((0, 1), 4), False)], [(((0, 0), 5), False), (((0, 1), 5), False)], [(((0, 0), 6), False), (((0, 1), 6), False)], [(((0, 0), 7), False), (((0, 1), 7), False)], [(((0, 0), 8), False), (((0, 1), 8), False)], [(((0, 0), 9), False), (((0, 1), 9), False)]]
    >>> no_row_duplicates_rules(board, 1)
    []
    """
    n = len(board)
    # all empty cells in same row
    all_empty_in_row = [(r, other_c) for other_c in range(n) if not get_cell(board, r, other_c)]
    # all allowed values from row
    valid_row_vals = [num for num in range(1,n+1) if num not in set(get_row(board, r))]
    ## for all allowed values no num can be true for any possible pair of the empty cells
    
    result = []
    for val in valid_row_vals:
        result.extend(all_possible_pairs_rule(all_empty_in_row, val, False))
    return result

def no_column_duplicates_rules(board, c):
    """
    Given a board and column index. Returns the rule such that each allowed number to is assinged to at most one empty cell in the column. 
    The return rule is a list of lists where each list is a clause of in the form [((cell1, val), False), ((cell2, val), False)]
    There is such a close for every possible pair of empty cells in the column for all allowed numbers in the column. 
    Each clause is True if at most one literal is True and False otherwise. 
    >>> board = [
    ...         [0,0,3,2],
    ...         [3,2,1,4],
    ...         [4,1,2,0],
    ...         [2,3,4,0],
    ...         ]
    >>> [no_column_duplicates_rules(board, c) for c in [0,1,2]]
    [[], [], []]
    >>> no_column_duplicates_rules(board, 3)
    [[(((2, 3), 1), False), (((3, 3), 1), False)], [(((2, 3), 3), False), (((3, 3), 3), False)], [(((2, 3), 5), False), (((3, 3), 5), False)], [(((2, 3), 6), False), (((3, 3), 6), False)], [(((2, 3), 7), False), (((3, 3), 7), False)], [(((2, 3), 8), False), (((3, 3), 8), False)], [(((2, 3), 9), False), (((3, 3), 9), False)]]
    """
    n = len(board)
    #all empty cells in same column
    all_empty_in_column = [(other_r, c) for other_r in range(n) if not get_cell(board, other_r, c)]
    #all allowed values from column
    valid_column_vals = [num for num in range(1,n+1) if num not in set(get_column(board, c))]

    # for all allowed values no value x be true in any possible pair of all the empty cells.
    result  = []
    for val in valid_column_vals:
        result.extend(all_possible_pairs_rule(all_empty_in_column, val, False))
    return result

def no_grid_duplicates_rules(board, sr, sc):
    """
    Given a board and its subgrid's coordinates. Returns a rule such that for all allowed values in the grid.
    Each number is assinged to at most one empty cell in the same grid. If any allowed number is assigned to more than one cell.
    At least one clause should become False >>> whole formula False.
    >>> board = [
    ...         [0,0,3,2],
    ...         [3,2,1,4],
    ...         [4,1,2,0],
    ...         [2,3,4,0],
    ...         ]
    >>> no_grid_duplicates_rules(board, *(1,1))
    [[(((2, 3), 1), False), (((3, 3), 1), False)], [(((2, 3), 3), False), (((3, 3), 3), False)], [(((2, 3), 5), False), (((3, 3), 5), False)], [(((2, 3), 6), False), (((3, 3), 6), False)], [(((2, 3), 7), False), (((3, 3), 7), False)], [(((2, 3), 8), False), (((3, 3), 8), False)], [(((2, 3), 9), False), (((3, 3), 9), False)]]
    >>> [no_grid_duplicates_rules(board, *cell) for cell in [(0,1), (1,0)]]
    [[], []]
    """
    n = len(board)
    # all empty cells in same subgrid.
    all_empty_in_grid = sub_grid_empty(board, sr,sc)
    # all alowed vals from same grid
    valid_subgrid_vals = [num for num in range(1, 10) if num not in set(get_sub_grid(board, sr,sc))]
    # for all allowed values, no val x can be true in both cells for any possible pair of all empty cells

    result = []
    for val in valid_subgrid_vals:
        result.extend(all_possible_pairs_rule(all_empty_in_grid, val, False))
    return result

def get_empty_cell_rules(board, cell):
    """
    Given a board and a cell return a general rule of all clauses that an empty cell alone must satisfy.
    It cannot be filled with some taboo values, it must be filled with at least once value and it must fille with at most one value at a time
    """
    return taboo_vals_rule(board, cell) + cell_must_be_filled_rule(board, cell) + fill_cell_at_most_once(board, cell)

def get_filled_cell_rules(val, cell):
    """
    Given a val and its corresponding cell. Return a rule specifying that that cell must contain only that value.
    The return rule is a list of one clause, where the clause is of the form [((cell, val), True)]. 
    """
    return [[((cell, val), True)]]

def reduce_clause(default_literal, clause):
    """ Given a clause and logical literal, return the simplified logical equivalence of the union of clause's literals"""
    for literal in clause:
        # if literal in clause is equivalent to default literal --> the clause is always true
        if literal == default_literal:
            # what is later on we find the same literal with opposite val
            return []
        # if literal in clause if not equivalent to default literal --> clause is true if any of the other variables are true
        if literal[0] == default_literal[0] and literal[1] != default_literal[1] and len(clause) > 1:
            # return [new_literal for new_literal in clause if new_literal != (default_literal[0], not default_literal[1])]
            return [new_literal for new_literal in clause if new_literal[0] != default_literal[0]]
    # if clause doesn't contain default literal --> clause is irreducible.
    return clause

def reduce_formula(default_literal, formula):
    """
    Given a forumla and a literal, reduces every clause such that if the literal is equiv to the same bool in clause, other clauses are considered.
    if not equivalent, clause should contain other literals to be evaluated.
    >>> formula = [
    ...    [('a', True), ('b', True), ('c', True)],
    ...    [('a', False), ('f', True)],
    ...    [('d', False), ('e', True), ('a', True), ('g', True)],
    ...    [('h', False), ('c', True), ('a', False), ('f', True)],
    ...   ]
    """
    new_formula = []
    for clause in formula:
        new_clause = reduce_clause(default_literal,clause)
        if new_clause:
            new_formula.append(new_clause)
    return new_formula




# # # MAIN # # #

def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    """
    n = len(sudoku_board)
    
    def get_rules_for_all_rows(n):
        """returns the rules for each all rows in board such that in a board, each valid number is assigned to at most one empty cell"""
        rules = []
        for r in range(n):
            rules.extend(no_row_duplicates_rules(sudoku_board,r))
        return rules

    def get_rules_for_all_columns(n):
        """returns rules for all columns such that in each column each valid number in assinged to at most one empty cell"""
        rules = []
        for c in range(n):
            rules.extend(no_column_duplicates_rules(sudoku_board, c))
        return rules
    
    def get_rules_for_all_sub_grids(n):
        """returns rules for all grids such that in each sub grid, each valid number is assigned to at most one empty cell"""
        sqrt_n = int(n**(1/2))
        rules = []
        
        for sr in range(sqrt_n):
            for sc in range(sqrt_n):
                rules.extend(no_grid_duplicates_rules(sudoku_board, sr, sc))
        return rules

    def get_all_cell_rules(n):
        """returns rules for every cell such that existing cells must maintain their values.
            Empty cells must be filled with at least one value, filled with at most one value, 
            and must not be filled up with recurring row,column,grid values"""
        all_existing_cell_rules = []
        all_empty_cell_rules = []

        for r in range(n):
            for c in range(n):
                #if cell is already filled
                if get_cell(sudoku_board, r, c):
                    all_existing_cell_rules.extend(get_filled_cell_rules(get_cell(sudoku_board,r,c), (r, c)))  
                else: #if cell is empty
                    all_empty_cell_rules.extend(get_empty_cell_rules(sudoku_board, (r,c)))
        return all_existing_cell_rules + all_empty_cell_rules
 

    all_cell_rules = get_all_cell_rules(n)
    all_rows_rules = get_rules_for_all_rows(n)
    all_columns_rules = get_rules_for_all_columns(n)
    all_sub_grids_rules = get_rules_for_all_sub_grids(n)

    ans = all_cell_rules + all_columns_rules + all_rows_rules + all_sub_grids_rules
    return ans 


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    """
    
    # base case : return an empty dictionary to populate with assignments as we backtrack
    if not formula: 
        return {}
    else:
        #loop through every clause to find length_1 clause and recurse on other variables and rules using the lenght-1 clause existing literal value.
        for i, clause in enumerate(formula):
            if len(clause) == 1:
                #the length 1 clause literal variable is fixed to its value in the literal. Reduce formula and recurse on the rest of the varibles.
                fixed_var, fixed_bool = clause[0]
                reduced_formula = reduce_formula((fixed_var, fixed_bool), formula)
                result = satisfying_assignment(reduced_formula)
                
                #if solution is found, return the result.
                if result != None:
                    #if solution is found but would contradict with already fixed variable, then no solution is possible.
                    if result.get(fixed_var, fixed_bool) != fixed_bool: return None
                    #otherwise use current assignment
                    result[fixed_var] = fixed_bool
                    return result
                return None

        #if no length-1 clause exists, choose any var  and fix and recurse on its two possible values i.e both True  and False.
        #return whichever gives a solution. #note that formula is not mutated at this point.
        #path 1
        fixed_var, fixed_bool = formula[0][0]
        with_fixed_bool = reduce_formula((fixed_var, fixed_bool), formula)
        result = satisfying_assignment(with_fixed_bool)
        if result != None:
            if result.get(fixed_var,fixed_bool) != fixed_bool: return None
            result[fixed_var] = fixed_bool
            return result
        

        #Path 2
        with_not_fixed_bool = reduce_formula((fixed_var, not fixed_bool), formula)
        result = satisfying_assignment(with_not_fixed_bool)           
        if result != None:
            if result.get(fixed_var, not fixed_bool) == fixed_bool: return None
            result[fixed_var] = not fixed_bool
            return result
        #if neither paths returns solution then no solution really exists. 
    return None


def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolveable board, return None
    instead.
    """

    if not assignments:
        return None
    
    new_board = [[0]*n for _ in range(n)]
    tot = int(n*n) #counter for all keys with value True i.e (cell,val) : True -> board[cell] = val

    for var in assignments:
        if not assignments[var]: continue
        new_board[var[0][0]][var[0][1]] = var[1]
        tot -= 1
    
    return new_board if tot == 0 else None #the board is valid iff all cells are filled.


if __name__ == "__main__":
    import doctest
    if False:
        _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
        doctest.testmod(optionflags=_doctest_flags)
    if False:
        test_board = [[1,0,3,4],[2,3,0,0],[3,4,1,0],[0,1,2,3]]
        test_formula = sudoku_board_to_sat_formula(test_board)

        for clause in test_formula:
            print(clause)


