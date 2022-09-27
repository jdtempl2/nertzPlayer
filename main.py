from statistics import mean, median
from collections import Counter
from NertzGame import *
from NertzGUI import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # get # of players & their names
    random.seed = 10

    names = ['Alf',
             'Bob',
             'Cat',
             'Dog',
             'Ela',
             'Flo',
             'Gob',
             'Hal',
             'Ike',
             'Joe']

    skills = ['bad',
              'good',
              'better',
              'best']

    strategy = ['never',
                'one-deep',
                'two-deep',
                'always']

    inputs = getInputs()

    #player_nums = [3,4,5,6]
    player_nums = inputs[0]
    number_games = inputs[1]

    for num in player_nums:
        table = Table()
        print('Playing {} games with {} players'.format(number_games, num))
        for n in range(num):
            table.add_player(names[n], skills[3], strategy[0])
        #table.players[0].strat = strategy[0]
        #table.players[1].strat = strategy[1]
        #table.players[2].strat = strategy[2]
        #table.players[3].strat = strategy[3]
        winners = []
        counts = []
        for g in range(number_games):
            game_stats = table.play_game()
            winners.append(game_stats.winner)
            counts.append(game_stats.round_count)
            if g > 0 and g % 100 == 0:
                print('.')
            elif g > 0 and g % 10 == 0:
                print('.', end='')

        print()
        print(Counter(winners))
        print('mean = {} \t median = {} \t max = {} \t min = {}'.format(mean(counts), median(counts), max(counts), min(counts)))
    #print()

    #for num in player_nums:
    #    counts = []
    #    table = Table()
    #    print('For {} players, playing {} games'.format(num, number_games))
    #    for n in range(num):
    #        table.add_player(names[n], skills[3], strategy[0])
    #    for g in range(number_games):
    #        counts.append(table.play_game())
    #    print('{}\nmean = {} \t median = {} \t max = {} \t min = {}'.format(counts, mean(counts), median(counts), max(counts), min(counts)))
    #    print()
