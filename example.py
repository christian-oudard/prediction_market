from prediction_market import PredictionMarket

market = PredictionMarket('SD', 'I go to bed by 10:30 pm.', 0.70, 5)
market.bet_dollars_yes('CO', 1)
market.bet_probability('YY', 0.83)
market.bet_probability('HH', 0.50)
market.bet_dollars_no('XX', 20)
market.bet_probability('ZZ', 0.9999)

market.show()
