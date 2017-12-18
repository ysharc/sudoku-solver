"""
    A sudoku solver agent
"""

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        ASSIGNMENTS.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins in every unit
    for unit in UNIT_LIST:
        all_unit_values = [values[box] for box in unit]
        nt_filter = lambda value, auv=all_unit_values: (True if (len(value) == 2 and
                                                                 auv.count(value) == 2)
                                                        else False)
        all_naked_twins = set(filter(nt_filter, all_unit_values))
        # Eliminate the naked twins as possibilities for their peers
        digits_to_remove = "".join(naked_twin for naked_twin in all_naked_twins)
        for box in unit:
            if values[box] not in all_naked_twins:
                for digit in digits_to_remove:
                    values = assign_value(values, box, values[box].replace(digit, ""))
    return values

def cross(row_names, col_names):
    "Cross product of elements in row_names and elements in col_names."
    return [row + col for row in row_names for col in col_names]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'.
                    If the box has no value, then the value will be '123456789'.
    """
    return {box: possibility if possibility != "." else "123456789"
            for box, possibility in zip(cross("ABCDEFGHI", "123456789"), grid)}

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    if not values:
        print("Not solvable")
        return
    max_widths = {col: len(max([values[row + col] for row in "ABCDEFGHI"], key=len))
                  for col in "123456789"}
    row_dic = {0: "A", 1: "B", 2: "C", 4: "D", 5: "E", 6: "F", 8: "G", 9: "H", 10: "I"}
    for i in range(11):
        if i not in row_dic:
            line = "-"
            for cols in ["123", "456", "789"]:
                for col in cols:
                    line += "-" * (max_widths[col] + 1)
                line += "+-"
        else:
            line = " "
            row = row_dic[i]
            for cols in ["123", "456", "789"]:
                for col in cols:
                    max_width = max_widths[col]
                    padding = max_width - len(values[row+col])
                    front_padding = " " * int(padding/2)
                    back_padding = " " * (padding - int(padding/2))
                    line += front_padding + values[row + col] + back_padding + " "
                line += "| "
        print(line)

def eliminate(values):
    """
    Eliminate values from peers of a box with single value
    Args:
        values(dict): Sudoku in dictionary form
    Returns:
        The Sudoku after eliminating the values
    """
    single_values = [box for box in BOXES if len(values[box]) == 1]
    for box in single_values:
        for peer in PEERS[box]:
            values = assign_value(values, peer, values[peer].replace(values[box], ""))
    return values

def only_choice(values):
    """
    Assign the only choice possible in a box for any of the units
    Args:
        values(dict): Sudoku in dictionary form
    Returns:
        The Sudoku with the updated values
    """
    for unit in UNIT_LIST:
        for digit in "123456789":
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate and only choice until one of the following conditions is met
        i) Sudoku is solved
       ii) eliminate and only choice do not change the state of the Sudoku
      iii) Any of the values is unfulfilled
    In the first two cases return the sudoku else return False
    Args:
        values(dict): Sudoku in dictionary form
    Returns:
        The updated sudoku or False denoting the sudoku can't be solved.
    """
    able_to_reduce = True
    while able_to_reduce:
        previous_values = values.copy()
        values = eliminate(values)  #eliminate obvious clashes
        values = only_choice(values)    #eliminate only choices
        values = naked_twins(values)    #eliminate naked twin values from all other boxes
        # if values have changed, then there's a chance that we can further reduce puzzle
        able_to_reduce = values != previous_values
        # Sudoku is not solvable if there are any empty boxes
        if any(len(values[box]) == 0 for box in BOXES):
            return False
    return values

def search(values):
    """
    Uses Depth-first search and propagates using a search tree
    Args:
        values(dict): Sudoku in dictionary form
    Returns:
        The box with least possibilities
    """
    values = reduce_puzzle(values)

    #values can now be a dict or a bool depending on whether it's solvable further
    if not values:
        return False

    if all(len(value) == 1 for value in values.values()):
        return values

    #best choice to expand the tree is the one containing least possibilities
    best_key, best_choices = min(values.items(), key=lambda t: len(t[1]) if len(t[1]) > 1 else 10)
    #iterating all the possible values and searching recursively
    for choice in best_choices:
        values_copy = values.copy()
        values_copy[best_key] = choice
        values_copy = search(values_copy)
        if values_copy and all(len(values_copy[box]) == 1 for box in values_copy):
            return values_copy

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
        Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)  #convert grid into a dictionary form
    values = search(values) # using depth first search search for solutions recursively
    return values

ASSIGNMENTS = []

ROWS = "ABCDEFGHI"
COLS = "123456789"
BOXES = cross(ROWS, COLS)
ROW_UNITS = [cross(row, COLS) for row in ROWS]
COL_UNITS = [cross(ROWS, col) for col in COLS]
BOX_UNITS = [cross(rows, cols)
             for rows in ["ABC", "DEF", "GHI"]
             for cols in ["123", "456", "789"]]
DIAG_UNIT = [row+col for row, col in zip("ABCDEFGHI", "123456789")]
ANTI_DIAG_UNIT = [row+col for row, col in zip("ABCDEFGHI", "987654321")]
UNIT_LIST = ROW_UNITS + COL_UNITS + BOX_UNITS
UNITS = {box: [unit for unit in UNIT_LIST if box in unit] for box in BOXES}
PEERS = {box: set(box2 for unit in UNITS[box] for box2 in unit) - set([box])
         for box in BOXES}

if __name__ == '__main__':
    import time
    initial_time = time.time()
    # '7....196......532.4...6...7..647819...95.27...729364..6...9...5.976......142....9'
    diag_sudoku_grid = input("Enter the sudoku puzzle to solve row-wise, use '.' for blank spots:\n")
    display(grid_values(diag_sudoku_grid))
    final_time = time.time()
    display(solve(diag_sudoku_grid))
    print("It took {} seconds to solve this puzzle.".format(final_time - initial_time))
    

    try:
        from visualize import visualize_assignments
        visualize_assignments(ASSIGNMENTS)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue.')
