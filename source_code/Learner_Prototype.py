from poker import *

class simpleLearnerPlayer(GenericPlayer):
    def policy():
        return 0
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        """
        This player is a very simple learner, it looks at the first two card and make the decision on
        whether to call, raise or fold based on the first two call. Player has 3 simple policies, fold, call and raise by 20.
        we selected the same betting amount as we had for always call and always raise players in order to be able to compare the results.
        Player starts learning by playing games, at first he randomly selects between different policy (fold, call and raise) and sotre the
        final results "game net change" as its rewards. As it play more hands it starts to build the intuition about which hands/strategy give him better results.
        Player going to store the first two cards as a dictionary with rankings and whether they are the same suit or not as Y/N (for example if player has king 
        daimond and 2 club the key for the dictionary will be K2N & 2KN, but if we had King club and 2 club then the key for dictionary will be 2KY & K2Y). Then we append 
        the value of "game net change" after each game into the list. 
        As player plays more hand it starts utilizing the "game net change" value for each pair for cards. for example if player recieves 2KY it looks at "game net change"
        value from previous plays and calculates the probability of playing by adding all the "game net change" values in the list for 2KY hand and then divide that by adding
        the absolute value of "game net change".
        we use uniform random number generator between 0 and 1 
        1- if random value is less than calculated probability player raise
        2- if random value is greater caluculated probability but less than calculated probability +0.2 player call
        3- if random value is less than calculated probability +0.2 player fold.

        in order to avoid early elimination of some cards, if calculated probability became negative we change that to 0.1  which means player may raise the hand with 10 percent chance or call the hand with 0.1+0.2=0.3 30%
        probability

        use make bet function as part of class.
        on the player make attribute of player call history.
        make preflop wins as dictionary.
        learn about getter and setter ( encapsolation), later.
        make the function for making it suitless. get the card and make it suitless.

        """
        print('______________________________________________________________________')
        print('______________________________________________________________________')
        
        
        if len(self.balance_history)==0:
            
            self.number_of_finished_games=0
        
        
        elif len(self.balance_history)>self.number_of_finished_games:
            number_of_game=len(self.balance_history)
            print('card1 is ',self.balance_history)
            #print('last_item is', self.balance_history[-1][-1])
            self.number_of_finished_games=len(self.balance_history)
            #print(self.number_of_finished_games)
        hand_rank=[x for x,y in hand]
        hand_suit=[y for x,y in hand]

        
        if hand_suit[0]==hand_suit[1]:
            same_suit='Y'
        else:
            same_suit='N'
        dictionary_key=[hand_rank[0]+hand_rank[1]+same_suit,hand_rank[1]+hand_rank[0]+same_suit]
        #using same probability to play for first hand
        #print('dictionary is ',self.hand_dictionary[dictionary_key[0]]['sum_absolute_bet'])
        print('river is ',river)
        if self.hand_dictionary[dictionary_key[0]]['sum_absolute_bet']==0:
            chance=random.random()
            if chance<0.33:
                self.fold_bet()
            elif chance>=0.33 and chance<0.66:
                self.call_bet()
            else:
                self.raise_bet(20)
        else:
            if self.hand_dictionary[0]['sum_bet']>0:
                self.raise_bet(round(100*self.hand_dictionary[0]['sum_bet']/self.hand_dictionary[0]['sum_absolute_bet'],0))
            else:
                if chance<0.2:
                    self.call_bet()
                else:
                    self.fold_bet()
        
        
        print('current pot is',pot)
        print(random.random())
        #print([x(card.rank) for x in hand])
        #sys.exit(0)

debug = 0 # to see detailed messages of simulation, put this to 1, think verbose mode
use_parallel = 0 # would not recommend using use_cache=1 on function simulate_win_odds due to not knowing if globals are thread or process safe.

# serial runs are guanteed unique repeatable results.  Parallel runs due to randomness of start times are not.  worth noting.

if __name__ == '__main__':
    print("starting poker simulation...(set debug=1 to see messages)")

    if debug == 1 and use_parallel == 1:
        raise Exception("Parallelism (use_parallel=1) is not supported with debug mode (debug=1)...set debug to 0")

    # defines all the simulations we will run
    simulations = {
       'tables': 1, # number of poker tables simulated
       'hands': 10, # number of hands the dealer will player, has to be greater than 2
       'balance': 100000, # beginning balance in dollars, recommend > 10,000 unless you want player to run out of money
       'minimum_balance': 50, # minimum balance to join a table
       'simulations': [ # each dict in the list is a simulation to run    
            {
                'simulation_name': 'smart vs 5 all different types player', # name of simulation - reference for data analytics
                'player_types': [ # type of players, see the subclasses of GenericPlayer
                    AlwaysCallPlayer, # defines strategy of player 1
                    AlwaysRaisePlayer, # defines strategy of player 2
                    #CalculatedPlayer, # defines strategy of player 3
                    #GambleByProbabilityPlayer, # defines strategy of player 4
                    #ConservativePlayer, # defines strategy of player 5
                    #SmartPlayer # defines strategy of player 6
                    #MonteCarloTreeSearchPlayer
                    simpleLearnerPlayer
                ]
            }    
        ]
    }

    random.seed(42) # gurantees standardized output for any given config

    run_all_simulations(simulations) # runs all the simulations in simulation variable
