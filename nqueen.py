import math
import random
import time
import sys
import copy

PRINT_ITERATIONS = False
# default values
# size of board also shows how many queens are in game
BOARD_SIZE = 15
# size of each generation
POPULATION_SIZE = 10
# how many generations should I check
# -1 for no generation limit. (search to find a result)
GENERATION_SIZE = -1
TEST_COUNT = 25

added_boards = []

def print_board(board):
    ''' prints current board in a nice way!'''
    
    for row in range(len(board)):
        print("", end="|")

        queen = board.index(row)
        
        for col in range(len(board)):
            if col == queen:
                print("Q", end="|")
            else:
                print("_", end="|")
        print("")

def get_h_cost(board):
    h = 0
    for i in range(len(board)):
        # Check every column we haven't already checked
        for j in range(i + 1, len(board)):
            # Queens are in the same row
            if board[i] == board[j]:
                h += 1
            # Get the difference between the current column
            # and the check column
            offset = j - i
            # To be a diagonal, the check column value has to be
            # equal to the current column value +/- the offset
            if board[i] == board[j] - offset or board[i] == board[j] + offset:
                h += 1

    return h


def make_move_steepest_hill(board):

    moves = {}
    for col in range(len(board)):

        for row in range(len(board)):
            if board[col] == row:
                # We don't need to evaluate the current
                # position, we already know the h-value
                continue

            board_copy = list(board)
            # Move the queen to the new row
            board_copy[col] = row
            moves[(col, row)] = get_h_cost(board_copy)

    best_moves = []
    h_to_beat = get_h_cost(board)
    for k, v in moves.items():
        if v < h_to_beat:
            h_to_beat = v

    for k, v in moves.items():
        if v == h_to_beat:
            best_moves.append(k)

    # Pick a random best move
    if len(best_moves) > 0:
        pick = random.randint(0, len(best_moves) - 1)
        col = best_moves[pick][0]
        row = best_moves[pick][1]
        board[col] = row

    return board


def random_restart():
    board = [random.randint(0, BOARD_SIZE-1) for i in range(BOARD_SIZE)]
    return board


def hill_climb(board):

    iteration = 0
    restart_count = 0
    while get_h_cost(board) != 0:

        added_boards.append(list(board))
        if PRINT_ITERATIONS == True:
            print("Iteration : ", iteration, ','.join(str(v)
                                                      for v in board), 'h : ', get_h_cost(board))
        board = make_move_steepest_hill(board)
        iteration = iteration+1

        if list(board) in added_boards:
            if PRINT_ITERATIONS == True:
                print('Local min : Restarting ..')
            board = random_restart()
            restart_count = restart_count+1
            del added_boards[:]
    if PRINT_ITERATIONS == True:
        print("Iteration : ", iteration, ','.join(str(v)
                                                  for v in board), 'h : ', get_h_cost(board))
    return iteration, restart_count, board


def start_hill_climbing():
    print(' '*16,BOARD_SIZE,'Queen Hill Climbing\n')
    print(' '*16, 'Iteration', ' '*15, 'Restart',
          ' '*8, 'Process Time', ' '*28, 'Last Board')
    total_time = 0

    for result in range(0, TEST_COUNT):
        start = time.clock()
        board = random_restart()
        iteration, restart_count, board = hill_climb(board)
        finish = time.clock()
        process_time = finish - start
        total_time += process_time

        if PRINT_ITERATIONS == True:
            print("==================================================================")
        if PRINT_ITERATIONS == True:
            print("Correct Answer found in iteration %s" %
                    iteration)
        # print result as a one lined list
        if PRINT_ITERATIONS == True:
            print(board)
        # print result as a nice game board
        if PRINT_ITERATIONS == True:
            print_board(board)

        print('Result : ', result+1, '\t\t', iteration, '\t\t\t',
              restart_count, '\t\t', format(process_time, '.6f'), '\t\t', board)
        print('-'*112)
    if TEST_COUNT>1:    
        print('Avg Process Time of ',TEST_COUNT,' Result : ',
          format(total_time/TEST_COUNT, '.6f'))


class Board:
    def __init__(self, board_size, goal):
        ''' initialize a board'''
        self.board_size = board_size
        self.goal = goal

        self.fitness = 0

        # put first items in bord
        self.queens = list(range(self.board_size))
        # switch half of them randomly
        self.switch(self.board_size/2)

    def __del__(self):
        pass

    def switch(self, count):
        ''' swithed queen places 'count' times'''
        count = int(count)

        for i in range(count):
            j = random.randint(0, self.board_size-1)
            k = random.randint(0, self.board_size-1)
            self.queens[j], self.queens[k] = self.queens[k], self.queens[j]

        # recheck fitness after moving queens
        self.compute_fitness()

    def regenerate(self):
        ''' randomly moves 3 queens
        used for creating new generation'''

        # randomly switvh 2 itmes
        self.switch(2)

        # get a random number if it's lower than 0.25 switch anither item
        if random.uniform(0, 1) < 0.25:
            self.switch(1)

    def compute_fitness(self):
        ''' computes fitness of current board
        bigger number is better'''
        self.fitness = self.goal

        for i in range(self.board_size):
            for j in range(i+1, self.board_size):
                if math.fabs(self.queens[i] - self.queens[j]) == j - i:
                    # for each queen guarding another one reduce fitness by 1
                    self.fitness -= 1

    def print_board(self):
        ''' prints current board in a nice way!'''
        for row in range(self.board_size):
            print("", end="|")

            queen = self.queens.index(row)

            for col in range(self.board_size):
                if col == queen:
                    print("Q", end="|")
                else:
                    print("_", end="|")
            print("")


