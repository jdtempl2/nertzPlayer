import random
from typing import List, Dict
from statistics import mean, median
from collections import Counter


class Card:
    def __init__(self, suit, value, owner):
        self.suit = suit  # string
        self.value = value  # number
        self.owner = owner  # string
        self.group = "U"  # U for 'unassigned' - can be N, S, H, or M
        self.face_down = True  # only used for 'Hand' cards
        self.color = 0
        if suit == 'B' or suit == 'D':
            self.color = 1

    def print_card(self, verbose=False):
        if self.value > 9:
            if verbose:
                print('{} {}:\t{}\t{}\t{}'.format(self.suit, self.value, self.group, self.owner, self.face_down))
            else:
                print('{} {}'.format(self.suit, self.value))
        else:
            if verbose:
                print('{}  {}:\t{}\t{}\t{}'.format(self.suit, self.value, self.group, self.owner, self.face_down))
            else:
                print('{}  {}'.format(self.suit, self.value))

    def is_red(self):
        return self.suit == "A" or self.suit == "C"

    def is_opposite_suit(self, other_card_is_red):
        return self.is_red() and not other_card_is_red

    def is_face_up(self):
        return not self.face_down

    def get_suit(self):
        return self.suit

    def get_value(self):
        return self.value

    def get_owner(self):
        return self.owner

    def get_group(self):
        return self.group

    def set_suit(self, suit):
        self.suit = suit

    def set_value(self, value):
        self.value = value

    def set_owner(self, owner):
        self.owner = owner

    def set_group(self, group):
        self.group = group

    def flip(self):
        self.face_down = ~self.face_down


class Stack:
    def __init__(self, group):
        self.stack: List[Card] = []
        self.group = group

    def print_stack(self, verbose=False):
        print('Stack type: {}'.format(self.group))
        if not self.is_empty():
            for card in self.stack:
                card.print_card(verbose)
        else:
            print('Empty stack!')
        print('+=== end of stack ===+')

    def is_empty(self):
        return self.get_size() == 0

    def get_size(self):
        return len(self.stack)

    def get_top(self):  # returns the last card placed on the stack
        if self.is_empty():
            return Card("E", 99, "Error")
        else:
            return self.stack[len(self.stack)-1]

    def add_card(self, card):
        self.stack.append(card)
        card.set_group(self.group)

    def remove_card(self):
        if self.is_empty():
            return
        else:
            self.stack.pop()

    def empty_stack(self):
        self.stack.clear()


class NertzStack(Stack):
    def __init__(self):
        group = "N"
        super().__init__(group)


class HandStack(Stack):
    def __init__(self):
        group = "H"
        super().__init__(group)

    def remove_card(self):
        self.stack.remove(self.get_top_face_up())

    def get_top_face_up(self):  # return the first face-up card, OR the 'top' card
        for card in self.stack:
            if card.is_face_up():
                return card
        return self.get_top()

    def get_top_face_up_idx(self):
        for card in self.stack:
            if card.is_face_up():
                return self.stack.index(card)
        return len(self.stack)

    def flip_three_cards(self):  # flip the last three face down cards in Stack
        top_face_up_idx = self.get_top_face_up_idx()

        if top_face_up_idx > 2:  # flip 3 cards
            self.stack[top_face_up_idx - 1].face_down = False
            self.stack[top_face_up_idx - 2].face_down = False
            self.stack[top_face_up_idx - 3].face_down = False

        else:  # need to flip all cards in hand & start over
            self.restack_hand(top_face_up_idx)
            self.stack[len(self.stack) - 1].face_down = False
            self.stack[len(self.stack) - 2].face_down = False
            self.stack[len(self.stack) - 3].face_down = False

    def restack_hand(self, new_top_idx):
        new_stack: List[Card] = []

        if new_top_idx > 0:
            for c in range(len(self.stack) - new_top_idx):
                new_stack.append(self.stack[c + new_top_idx])
            new_stack.append(self.stack[0])
            if new_top_idx == 2:
                new_stack.append(self.stack[1])

            self.empty_stack()

            for card in new_stack:
                self.add_card(card)

        for card in self.stack:
            card.face_down = True


