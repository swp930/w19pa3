from __future__ import absolute_import, division, print_function
from math import sqrt, log
import pygame
import random
import copy
import heapq

#Feel free to add extra classes and functions
class State:
    # State constructor to initialize grid, player, parent, current coordinate, and
    # options
    def __init__(self, grid, player, parent, coord, options):
        self.grid = grid
        self.player = player
        self.parent = parent
        self.children = []
        self.Q = 0
        self.N = 0
        self.coord = coord
        self.counter = 0
        self.grid_count = 11
        self.options = options
        if(coord is None):
            self.terminalVal = False
        else:
            val = self.check_win()
            #print(val)
            #print(self.grid)
            #val2 = input("")
            self.terminalVal = val

    # Adds child to states children
    def add_child(self, child):
        self.children.append(child)

    # Gets continuous count in a specific direction
    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result
    
    # Check if this current board is a winner
    def check_win(self):
        grid = self.grid
        r, c = self.coord
        n_count = self.get_continuous_count(r, c, -1, 0)
        s_count = self.get_continuous_count(r, c, 1, 0)
        e_count = self.get_continuous_count(r, c, 0, 1)
        w_count = self.get_continuous_count(r, c, 0, -1)
        se_count = self.get_continuous_count(r, c, 1, 1)
        nw_count = self.get_continuous_count(r, c, -1, -1)
        ne_count = self.get_continuous_count(r, c, -1, 1)
        sw_count = self.get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            return True
        return False
        

