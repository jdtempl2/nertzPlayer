from typing import List


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
