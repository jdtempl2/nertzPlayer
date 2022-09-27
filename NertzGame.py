from Card import *
import random
from typing import List, Dict


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
            self.table.start_middle_stack(top_nertz_card)
            self.nertzStack.remove_card()
            if self.do_print:
                print('{} moved ace out from Nertz'.format(self.name))
            self.check_nertz()
            any_aces = True

        for solitaire in self.solitaireStacks:
            top_solitaire = solitaire.get_top()
            if top_solitaire.value == 1:
                self.table.start_middle_stack(top_solitaire)
                solitaire.remove_card()
                if self.do_print:
                    print('{} moved ace out from Solitaire'.format(self.name))
                self.check_solitaire_empty()
                any_aces = True

        if top_hand_card.value == 1:
            self.table.start_middle_stack(top_hand_card)
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
        self.starting_player = 0

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

        # Take turns making different players "start" on each Tick
        player_order = list(range(len(self.players)))
        player_list = player_order[self.starting_player:] + player_order[:self.starting_player]
        if self.starting_player == len(self.players) - 1:
            self.starting_player = 0
        else:
            self.starting_player = self.starting_player + 1

        for p in player_list:
            player = self.players[p]
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
            while game.timeout:  # keep playing rounds until games DOESN'T timeout
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