class SolitaireStack(Stack):
    def __init__(self):
        group = "S"
        super().__init__(group)

    def get_bottom(self):
        return self.stack[0]

    def can_add_card(self, card: Card):
        if self.is_empty():
            return True
        else:
            top_card = self.get_top()
            if card.is_opposite_suit(top_card.is_red()):
                if card.get_value() == (top_card.get_value() - 1):
                    return True
            return False


class MiddleStack(Stack):
    def __init__(self):
        group = "M"
        super().__init__(group)

    def can_add_card(self, card: Card):
        top_card = self.get_top()
        if card.get_suit() == top_card.get_suit():
            if card.get_value() == top_card.get_value() + 1:
                return True
        return False


class Action:
    def __init__(self, name):
        self.name = name
        self.id = 0
        self.type = ""
        self.status = "idle"
        self.granted = False

    def clear(self):
        self.id = 0
        self.type = ""
        self.status = "idle"
        self.granted = False

    def set_waiting(self, stack_id, action_type):
        self.id = stack_id
        self.type = action_type
        self.status = "waiting"

    def is_waiting(self):
        return self.status == "waiting"

    def set_granted(self):
        self.status = "granted"

    def is_granted(self):
        return self.status == "granted"


def combine_solitaire_stacks(stack1: SolitaireStack, stack2: SolitaireStack):
    # take cards from stack 1 and put them onto stack 2, then clear stack 1
    for card in stack1.stack:
        stack2.add_card(card)
    stack1.empty_stack()


def can_stack_solitaire(card1: Card, card2: Card):
    # check if you can stack card2 on top of card1 for solitaire
    if not card1.color == card2.color:
        return card2.value == card1.value - 1
    return False


def can_stack_solitaire_2cards(card1: Card, card2: Card):
    # check if you will be able to stack card2 on top of card1
    if card1.color == card2.color:
        return card2.value == card1.value - 2
    return False


def can_stack_solitaire_ncards(card1: Card, card2: Card, num_cards):
    # check if you will be able to stack card2 on top of card1
    # n = number of cards between card1 and card2 (0 if no cards in between)
    if num_cards == 1:
        if not card1.color == card2.color:
            return card2.value == (card1.value - num_cards)
        return False

    if num_cards == 2:
        if card1.color == card2.color:
            return card2.value == (card1.value - num_cards) or can_stack_solitaire_ncards(card1, card2, num_cards-1)
        return False or can_stack_solitaire_ncards(card1, card2, num_cards-1)


