from pprint import pprint
import itertools
from collections import defaultdict
from decimal import Decimal


def logit(p):
    """Log-odds of the probability."""
    return (p / (1-p)).ln()

def inv_logit(x):
    return 1 / (1 + (-x).exp())


class Bet:
    def __init__(self, name, amount, probability):
        """
        name: Bettor's name.
        amount: Dollar amount of the bet.
        probability: Predicted probability of the event.
        """
        self.name = str(name)
        self.amount = Decimal(amount)
        assert self.amount >= 0
        self.p = Decimal(probability)
        assert 0 < self.p < 1

        self.prev = None

    def log_odds(self):
        return logit(self.p)

    def force(self):
        return self.amount * self.log_odds()

    def points_if_yes(self):
        if self.prev is None:
            return 0
        return (self.p / self.prev.p).ln()

    def points_if_no(self):
        if self.prev is None:
            return 0
        return ((1-self.p) / (1-self.prev.p)).ln()

    def ratio(self):
        if self.prev is None:
            return 0

        if_yes = self.points_if_yes()
        if_no = self.points_if_no()
        downside = min(if_yes, if_no)
        upside = max(if_yes, if_no)
        assert upside > 0
        assert downside < 0
        return upside / -downside

    def payoff(self):
        return self.ratio() * self.amount


header = (
    'Name     '
    'Amount    '
    'Prob  '
    'LogOdds    '
    'Force    '
    'IfYes     '
    'IfNo   '
    'Ratio  '
    'Payoff '
    'MarketSize '
    'TotalForce '
    'MarketProb'
)
fmt = (
    '{:<6} '  # name
    '{:>8} '  # amount
    '{: >6.1f}% '  # probability
    '{:>+8.2f} '  # log odds
    '{:>+8.2f} '  # force
    '{:>+8.3f} '  # if_yes
    '{:>+8.3f} '  # if_no
    '{:>7.2f} '  # ratio
    '{:>7} '  # payoff
    '{:>10} '  # market_size
    '{:>+10.2f} '  # total_force
    '{: >9.1f}%'  # market_probability
)

def run_market(bets):
    print(header)

    payoffs_if_yes = defaultdict(Decimal)
    payoffs_if_no = defaultdict(Decimal)

    for b1, b2 in pairwise(bets):
        b2.prev = b1

    market_size = 0  # Total amount of all bets.
    total_force = 0  # Total log odds, scaled by dollar amount.
    for b in bets:
        market_size += b.amount
        total_force += b.force()
        if market_size == 0:
            market_probability = 0.5
        else:
            market_probability = inv_logit(total_force / market_size)

        if_yes = b.points_if_yes()
        if_no = b.points_if_no()
        ratio = b.ratio()
        payoff = b.payoff()

        # If your bet fails, the most you can lose is the entire bet.
        if b.prev is not None:
            if b.p > b.prev.p:  # Bet increases probability.
                payoffs_if_yes[b.name] += payoff
                payoffs_if_no[b.name] += -b.amount
            else:  # Bet decreases probability.
                payoffs_if_yes[b.name] += -b.amount
                payoffs_if_no[b.name] += payoff

        print(fmt.format(
            b.name,
            '${:,.0f}'.format(b.amount),
            100*b.p,
            b.log_odds(),
            b.force(),
            if_yes,
            if_no,
            ratio,
            '${:,.2f}'.format(payoff),
            '${:,.0f}'.format(market_size),
            total_force,
            100*market_probability,
        ))

    market_maker = bets[0].name
    payoffs_if_yes[market_maker] = -sum(payoffs_if_yes.values())
    payoffs_if_no[market_maker] = -sum(payoffs_if_no.values())

    print('If Yes:')
    pprint({ name: float(payoff) for (name, payoff) in payoffs_if_yes.items()})
    print('If No:')
    pprint({ name: float(payoff) for (name, payoff) in payoffs_if_no.items()})


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ...

    >>> list(pairwise([1, 2, 3, 4]))
    [(1, 2), (2, 3), (3, 4)]
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)



bets = [
    Bet('SD', 5, .7),
    Bet('CO', 1, .75),
    Bet('XCO', 1, .6533),
    Bet('XSD', 5, .3),
    Bet('XX', 20, .01),
    Bet('CO', 1, .75),
    # Bet('ZZ', 2, '0.999999999999999999999'),
]

run_market(bets)



