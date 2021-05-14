# PokerPro - Poker simulation software 
# Simulations - Georgia Tech Grad School Project 

## High Level Overview

poker.py is a poker simulator that allows you to quickly define strategies via a Python class that inherits from GenericPlayer and use it in simulations by adding it to the simulations variable, which is a nested dictionary of parameters used by the simulator.  poker.py was set up as a single file with no parameters to make it easy to run for teacher assistants in the program.  We thought of potentially modularizing this system, but felt it would make grading complicated.  The simulation variable contains global parameters for: number of tables, number of hands, beginning player balances and minimum game balance to play.  It also contains a list of simulations to run including a generic human name to identify that specific simulation and a list of players to use in the simulation.  Players are defined as a class that inherits from GenericPlayer and implements the bet_strategy method calls only one of these 3 methods within the bet strategy method: raise_bet, call_bet or fold_bet.  The implementation includes a multi-processing pool to speed things up, though I didn't have enough time to properly implement interrupts.  We implemented a bunch of sample players:

AlwaysCallPlayer -> always calls no matter what
AlwaysRaisePlayer -> always raise 20 no matter what
CalculatedPLayer -> if chance of winning is greater than random call else fold
GambleByProbabilityPlayer -> if chance of winning is greater than random than bet 100 * probability chance else fold.
ConservativePlayer -> bets. a percent of current based on win probabilities with cut-offs being 50% - 70% -  90% - 95% - 99%.
SmartPlayer -> does a quick simulation of 100 games with current hand, calls if profit is greater than $0 and faises if bet is higher than random chance.
simpleLearnerPlayer -> Player that learns from it's past behavior by maintaining state.
AwarePlayer -> Player that learns from it's past behavior and adjusts based on the opponent actions.  Good example of a model that learns from it's opponent.
MonteCarloTreePlayer -> player that builds a monte carlo search tree and than uses it to make decisions.  Doesn't perform as well as AwarePlayer.

We built this as a prototype for a class project.  We discovered some minor bugs: 1. we player 3 rounds of poker and only check if during a round all 3 players checked or folded to move to the next betting round.  Technically, it should check after each players turn not after all players have made a turn.  2. We didn't get around to writing a check that gurantees only 1 of: raise_bet, call_bet or fold_bet were used during a bet_strategy call.  We decided to focus on building players instead of fixing the above bugs to make sure we hit the deadline, but it would be worth fixing those for the future.  Fixing 1st bug necessitates the monte carlo tree search being adjusted since it's currently using the bugged logic for it's code.

By Chris Kottmyer and Shahin Shirazi