class Player:
    def __init__(self, table, name, skill, strategy, do_print):
        self.table = table
        self.name = name
        self.deck: List[Card] = []
        self.score = 0
        self.called_nertz = False
        self.action = Action(name)
        self.solitaireStacks = [SolitaireStack(), SolitaireStack(), SolitaireStack(), SolitaireStack()]
        self.nertzStack = NertzStack()
        self.handStack = HandStack()
        self.skill = skill
        self.strat = strategy
        self.do_print = do_print

        # create deck of Cards for Player
        suits = ["A", "B", "C", "D"]  # A & C are red, B & D are black
        for suit in suits:
            for val in range(13):  # Ace, 1-10, J, Q, K
                self.deck.append(Card(suit, val+1, name))

    def clear_stacks(self):
        self.solitaireStacks = [SolitaireStack(), SolitaireStack(), SolitaireStack(), SolitaireStack()]
        self.nertzStack = NertzStack()
        self.handStack = HandStack()

    def declare_nertz(self):
        self.called_nertz = True

    def did_declare_nertz(self):
        return self.called_nertz

    def check_nertz(self):
        if self.nertzStack.is_empty():
            self.declare_nertz()
            if self.do_print:
                print('{} declared Nertz!'.format(self.name))

    def add_one(self):
        self.score = self.score + 1

    def minus_two(self):
        self.score = self.score - 2

    def print_deck(self, verbose=False):
        print('{}\'s deck:'.format(self.name))
        for card in self.deck:
            card.print_card(verbose)
        print('+==+')

    def print_stacks(self, verbose=False):
        print('{}\'s stacks:'.format(self.name))
        self.nertzStack.print_stack(verbose)
        for s in self.solitaireStacks:
            s.print_stack(verbose)
        self.handStack.print_stack(verbose)

    def shuffle_cards(self):
        random.shuffle(self.deck)

    def setup_cards(self):
        self.called_nertz = False
        self.clear_stacks()
        self.shuffle_cards()

        for i in range(13):
            self.nertzStack.add_card(self.deck[i])

        self.solitaireStacks[0].add_card(self.deck[13])
        self.solitaireStacks[1].add_card(self.deck[14])
        self.solitaireStacks[2].add_card(self.deck[15])
        self.solitaireStacks[3].add_card(self.deck[16])

        for i in range(17, 51):
            self.handStack.add_card(self.deck[i])

        self.handStack.flip_three_cards()

    def check_and_move_aces(self):
        any_aces = False

        top_nertz_card = self.nertzStack.get_top()
        top_hand_card = self.handStack.get_top_face_up()

        # check for Aces (val = 1) to send to Middle
        if top_nertz_card.value == 1:
            table.start_middle_stack(top_nertz_card)
            self.nertzStack.remove_card()
            if self.do_print:
                print('{} moved ace out from Nertz'.format(self.name))
            self.check_nertz()
            any_aces = True

        for solitaire in self.solitaireStacks:
            top_solitaire = solitaire.get_top()
            if top_solitaire.value == 1:
                table.start_middle_stack(top_solitaire)
                solitaire.remove_card()
                if self.do_print:
                    print('{} moved ace out from Solitaire'.format(self.name))
                self.check_solitaire_empty()
                any_aces = True

        if top_hand_card.value == 1:
            table.start_middle_stack(top_hand_card)
            self.handStack.remove_card()
            if self.do_print:
                print('{} moved ace out from Hand'.format(self.name))
            any_aces = True

        return any_aces

    def check_solitaire_empty(self):
        for stack in self.solitaireStacks:
            if stack.is_empty():
                stack.add_card(self.nertzStack.get_top())
                self.nertzStack.remove_card()
                if self.do_print:
                    print('{} moved Nertz to empty Solitaire stack'.format(self.name))
                self.check_nertz()
                return True
        return False

    def play_nertz_on_solitaire(self):
        for stack in self.solitaireStacks:
            nertz_card = self.nertzStack.get_top()
            if stack.can_add_card(nertz_card):
                stack.add_card(nertz_card)
                self.nertzStack.remove_card()
                if self.do_print:
                    print('{} played Nertz on Solitaire'.format(self.name))
                self.check_nertz()
                return True
        return False

    def play_nertz_to_middle(self, granted=True):
        nertz_card = self.nertzStack.get_top()
        for stack in self.table.middleStacks:
            if stack.can_add_card(nertz_card):
                self.action.set_waiting(id(stack), "N")
                if granted:
                    stack.add_card(nertz_card)
                    self.nertzStack.remove_card()
                    if self.do_print:
                        print('{} played Nertz to Middle!'.format(self.name))
                    self.check_nertz()
                    return True
                if self.do_print:
                    print('{} can play Nertz to Middle\t\t{}'.format(self.name, self.action.id))
                return True
        return False

    def check_nertz_to_middle(self):
        return self.play_nertz_to_middle(False)

    def play_hand_to_middle(self, granted=True):
        hand_card = self.handStack.get_top_face_up()
        for stack in self.table.middleStacks:
            if stack.can_add_card(hand_card):
                self.action.set_waiting(id(stack), "H")
                if granted:
                    stack.add_card(hand_card)
                    self.handStack.remove_card()
                    if self.do_print:
                        print('{} played Hand to Middle!'.format(self.name))
                    return True
                if self.do_print:
                    print('{} can play Hand to Middle\t\t\t{}'.format(self.name, self.action.id))
                return True
        return False

    def check_hand_to_middle(self):
        return self.play_hand_to_middle(False)

    def play_solitaire_to_middle(self, granted=True):
        for sol_stack in self.solitaireStacks:
            solitaire_card = sol_stack.get_top()
            for stack in self.table.middleStacks:
                if stack.can_add_card(solitaire_card):
                    self.action.set_waiting(id(stack), "S")
                    if granted:
                        stack.add_card(solitaire_card)
                        sol_stack.remove_card()
                        if self.do_print:
                            print('{} played Solitaire to Middle!'.format(self.name))
                        self.check_solitaire_empty()
                        return True
                    if self.do_print:
                        print('{} can play Solitaire to Middle\t{}'.format(self.name, self.action.id))
                    return True
        return False

    def check_solitaire_to_middle(self):
        return self.play_solitaire_to_middle(False)

    def consolidate_solitaire(self):
        for i in range(4):
            bottom_card = self.solitaireStacks[i].get_bottom()
            for stack in self.solitaireStacks:
                if stack.can_add_card(bottom_card):
                    for card in self.solitaireStacks[i].stack:
                        stack.add_card(card)
                    self.solitaireStacks[i].empty_stack()

                    if self.do_print:
                        print('{} consolidated Solitaire'.format(self.name))
                    self.check_solitaire_empty()
                    return True
        return False

    def play_hand_on_solitaire(self):
        # only move that uses strategy
        # can either:
        #    always - always move a Hand card to Solitaire if possible
        #    n-deep - ONLY move a card if there are N cards between Nertz and Solitaire
        #    never  - never move Hand cards to Solitaire

        if self.strat == 'never':
            return False

        elif self.strat == 'always':
            for stack in self.solitaireStacks:
                hand_card = self.handStack.get_top_face_up()
                if stack.can_add_card(hand_card):
                    stack.add_card(hand_card)
                    self.handStack.remove_card()
                    if self.do_print:
                        print('{} played Hand on Solitaire'.format(self.name))
                    return True
            return False

        else:
            num_deep = 0
            if self.strat == 'one-deep':
                num_deep = 1
            elif self.strat == 'two-deep':
                num_deep = 2

            for stack in self.solitaireStacks:
                hand_card = self.handStack.get_top_face_up()
                nertz_card = self.nertzStack.get_top()
                if stack.can_add_card(hand_card):
                    # check if hand card is right before the nertz card
                    if can_stack_solitaire_ncards(hand_card, nertz_card, num_deep):
                        stack.add_card(hand_card)
                        self.handStack.remove_card()
                        if self.do_print:
                            print('{} played Hand on Solitaire'.format(self.name))
                        return True
            return False

    def play_single_action(self):  # plays a single 'action', then returns

        # test actions in order of precedence
        # return if action occurs
        self.action.clear()

        if self.check_and_move_aces():
            return

        if self.check_nertz_to_middle():
            return

        if self.play_nertz_on_solitaire():
            return

        if self.consolidate_solitaire():
            return

        if self.check_solitaire_to_middle():
            return

        if self.check_hand_to_middle():
            return

        if self.play_hand_on_solitaire():
            return

        # if no action can happen, flip 3 cards
        self.handStack.flip_three_cards()
        if self.do_print:
            print('{} flipped 3 cards'.format(self.name))
        return

    def finish_single_action(self):
        if self.action.is_granted():
            if self.action.type == "N":
                self.play_nertz_to_middle()
                return '{} played Nertz to Middle!'.format(self.name)
            if self.action.type == "S":
                self.play_solitaire_to_middle()
                return '{} played Solitaire to Middle!'.format(self.name)
            if self.action.type == "H":
                self.play_hand_to_middle()
                return '{} played Hand to Middle!'.format(self.name)


