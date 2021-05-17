# Simulation Project - Georgia Tech

## High Level Overview
We developed a poker simulation system.  The idea was to allow us to rapidly prototype different poker strategies and try them out.  It's easy to use.  You just execute the poker.py file using python.

```
python poker.py
```

we tried to keep it simple to make grading easier.  You can modify the poker simulation via a variable in the script.  An example below:

```python
    simulations = {
       'tables': 10, # number of poker tables simulated
       'hands': 50, # number of hands the dealer will player, has to be greater than 2
       'balance': 100000, # beginning balance in dollars, recommend > 10,000 unless you want player to run out of money
       'minimum_balance': 50, # minimum balance to join a table
       'simulations': [ # each dict in the list is a simulation to run    
            {
                'simulation_name': 'monte vs 1 all different types player', # name of simulation - reference for data analytics
                'player_types': [ # type of players, see the subclasses of GenericPlayer
                    #AlwaysCallPlayer, # defines strategy of player 1
                    AlwaysRaisePlayer,
                    MonteCarloTreeSearchPlayer

                ]
            },
            {
                'simulation_name': 'smart vs 1 all different types player', # name of simulation - reference for data analytics
                'player_types': [ # type of players, see the subclasses of GenericPlayer
                    AlwaysCallPlayer, # defines strategy of player 1
                    SmartPlayer,
                    AwareLearnerPlayer
                ]
            }           
        ]
    }    simulations = {
       'tables': 10, # number of poker tables simulated
       'hands': 50, # number of hands the dealer will player, has to be greater than 2
       'balance': 100000, # beginning balance in dollars, recommend > 10,000 unless you want player to run out of money
       'minimum_balance': 50, # minimum balance to join a table
       'simulations': [ # each dict in the list is a simulation to run    
            {
                'simulation_name': 'monte vs 1 all different types player', # name of simulation - reference for data analytics
                'player_types': [ # type of players, see the subclasses of GenericPlayer
                    #AlwaysCallPlayer, # defines strategy of player 1
                    AlwaysRaisePlayer,
                    MonteCarloTreeSearchPlayer

                ]
            },
            {
                'simulation_name': 'smart vs 1 all different types player', # name of simulation - reference for data analytics
                'player_types': [ # type of players, see the subclasses of GenericPlayer
                    AlwaysCallPlayer, # defines strategy of player 1
                    SmartPlayer,
                    AwareLearnerPlayer
                ]
            }           
        ]
    }
```

In the above, you have a few variables you can modify:

1. tables - the number of tables to play for each simulation.  You can think of this as independent replications.
2. hands - the number of hands to play at each table.  Once all hands are played a table ends and the data is written to the data directory.
3. balance - the balance of the poker player
4. minimum balance - minimum balance needed to play poker.
5. simulations - a list of simulations to run.  Each simulation has a user-friendly simulation_name and player_types list, which defines the players and what strategies they use. 

Strategies are easy to define, you just inherit from GenericPlayer and implement a bet strategy.  The list is the class name, not an instance of the class:

```python
# Player that always calls
class AlwaysCallPlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        self.call_bet()
        return None

# Player that always raises
class AlwaysRaisePlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        self.raise_bet(20)
        return None
```

Two examples above.  You have a player that always calls and a player that always bets.  Each strategy needs to call self.raise_bet, self.call_bet or self.fold_bet once and only once.  The bet_strategy parameters need to be implemented for the method.  You can't miss a parameter.  Everything else is up to the person designing the player.  They can get very complex.  See AlwaysAwarePlayer and MonteCarloTreeSearchPlayer to see some cool ones.

We implemented a ton of player types, the below are all the ones we tried out:

1. AlwaysCallPlayer - always calls no matter what.
2. AlwaysRaisePlayer - always raises $20.00 no matter what.
3. CalculatedPlayer - if win chance is better than random selection call the bet.
4. GambleByProbabilityPlayer - if win chance is better than random than bet the win percent * $100.
5. ConservativePlayer - bets a percent of his balance based on a switch statement.  Generally only bets on the best hands.
6. SmartPlayer - player that does a 100 simulation of his current hand and bets up to $100.00 based on his chance of winning.
7. simpleLearnerPlayer - player that checks his win probability for each given pre-flop hand and makes bets on it.
8. AwareLearnerPlayer - player that uses reinforcement learning concepts to predict his opponents behavior and updates his win chance based on that.
9. MonteCarloTreeSearchPlayer - player that builds a monte carlo tree search algorithm and makes decisions on it.  Monte Carlo Tree Search algorithm is simplified due to time constraints.

You can see the results of our work in 2 papers: 

1. paper1.pdf - covers developing our simulation framework
2. paper2.pdf - covers developing reinforcement learning and monte carlo tree search player types using the 1st paper.

Around 70 pages combined.  Feel like warning people just in case.  The results were kind of fun in that we got to explore the percent chance for pre-flops and see how different strategies worked out.

By Chris Kottmyer and Shahin Shirazi
