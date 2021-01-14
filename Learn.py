# import libraries

from random import randint
from random import random
from math import tanh
import pickle
from time import time


# define the class

class State:
    def __init__(self, states_value):
        self.rolls = [randint(1, 6), randint(1, 6)]  # each player's roll
        self.moves_list = [[0]]  # list of aall possible moves moves
        self.states = []  # a running list of board positions from this particular game
        self.states_value = states_value  # a dictionary of board positions and their values
        self.learn_rate = 0.1  # 0 is learn nothing new, 1 is only consider new information
        self.discount_factor = 0.99  # 0 is myopic, 1 is long term accuracy
        self.turn = 0  # the current player's turn
        self.guesses = []  # a running list of a games guesses
        self.wins = [0, 0]  # a tally of winning between the first player and the second
        for i in reversed(range(6)):
            self.moves_list.append([i+1, i+1])
        for i in reversed(range(6)):
            self.moves_list.append([i+1])

    # the main method to play a game

    def play(self, rounds=50):
        for i in range(rounds):
            if i % 1000000 == 0:
                print("Rounds {}".format(i))
                outfile1 = open('Liars_dic', 'wb')
                pickle.dump(self.states_value, outfile1)
                outfile1.close()
                print(str((time() - begin)/60) + ' minutes')
            while 1:
                available_moves = self.available_moves()
                move = self.choose_move(available_moves)
                state = self.get_hash(move)
                self.add_state(state)
                if move == [0]:
                    winner = self.check_winner()
                    if winner == 0:
                        self.wins[0] += 1
                    if winner == 1:
                        self.wins[1] += 1
                    self.feed_reward(winner)
                    self.reset()
                    break
                else:
                    self.guesses.append(move)
                    self.turn = (self.turn + 1) % 2

    # find all available moves possible in the current game

    def available_moves(self):
        if not self.guesses:
            return self.moves_list[1:]
        for i in range(13):
            if self.guesses[-1] == self.moves_list[i]:
                return self.moves_list[0:i]

    # choose a move to be played

    def choose_move(self, moves):
        if len(moves) == 1:
            return moves[0]
        if self.win_possible():
            print('playing winning move')
            return [0]
        move_value_list = []
        for p in moves:
            move_hash = self.get_hash(p)
            #print(move_hash)
            move_value = 0 if self.states_value.get(move_hash) is None else self.states_value.get(move_hash)
            move_value_list.append([(tanh(2*move_value)+1)/2, p])
        move_value_list.sort(reverse=True, key=lambda x: x[0])
        #print('Move list is: ' + str(move_value_list))
        i = 0
        while 1:
            chance = random()
            #print('trying move ' + str(i) + ' with a roll of ' + str(chance))
            if chance < move_value_list[i][0]:
                return move_value_list[i][1]
            else:
                i += 1
                i = i % (len(moves)-1)

    # get a hash of the current state to be used to gt a value from the states_value dictionary

    def get_hash(self, move):
        move_hash = str(self.rolls[self.turn])+str(move)+str(self.guesses)
        return move_hash

    # check if a guaranteed win is possible by calling 0

    def win_possible(self):
        if not self.guesses:
            return False
        if len(self.guesses[-1]) == 2 and self.guesses[-1][0] != self.rolls[self.turn] and self.rolls[self.turn] != 1:
            print(' i can win!!!!!!')
            print(self.rolls[self.turn])
            print(self.guesses)
            return True
        print('no win possible')
        return False

    # check who has won, this is called after someone has opted to check all dice

    def check_winner(self):
        for i in range(2):
            if self.rolls[i] == 1:
                self.rolls[i] = self.guesses[-1][0]
        if len(self.guesses[-1]) == 1:
            if self.guesses[-1][0] == self.rolls[0] or self.guesses[-1][0] == self.rolls[1]:
                return (self.turn+1) % 2
            else:
                return self.turn
        if len(self.guesses[-1]) == 2:
            if self.guesses[-1][0] == self.rolls[0] and self.guesses[-1][0] == self.rolls[1]:
                return (self.turn+1) % 2
            else:
                return self.turn

    # reset the game variables after it has finished

    def reset(self):
        self.rolls = [randint(1, 6), randint(1, 6)]
        self.turn = 0
        self.guesses = []
        self.states = []

    # upate the states_value dictionary

    def feed_reward(self, winner):
        i = 0
        for st in self.states:
            if i % 2 == winner:
                reward = 1
            else:
                reward = -1
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            self.states_value[st] += self.learn_rate * ((self.discount_factor * reward) - self.states_value[st])
            #print('feeding ' + str(self.learn_rate * ((self.discount_factor * reward) - self.states_value[st])) + ' to ' + str(st))
            i += 1

    # add the current state to the states list

    def add_state(self, state):
        self.states.append(state)


# open the dictionary
infile1 = open('Liars_dic', 'rb')
liars_dic = pickle.load(infile1)
infile1.close()

# define the state
Game = State(liars_dic)

#start a timer
begin = time()

# play itself
Game.play()




