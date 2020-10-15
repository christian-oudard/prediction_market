from decimal import Decimal


class Bet:
    def __init__(self, name, probability):
        """
        name: Bettor's name.
        probability: Predicted probability of the event.
        """
        self.name = str(name)
        self.p = Decimal(probability).quantize(Decimal('.0001'))
        assert 0 < self.p < 1


class PredictionMarket:

    def __init__(self, market_maker, proposition, initial_probability, endowment):
        self.market_maker = market_maker
        self.proposition = proposition

        self.endowment = Decimal(endowment)
        mm = Bet(market_maker, initial_probability)
        self.bets = [mm]

        # Determine a scale that does not lose more money than the endowment.
        # -endowment < payoff_yes < 0
        # -endowment < payoff_no < 0
        # -payoff_yes = scale * log(mm.p) - scale * log(99.99%)
        # -payoff_no = scale * log(1-mm.p) - scale * log(1 - 0.01%)
        # In both formulas, log(100%) = 0.
        # -payoff_yes = scale * log(mm.p)
        # -payoff_no = scale * log(1-mm.p)
        # -payoff_yes / log(mm.p) = scale
        # -payoff_no / log(1-mm.p) = scale
        scale_yes = -endowment / mm.p.ln()
        scale_no = -endowment / (1-mm.p).ln()
        self.scale = min(scale_yes, scale_no)

    def score(self, p):
        return self.scale * p.ln()

    def inv_score(self, amount):
        return (amount / self.scale).exp()

    def update_market_maker(self, bet):
        mm = self.bets[0]
        mm.payoff_if_yes = self.score(mm.p) - self.score(bet.p)
        mm.payoff_if_no = self.score(1-mm.p) - self.score(1-bet.p)

    def bet_probability(self, name, probability):
        prev = self.bets[-1]
        b = Bet(name, probability)
        b.payoff_if_yes = self.score(b.p) - self.score(prev.p)
        b.payoff_if_no = self.score(1-b.p) - self.score(1-prev.p)
        self.bets.append(b)

        self.update_market_maker(b)

    def bet_dollars_yes(self, name, amount):
        prev = self.bets[-1]

        # Find the probability which, if the market goes to "no", loses exactly the desired amount.
        # -amount < b.payoff_if_no < 0
        # b.payoff_if_no = self.score(1-b.p) - self.score(1-prev.p)
        # self.inv_score(b.payoff_if_no + self.score(1-prev.p)) = 1 - b.p
        # b.p = 1 - self.inv_score(b.payoff_if_no + self.score(1-prev.p))
        p = 1 - self.inv_score(-amount + self.score(1-prev.p))
        self.bet_probability(name, p)

    def bet_dollars_no(self, name, amount):
        prev = self.bets[-1]

        # Find the probability which, if the market goes to "yes", loses exactly the desired amount.
        # -amount < b.payoff_if_no < 0
        # b.payoff_if_yes = self.score(b.p) - self.score(prev.p)
        # b.payoff_if_yes + self.score(prev.p) = self.score(b.p)
        # self.inv_score(b.payoff_if_yes + self.score(prev.p)) = b.p
        p = self.inv_score(-amount + self.score(prev.p))
        self.bet_probability(name, p)

    def show(self):
        header = (
            'Name      '
            'Prob    '
            'IfYes     '
            'IfNo   '
        )
        fmt = (
            '{:<6} '  # name
            '{: >6.2f}% '  # probability
            '{:>8} '  # if_yes
            '{:>8} '  # if_no
        )

        # Show market outcome.
        print(header)
        for b in self.bets:
            print(fmt.format(
                b.name,
                100*b.p,
                '${:,.2f}'.format(b.payoff_if_yes),
                '${:,.2f}'.format(b.payoff_if_no),
            ))


market = PredictionMarket('SD', 'I go to bed by 10:30 pm.', 0.70, 5)
market.bet_dollars_yes('CO', 1)
# market.bet_probability('YY', 0.83)
# market.bet_probability('HH', 0.50)
# market.bet_dollars_no('XX', 20)
# market.bet_probability('ZZ', 0.9999)

market.show()