class MCTS:
    # Constructor for MCTS 
    def __init__(self, grid, player, r, c, first):
        self.first = first
        self.grid = grid
        self.game_over = False
        self.player = player
        self.maxrc = len(grid)-1
        self.winner = None
        self.winner_m = None
        self.piece = player
        self.grid_count = 11
        self.root = State(grid, player, None, (r, c), self.get_options_ibounds(grid, r, c))
        #print("Options", self.root.options)
        self.root.counter = 1
        self.grid_size = 46
        self.start_x, self.start_y = 38, 55
        self.edge_size = self.grid_size // 2
        self.counter = 1

    def uct_search(self):
        i = 0
        # Computational budget 150000 loops
        while i < 800: 
            print("Loop: ", i)
            # Run selection with the root
            #print(self.root)
            #print(self.root.grid)
            #val = input("")
            s = self.selection(self.root)
            #print(s.grid)
            #val = input("")
            # Retrieve simulation for current board
            winner = self.simulation(s)
            # Backpropogate to best winner
            self.backpropagation(s, winner)
            i += 1
            if(self.first and i > 30):
                break
        max = 0
        maxNode = None
        print(len(self.root.children))
        print(self.root.Q, self.root.N)
        # Retrieve node with max Q/N
        for node in self.root.children:
            print("Ratio", node.Q, node.N)
            val = node.Q/node.N
            if(val > max):
                max = val
                maxNode = node
        return maxNode.coord

    def selection(self, state):
        # Go down to terminal val
        while not state.terminalVal:
            #print("Running selection")
            # Check whether state is expanded
            #val = input("")
            expanded = self.isFullyExpanded(state)
            if not expanded:
                #print("Not fully expanded")
                #val = input("")
                return self.expansion(state)
            else: # If not fully expanded then return the best child
                #print("Fully expanded")
                #val = input("")
                newChild = self.best_child(state)
                if(newChild is None):
                    return state
                state = newChild
        return state
            
    # Every node knows its available options so if a node has 0 options then 
    # it must not have any children
    def isFullyExpanded(self, state):
        #print(state.counter)
        #print(state.grid)
        #print(state.options)
        return len(state.options) == 0

    # Expand one node
    def expansion(self, state):
        newGrid = copy.deepcopy(state.grid)

        # Remove an option from the node
        #print(state.options)
        #val = input("")
        
        #r,c = state.options.pop(self.get_best_option(state))
        opt = heapq.heappop(state.options)
        #print(opt)
        r, c = opt[1]
        #val = input("")
        #print(r, c)
        #print(r, c)
        #print(state.options)
        #val = input("")

        playerVal = ''
        if state.player == 'b':
            playerVal = 'w'
        else:
            playerVal = 'b'
        if newGrid[r][c] == '.':
            newGrid[r][c] = state.player


            # Create a child with new options
            #newChildOptions = self.get_options_modified(newGrid, r, c, False)
            newChildOptions = self.get_options_ibounds(newGrid, r, c)
            if(len(newChildOptions) == 0):
                print("Maybe you done goofed?")
                print(r, c)
                print(newGrid)
                testOptions = self.get_options_modified(newGrid, r, c, True)
                #val = input("")
            newChild = State(newGrid, playerVal, state, (r,c), newChildOptions)
            newChild.counter = self.counter
            self.counter += 1
            state.add_child(newChild)
            return newChild
        else:
            # Create a child with new options
            #newChildOptions = self.get_options_modified(newGrid, r, c, False)
            newChildOptions = self.get_options_ibounds(newGrid, r, c)
            if(len(newChildOptions) == 0):
                print("Maybe you done goofed #2?")
                print(r, c)
                print(newGrid)
                testOptions = self.get_options_modified(newGrid, r, c, True)
                #val = input("")
            newChild = State(newGrid, playerVal, state, (r,c), newChildOptions)
            newChild.counter = self.counter
            self.counter += 1
            # Set terminal val to true since this game results in a tie.
            newChild.terminalVal = True
            state.add_child(newChild)
            return newChild

    def get_best_option(self, state):
        maxVal = 0
        maxOption = 0
        i = 0
        for opt in state.options:
            r, c = opt
            state.grid[r][c] = 'w'
            tmp = self.get_continuous_count_grid_max(state.grid, r, c)
            if(maxVal > tmp):
                maxVal = tmp
                maxOption = i
            state.grid[r][c] = '.'
            i += 1
        return maxOption
    
    def get_continuous_count_grid_max(self, grid, r, c):
        n_count = self.get_continuous_count_grid(grid, r, c, -1, 0)
        s_count = self.get_continuous_count_grid(grid, r, c, 1, 0)
        e_count = self.get_continuous_count_grid(grid, r, c, 0, 1)
        w_count = self.get_continuous_count_grid(grid, r, c, 0, -1)
        se_count = self.get_continuous_count_grid(grid, r, c, 1, 1)
        nw_count = self.get_continuous_count_grid(grid, r, c, -1, -1)
        ne_count = self.get_continuous_count_grid(grid, r, c, -1, 1)
        sw_count = self.get_continuous_count_grid(grid, r, c, 1, -1)
        return max((n_count + s_count), (e_count + w_count), (se_count + nw_count), (ne_count + sw_count))

    def get_continuous_count_grid(self, grid, r, c, dr, dc):
        piece = grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    def best_child(self, state):
        maxNode = None
        maxVal = 0
        # Choose the child with the greatest Q'/N' + sqrt(log(N)/N')
        for child in state.children:
            tmp = child.Q/child.N + 2.0*sqrt(log(state.N)/child.N)
            if(tmp > maxVal):
                maxNode = child
                maxVal = tmp
        if(maxNode is None):
            #print(state.grid)
            self.drawScreen(state.grid)
            print("You done goofed!")
            #val = input("")
        return maxNode

    # Simulate a game until it finishes
    def simulation(self, state):
        return self.rollout_m(copy.deepcopy(state.grid))
        #self.game_over = False
        #simReward = {}
        ##print("Simulation start")
        ##("Game over: ", self.game_over)
        #while not self.game_over:
        #    #print("Game over loop: ", self.game_over)
        #    r,c = self.make_move(state)
        #    if (r,c) != (-1, -1):
        #        self.set_piece(state,r,c)
        #        self.check_win(state,r,c)
        #    else: 
        #        break
        #if self.winner == 'b':
        #    simReward['b'] = 0
        #    simReward['w'] = 1
        #elif self.winner == 'w':
        #    simReward['b'] = 1
        #    simReward['w'] = 0
        #print(simReward)
        #return simReward

    # Set a particular piece to the current player
    def set_piece(self, state, r, c):
        grid = state.grid
        if grid[r][c] == '.':
            grid[r][c] = state.player
            if state.player == 'b':
                state.player = 'w'
            else:
                state.player = 'b'
            return True
        return False

    # Make a move on the board
    def make_move(self, state):
        grid = state.grid
        options = self.get_options(grid)
        #print("Make move: ", options)
        if(len(options) != 0):
            return random.choice(options)
        return -1, -1

    def get_options_modified(self, grid, row, col, verbose):
        current_pcs = []
        #r - 2 to r + 2
        #c - 2 to c + 2
        for r in range(row - 2, row + 2):
            for c in range(col - 2, col + 2):
                if(r >= 0 and r < len(grid) and c >= 0 and c < len(grid)):
                    if grid[r][c] == '.':
                        current_pcs.append((r,c))
                    if verbose:
                        print("Valid piece:", r, c, "Value: ", grid[r][c])
                else:
                    if(verbose):
                        print(r, c)
        return current_pcs
    
    def get_best_white(self, grid):
        maxWhite = 0
        whitePos = 5, 5
        for r in range(len(grid)):
            for c in range(len(grid)):
                if(grid[r][c] == 'w'):
                    n_count = self.get_continuous_count_m(grid, r, c, -1, 0)
                    s_count = self.get_continuous_count_m(grid, r, c, 1, 0)
                    e_count = self.get_continuous_count_m(grid, r, c, 0, 1)
                    w_count = self.get_continuous_count_m(grid, r, c, 0, -1)
                    se_count = self.get_continuous_count_m(grid, r, c, 1, 1)
                    nw_count = self.get_continuous_count_m(grid, r, c, -1, -1)
                    ne_count = self.get_continuous_count_m(grid, r, c, -1, 1)
                    sw_count = self.get_continuous_count_m(grid, r, c, 1, -1)
                    maxCount = max((n_count + s_count), (e_count + w_count), (se_count + nw_count), (ne_count + sw_count))
                    if(maxCount > maxWhite):
                        maxWhite = maxCount
                        whitePos = (r, c)
        return whitePos
                    
        

    def get_options_ibounds(self, grid, row, col):
        row, col = self.get_best_white(grid)
        current_pcs = []
        optimal_pcs = []
        bottom = 0
        top = 0
        left = 0
        right = 0
        if(row - 2 < 0):
            bottom = 0
            top = 5
        elif(row + 3 > len(grid)):
            top = len(grid) - 1
            bottom = len(grid) - 6
        else:
            bottom = row - 2
            top = row + 2
        if(col - 2 < 0):
            left = 0
            right = 5
        elif(col + 3 > len(grid)):
            right = len(grid) - 1
            left = len(grid) - 6
        else:
            left = col - 2
            right = col + 2

        for r in range(bottom, top):
            for c in range(left, right):
                if(grid[r][c] == '.'):
                    grid[r][c] = 'w'
                    count = self.get_continuous_count_grid_max(grid, r, c)
                    n_count = self.get_continuous_count_m(grid, r, c, -1, 0)
                    s_count = self.get_continuous_count_m(grid, r, c, 1, 0)
                    e_count = self.get_continuous_count_m(grid, r, c, 0, 1)
                    w_count = self.get_continuous_count_m(grid, r, c, 0, -1)
                    se_count = self.get_continuous_count_m(grid, r, c, 1, 1)
                    nw_count = self.get_continuous_count_m(grid, r, c, -1, -1)
                    ne_count = self.get_continuous_count_m(grid, r, c, -1, 1)
                    sw_count = self.get_continuous_count_m(grid, r, c, 1, -1)
                    #print(r, c)
                    #print(count)
                    #print(grid)
                    maxCount = max((n_count + s_count), (e_count + w_count), (se_count + nw_count), (ne_count + sw_count))
                    #print(maxCount)
                    #val = input("")
                    grid[r][c] = '.'
                    
                    current_pcs.append((-maxCount, (r, c)))
                    if(maxCount > 2):
                        optimal_pcs.append((-maxCount, (r, c)))
        #print("Current_pcs", current_pcs)
        if(len(optimal_pcs) > 0):
            heapq.heapify(optimal_pcs)
            current_pcs = optimal_pcs
            print("Optimal")
        else:
            heapq.heapify(current_pcs)
            print("Not optimal")
        #print("Heaplist", current_pcs)
        #return heapq.heapify(current_pcs)
        return current_pcs

    def get_options_tmp(self, grid, row, col):
        #collect all occupied spots
        current_pcs = []
        for r in range(row - 2, row + 3):
            for c in range(col - 2, col + 3):
                if(r >= 0 and r < len(grid) and c >= 0 and c < len(grid)):
                    if not grid[r][c] == '.':
                        current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc//2, self.maxrc//2)]
        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i,j))
        if len(options) == 0:
            #print("Get options length", len(options))
            #In the unlikely event that no one wins before board is filled
            #Make white win since black moved first
            self.game_over = True
            print("Setting self.winner in get_options")
            #val = input("")
            self.winner = 'w'
        return options

    def get_options(self, grid):
        #collect all occupied spots
        current_pcs = []
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc//2, self.maxrc//2)]
        #Reasonable moves should be close to where the current pieces are
        #Think about what these calculations are doing
        #Note: min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i,j))
        if len(options) == 0:
            #print("Get options length", len(options))
            #In the unlikely event that no one wins before board is filled
            #Make white win since black moved first
            self.game_over = True
            print("Setting self.winner in get_options")
            #val = input("")
            self.winner = 'w'
        return options
    
    # Gets continuous count in a specific direction
    def get_continuous_count(self, grid, r, c, dr, dc):
        piece = grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result
    
    # Check if a player won
    def check_win(self, state, r, c):
        grid = state.grid
        n_count = self.get_continuous_count(grid, r, c, -1, 0)
        s_count = self.get_continuous_count(grid, r, c, 1, 0)
        e_count = self.get_continuous_count(grid, r, c, 0, 1)
        w_count = self.get_continuous_count(grid, r, c, 0, -1)
        se_count = self.get_continuous_count(grid, r, c, 1, 1)
        nw_count = self.get_continuous_count(grid, r, c, -1, -1)
        ne_count = self.get_continuous_count(grid, r, c, -1, 1)
        sw_count = self.get_continuous_count(grid, r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            self.game_over = True

    # Backpropogate and update parent nodes
    def backpropagation(self, state, result):
        #print("Backpropogation start")
        #print(result)
        #val = input("")
        while state is not None:
            #print("Before: ", state.player, state.Q, state.N)
            #val = input("")
            if(len(result) == 0):
                state.Q += 0.5
            elif result[state.player] == 0:
                state.Q += 1
            state.N += 1
            #print("After: ", state.Q, state.N)
            #val = input("")
            state = state.parent


    def rollout_m(self, grid):
        self.game_over = False
        simReward = {}
        while not self.game_over:
            r,c = self.make_move_m(grid)
            self.set_piece_m(grid,r,c)
            self.check_win_m(grid,r,c)
        #assign rewards
        if self.winner_m == 'b':
            simReward['b'] = 0
            simReward['w'] = 1
        elif self.winner_m == 'w':
            simReward['b'] = 1
            simReward['w'] = 0
        print("Rolling out, winner is ", self.winner_m)
        print(simReward)
        return simReward

    def get_continuous_count_m(self, grid, r, c, dr, dc):
        piece = grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result

    def set_piece_m(self, grid, r, c):
        if grid[r][c] == '.':
            grid[r][c] = self.piece
            if self.piece == 'b':
                self.piece = 'w'
            else:
                self.piece = 'b'
            return True
        return False

    def check_win_m(self, grid, r, c):
        #print(r, c)
        n_count = self.get_continuous_count_m(grid, r, c, -1, 0)
        s_count = self.get_continuous_count_m(grid, r, c, 1, 0)
        e_count = self.get_continuous_count_m(grid, r, c, 0, 1)
        w_count = self.get_continuous_count_m(grid, r, c, 0, -1)
        se_count = self.get_continuous_count_m(grid, r, c, 1, 1)
        nw_count = self.get_continuous_count_m(grid, r, c, -1, -1)
        ne_count = self.get_continuous_count_m(grid, r, c, -1, 1)
        sw_count = self.get_continuous_count_m(grid, r, c, 1, -1)
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            self.winner_m = grid[r][c]
            self.game_over = True
            #print(self.game_over)
            #print(grid)

    def make_move_m(self, grid):
        options = self.get_options(grid)
        if len(options) == 0:
            return -1, -1
        return random.choice(options)

    def drawScreen(self, grid):
        for r in range(len(grid)):
            for c in range(len(grid)):
                if(grid[r][c] != '.'):
                    print(grid[r][c])
                else:
                    print('x')

        
