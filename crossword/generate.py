import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains.keys():
            words = self.domains[var].copy()
            for word in words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False
        
        revised = False
        x_words = self.domains[x].copy()

        for x_word in x_words:
            y_words = self.domains[y].copy()

            for y_word in self.domains[y]:
                if x_word[overlap[0]] != y_word[overlap[1]]:
                    y_words.remove(y_word)
            
            if len(y_words) == 0:
                self.domains[x].remove(x_word)
                revised = True
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            vars = self.domains.keys()
            for var in vars:
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    arcs.append((var, neighbor))

        while len(arcs) > 0:
            (x, y) = arcs[0]
            arcs.pop(0)

            if self.revise(x, y):
                if len(self.domains[x]):
                    return False
                
                neighbors = self.crossword.neighbors(x).difference({y})
                for z in neighbors:
                    arcs.append((z, x))
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            try:
                if len(assignment[var]) == 0:
                    return False
            except:
                return False
        
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        taken_words = set()

        for var in assignment.keys():
            value = assignment[var]
            if taken_words.issuperset({value}):
                return False
            
            taken_words.add(value)
            
            if var.length != len(value):
                return False

            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]

                try:
                    if value[overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False
                except KeyError:
                    continue

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #each key is a possible value of the variable
        #each value is the total count (int) of other values eliminated in neighbors
        values_eliminated_count = dict()

        #get neighbors
        neighbors = self.crossword.neighbors(var)

        #Get the domain of variable
        domain_set = self.domains[var].copy()

        #calculate values of values_eliminated_count
        for value in domain_set:
            values_eliminated_count.update({value : 0})
            for neighbor in neighbors:
                assigned_vars = assignment.keys()

                neighbor_is_assigned = False
                for assigned_var in assigned_vars:
                    if neighbor == assigned_var:
                        neighbor_is_assigned = True
                        break

                if neighbor_is_assigned:
                    continue

                neighbor_values = self.domains[neighbor]
                overlaps = self.crossword.overlaps[var, neighbor]
                for neighbor_value in neighbor_values:
                    if neighbor_value == value:
                        values_eliminated_count[value] += 1
                        continue
                    
                    if value[overlaps[0]] != neighbor_value[overlaps[1]]:
                        values_eliminated_count[value] += 1

        #Create list of values to return
        values_list = []
        while len(domain_set) > 0:
            least_constraining_value = None
            for value in domain_set:
                if least_constraining_value is None or values_eliminated_count[value] < values_eliminated_count[least_constraining_value]:
                    least_constraining_value = value

            values_list.append(least_constraining_value)
            domain_set.remove(least_constraining_value)

        return values_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        variables = self.crossword.variables.copy()
        for variable in assignment.keys():
            variables = variables.difference({variable})

        smallest_domain_vars = []
        smallest_domain_len = None
        for variable in variables:
            if smallest_domain_len is None or len(self.domains[variable]) < smallest_domain_len:
                smallest_domain_vars = [variable]
                smallest_domain_len = len(self.domains[variable])
            elif len(self.domains[variable]) == smallest_domain_vars:
                smallest_domain_vars.append(variable)

        if len(smallest_domain_vars) == 1:
            return smallest_domain_vars[0]

        highest_neighbor_count_var = smallest_domain_vars[0]
        num_of_neighbors = len(self.crossword.neighbors(smallest_domain_vars[0]))
        for variable in smallest_domain_vars:
            if len(self.crossword.neighbors(variable)) > num_of_neighbors:
                highest_neighbor_count_var = variable
                num_of_neighbors = len(self.crossword.neighbors(variable))

        return highest_neighbor_count_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        values = self.order_domain_values(var, assignment)

        for value in values:
            assignment.update({var : value})

            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result

            assignment.pop(var, None)

        return None  

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