class GaQueens:
    def __init__(self, board_size, population_size, generation_size):
        # store values to class properties
        self.board_size = board_size
        self.population_size = population_size
        self.generation_size = generation_size
        self.result_board = []
        # counts how many generations checked
        self.generation_count = 0
        # fitness value of goal
        self.goal = int((self.board_size*(self.board_size-1))/2)

        # current populations will go here
        self.population = []

        # creates the first population
        self.first_generation()

        while True:
            # if current population reached goal stop checking
            if self.is_goal_reached() == True:
                break
            # don't create more generations if program reached generation_size
            if -1 < self.generation_size <= self.generation_count:
                break

            # create another generation from last generation
            # (discards old generation)
            self.next_generation()
        if PRINT_ITERATIONS == True:
            print("==================================================================")

        # if couldn't find answer
        if -1 < self.generation_size <= self.generation_count:
            if PRINT_ITERATIONS == True:
                print("Couldn't find result in %d generations" %
                      self.generation_count)
                # if there was a result, print it
                pass
        elif self.is_goal_reached():
            if PRINT_ITERATIONS == True:
                print("Correct Answer found in generation %s" %
                      self.generation_count)
            for population in self.population:
                if population.fitness == self.goal:

                    # print result as a one lined list
                    if PRINT_ITERATIONS == True:
                        print(population.queens)
                    # print result as a nice game board
                    if PRINT_ITERATIONS == True:
                        population.print_board()
                    self.result_board.append(list(population.queens))

    def result(self):
        return self.generation_count, self.result_board

    def __del__(self):
        pass

    def is_goal_reached(self):
        ''' returns True if current population reached goal'''
        for population in self.population:
            if population.fitness == self.goal:
                return True
        return False

    def random_selection(self):
        ''' select some items from current population for next generation
        selection are items with highest fit value
        returns a list of selections'''
        population_list = []
        for i in range(len(self.population)):
            population_list.append((i, self.population[i].fitness))
        population_list.sort(key=lambda pop_item: pop_item[1], reverse=True)
        return population_list[:int(len(population_list)/3)]

    def first_generation(self):
        ''' creates the first generation '''
        for i in range(self.population_size):
            self.population.append(Board(self.board_size, self.goal))
        if PRINT_ITERATIONS == True:
            self.print_population()

    def next_generation(self):
        ''' creates next generations (all except first one)'''

        # add to generation counter
        self.generation_count += 1

        # get a list of selections to create next generation
        selections = self.random_selection()

        # creates a new population using given selection
        new_population = []
        while len(new_population) < self.population_size:
            sel = random.choice(selections)[0]
            new_population.append(copy.deepcopy(self.population[sel]))
        self.population = new_population

        # make random changes to current population
        for population in self.population:
            population.regenerate()
        if PRINT_ITERATIONS == True:
            self.print_population(selections)

    def print_population(self, selections=None):
        ''' print all items in current population
        Population #15
            Using: [1]
            0 : (25) [6, 1, 3, 0, 2, 4, 7, 5]
        line 1: Population #15
            shows current population id
        line 2: Using: [1]
            shows id of items from last generation
            used for creating current generation
        line 3: 0 : (25) [0, 1, 2, 3, 4, 5, 6, 7]
            0 -> item is
            (25) -> fitness for current item
            [0, 1, 2, 3, 4, 5, 7] -> queen positions in current item
        '''
        if PRINT_ITERATIONS == True:
            print("Population #%d" % self.generation_count)

        if selections == None:
            selections = []
        if PRINT_ITERATIONS == True:
            print("       Using: %s" % str([sel[0] for sel in selections]))

        count = 0
        for population in self.population:
            if PRINT_ITERATIONS == True:
                print("%8d : (%d) %s" %
                      (count, population.fitness, str(population.queens)))
                count += 1


def start_genetic_algorithm():

    # print some information about current quest!
    print("Starting:")
    print("    board size      : ", BOARD_SIZE)
    print("    population size : ", POPULATION_SIZE)
    print("    generation size : ", GENERATION_SIZE)
    print("==================================================================")

    print(' '*18,BOARD_SIZE,'Queen Genetic Algorithm\n')
    print(' '*18, 'Generation Count', ' '*16,
          'Process Time', ' '*32, 'Results')
    total_time = 0
    for result in range(0, TEST_COUNT):
        # Run!
        start = time.clock()
        generation, results = GaQueens(
            BOARD_SIZE, POPULATION_SIZE, GENERATION_SIZE).result()
        finish = time.clock()
        process_time = finish - start
        total_time += process_time

        print('Result : ', result+1, '\t\t\t', generation, '\t\t\t',
              format(process_time, '.6f'), '\t\t', results)
        print('-'*112)
    if TEST_COUNT>1:
        print('Avg Process Time of ',TEST_COUNT,' Result : ',
          format(total_time/TEST_COUNT, '.6f'))


def main():

    if(len(sys.argv) > 1) and sys.argv[1] == "-hc":

        if (len(sys.argv) > 2) and sys.argv[2] == "-p":

            global PRINT_ITERATIONS
            global TEST_COUNT
            PRINT_ITERATIONS = True
            TEST_COUNT = 1
        start_hill_climbing()
    elif (len(sys.argv) > 1) and sys.argv[1] == "-ga":

        if (len(sys.argv) > 2) and sys.argv[2] == "-p":

            PRINT_ITERATIONS = True
            TEST_COUNT  = 1
        start_genetic_algorithm()
    else:
        print("Hill Climbing  -hc\nGenetic Algorithm -ga\nPrint Iterations -p")


if __name__ == "__main__":
    main()