class Table:
    def __init__(self):
        self.players: List[Player] = []
        self.middleStacks: List[MiddleStack] = []
        self.do_print = False

    def print_player_cards(self, verbose=False):
        for player in self.players:
            player.print_deck(verbose)

    def print_player_stacks(self, verbose=False):
        for player in self.players:
            player.print_stacks(verbose)

    def print_middle_stacks(self, verbose=False):
        for stack in self.middleStacks:
            stack.print_stack(verbose)

    def print_all_stacks(self, verbose=False):
        self.print_player_stacks(verbose)
        self.print_middle_stacks(verbose)

    def print_nertz_remaining(self):
        for player in self.players:
            print('{}\t'.format(len(player.nertzStack.stack)), end='')
        print()

    def print_scores(self):
        for player in self.players:
            print('{}\t'.format(player.score), end='')
        print()

    def add_player(self, name, skill, strat):
        self.players.append(Player(self, name, skill, strat, self.do_print))

    def get_player(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None

    def start_middle_stack(self, card: Card):
        self.middleStacks.append(MiddleStack())
        self.middleStacks[len(self.middleStacks)-1].add_card(card)

    def setup_table(self):
        for player in self.players:
            player.setup_cards()
        self.middleStacks.clear()

    def play_one_tick(self):
        if self.do_print:
            print("+=======================+")
        actions = []
        for player in self.players:
            player.play_single_action()
            if player.action.is_waiting():  # player.action is set iff an action to the middle can happen
                actions.append(player.action)

        while len(actions) > 0:
            if len(actions) > 1:
                # this is where it gets complicated
                # if any action has a once-occurring ID, then it is granted
                # if there are more than one identical IDs, then need to randomize who is granted
                temp_list = [actions[0]]
                for a in actions:
                    if id(a) != id(temp_list[0]):
                        if a.id == temp_list[0].id:
                            temp_list.append(a)
                temp_list[pick_a_player(len(temp_list))].set_granted()
                for t in temp_list:
                    actions.remove(t)
            else:
                actions[0].set_granted()
                actions.pop()

        for player in self.players:
            player.finish_single_action()

        return

    def play_round(self, game):
        timeout = 1000
        count = 0
        round_over = False
        game.timeout = False

        while not round_over:
            self.play_one_tick()
            if self.do_print:
                self.print_nertz_remaining()
            for player in self.players:
                if player.did_declare_nertz():
                    round_over = True
            if count > timeout:
                round_over = True
                game.timeout = True
            count = count + 1
        #self.print_all_stacks(True)

    def score_round(self, game):

        for middle_stack in self.middleStacks:
            for card in middle_stack.stack:
                self.get_player(card.owner).add_one()

        for player in self.players:
            for card in player.nertzStack.stack:
                player.minus_two()

        for player in self.players:
            if player.score == -50:
                player.score = 50
                #print('{} jumped from -50 to +50!'.format(player.name))
            if player.score == -100:
                player.score = 100
                #print('{} jumped from -100 to +100!'.format(player.name))
            if player.score >= 100:
                game.winner = player.name
                game.is_over = True

        #if self.do_print:
        #self.print_scores()
        return game

    def play_game(self):

        game = Game()
        game.round_count = 0

        while not game.is_over:
            game.timeout = True
            while game.timeout:
                self.setup_table()
                self.play_round(game)
            game.round_count = game.round_count + 1
            game = self.score_round(game)
            # if game.timeout:
            #    game.is_over = True
            #    game.winner = "stuck"
            #    game.round_count = -1

        if self.do_print:
            print('+=========================+')
            print('| Game over in {} rounds |'.format(game.round_count))
            print('+=========================+')

        for player in self.players:
            player.score = 0

        return game


class Game:
    def __init__(self):
        self.round_count = 0
        self.winner = ""
        self.scores = []
        self.is_over = False
        self.timeout = False


def pick_a_player(num_players):
    chances = []
    for p in range(num_players):
        chances.append(abs(0.5 - random.random()))
    return chances.index(min(chances))


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

    strategy = ['always',
                'two-deep',
                'one-deep',
                'never']

    player_nums = [6]

    number_games = 1000

    counts = []
    table = Table()

    for num in player_nums:
        print('Playing {} games with {} players'.format(number_games, num))
        for n in range(num):
            table.add_player(names[n], skills[3], strategy[0])
        table.players[0].strat = strategy[1]
        table.players[1].strat = strategy[1]
        table.players[2].strat = strategy[2]
        table.players[3].strat = strategy[2]
        winners = []
        for g in range(number_games):
            game_stats = table.play_game()
            winners.append(game_stats.winner)
            counts.append(game_stats.round_count)
            if g % 100 == 0:
                print()
            print('.', end='')
        print()
        print(Counter(winners))
    #print('{}\nmean = {} \t median = {} \t max = {} \t min = {}'.format(counts, mean(counts), median(counts), max(counts), min(counts)))
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
