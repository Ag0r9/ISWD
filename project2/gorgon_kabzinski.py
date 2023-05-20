### Implement player's strategy. You can compare it with random player
### (or some strategy implemented by one of you colleagues)
### Time limit per decision 0.01s !!!
class Player():
    def __init__(self, name):
        self.name = name
        self.cards = None

    def putCard(self, declared_card):
        return self.cards[0], self.cards[0]

    def checkCard(self, opponent_declaration):
        pass

    def getCheckFeedback(self, checked, iChecked, iDrewCards, revealedCard, noTakenCards, log=True):
        if log: print("Feedback = " + self.name + " : checked this turn = " + str(checked) +
                      "; I checked = " + str(iChecked) + "; I drew cards = " +
                      str(iDrewCards) + "; revealed card = " +
                      str(revealedCard) + "; number of taken cards = " + str(noTakenCards))

    def startGame(self, cards):
        self.cards = cards

    def takeCards(self, cards_to_take):
        self.cards = self.cards + cards_to_take


class Gorgon_kabzinski(Player):
    def __init__(self, name):
        super().__init__(name)
        self.last_card = None

    def putCard(self, declared_card):

        if len(self.cards) == 1 and declared_card is not None and self.cards[0][0] < declared_card[0]:
            return "draw"

        card = min(self.cards, key=lambda x: x[0])
        declaration = (card[0], card[1])
        if declared_card is not None:
            min_val = declared_card[0]
            if card[0] < min_val:
                declaration = (min(min_val + 1, 14), declaration[1])
                declaration = self.pick_your_card(declaration)
        return card, declaration

    def checkCard(self, opponent_declaration):
        if opponent_declaration in self.cards: return True
        if self.last_card and (self.last_card[0] > opponent_declaration[0] + 1): return True
        return False

    def pick_your_card(self, declaration):
        for chosen_card in self.cards:
            if chosen_card[0] in (declaration[0], declaration[0] + 1):
                return chosen_card
        return declaration
