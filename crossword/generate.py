import sys

from crossword import Crossword, Variable


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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        for variable in self.domains:
            length_of_variable = variable.length
            updated_words = {word for word in self.domains.get(
                variable) if len(word) == length_of_variable}
            self.domains[variable] = updated_words

    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Solution indicated by slides:
        # revised = False
        # overlapped_index_x, overlapped_index_y = self.crossword.overlaps[x, y]
        # # for x in X.domain:
        # for word_x in self.domains.get(x).copy():
        #     no_y_satisfies = True
        #     # if no y in Y.domain satisfies constraint for (X, Y):
        #     for word_y in self.domains.get(y):
        #         if word_y[overlapped_index_y] == word_x[overlapped_index_x]:
        #             no_y_satisfies = False
        #     if no_y_satisfies:
        #         # delete x from X.domain
        #         self.domains[x].remove(word_x)
        #         # revised = true
        #         revised = True
        # return revised

        # My solution:
        # If x does not overlap with y, then there's no arc consistency
        # between them. Thus return false directly.
        if self.crossword.overlaps[x, y] is None:
            return False

        # If x overlaps with y, then the value of self.crossword.overlaps[x, y]
        # is the index where they overlap with each other.
        overlapped_index_x, overlapped_index_y = self.crossword.overlaps[x, y]
        overlapped_char_set = {
            word[overlapped_index_y] for word in self.domains[y]}

        old_words = self.domains.get(x)
        updated_words = {
            word for word in old_words if word[overlapped_index_x] in overlapped_char_set}
        self.domains[x] = updated_words
        if updated_words == old_words:
            return False
        return True

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = []
        if arcs is None:
            # queue = all arcs in csp (constraint satisfication problem)
            # All arcs: all overlapped variables.
            for variable in self.domains:
                neighbors = self.crossword.neighbors(variable)
                for neighbor in neighbors:
                    queue.append((variable, neighbor))
        else:
            queue = arcs

        while queue:
            variable, neighbor = queue.pop(0)
            if self.revise(variable, neighbor):
                if len(self.domains.get(variable)) == 0:
                    return False
                # for each Z in X.neighbors - {Y}:
                # ENQUEUE(queue, (Z, X))
                # Namely, if we have revised variable, then will the element(s) that
                # we delete from variable's options, affect variable's relation with
                # other variables other than neighbor? In case to figure that out,
                # we need to add (every neighbor of variable, variable) to the queue.
                revised_neighbors = self.crossword.neighbors(variable) - {neighbor}
                for new_neighbor in revised_neighbors:
                    queue.append((new_neighbor, variable))
        return True

    def assignment_complete(self, assignment: dict):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for value in self.domains:
            if value not in assignment:
                return False

        return True

    def consistent(self, assignment: dict):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # all values are distinct:
        if len(assignment.values()) != len(set(assignment.values())):
            return False

        # every value is the correct length:
        for variable, word in assignment.items():
            if variable.length != len(word):
                return False

            # there are no conflicts between neighboring variables:
            # Get a set of neighbors of this variable.
            variable_neighbors = self.crossword.neighbors(variable)

            # Check if the overlapped char of the variable itself and its neighbor is the same.
            for neighbor in variable_neighbors:
                if neighbor in assignment:
                    char_in_v, char_in_neighbor = self.crossword.overlaps[variable, neighbor]
                    if word[char_in_v] != assignment.get(neighbor)[char_in_neighbor]:
                        return False

        return True

    def order_domain_values(self, var: Variable, assignment: dict):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        possible_words_list = list(self.domains.get(var))
        # substract already assigned variables.
        neighbors_of_var = self.crossword.neighbors(var) - set(assignment.keys())

        result_dict = {}
        for word in possible_words_list:
            counter = 0
            for neighbor in neighbors_of_var:
                char_in_v, char_in_neighbor = self.crossword.overlaps[var, neighbor]
                neighbor_words = self.domains.get(neighbor)
                for neighbor_word in neighbor_words:
                    if word[char_in_v] != neighbor_word[char_in_neighbor]:
                        counter += 1
            result_dict.update({counter: word})

        result_dict = dict(sorted(result_dict.items()))
        return list(result_dict.values())

    def select_unassigned_variable(self, assignment: dict) -> Variable:
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        all_unassigned_variables = [
            variable for variable in self.domains.keys() if variable not in assignment.keys()]
        all_unassigned_variables = sorted(all_unassigned_variables, key=lambda variable: (
            len(self.domains.get(variable)), -len(self.crossword.neighbors(variable))))

        return all_unassigned_variables[0]

    def backtrack(self, assignment: dict) -> dict:
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        variable = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(variable, assignment):
            new_assignment = assignment.copy()
            new_assignment.update({variable: word})
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # structure = "data/structure1.txt"
    # words = "data/words1.txt"
    # output = None

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
