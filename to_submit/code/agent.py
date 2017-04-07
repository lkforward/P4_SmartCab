"""
[Obj]: updated from 'agent_v1.py'

Add condition check in learn() and createQ(): if the agent is learning or not. 
"""

import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

import numpy as np

## Define some decay functions for the epsilon factor:
def f1(eps):
    return eps - 0.0025 if eps > 0.0025 else 0.0


def f2(eps):
    return eps - 0.005 if eps > 0.005 else 0.0


def f3(eps):
    return eps * 0.25


def f4(eps):
    return eps * 0.50


def f5(eps):
    return eps * np.exp(-0.025)


class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5, \
                 optimized=True, eps_func=f1):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        # Add a parameter to instruct the training parameters
        self.optimized = optimized
        self.eps_func = eps_func

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.previous_state = None
        self.previous_action = None
        self.previous_reward = 0.0


    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        if testing: 
            self.epsilon = 0.0
            self.alpha = 0.0
        else:
            if self.optimized:
                self.epsilon = self.eps_func(self.epsilon)
                self.alpha = self.alpha - 0.0025 if self.alpha > 0.0025 else 0.0
            else:
                self.epsilon -= 0.05

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent

        # is_oncoming_left = (inputs['oncoming'] == 'left')
        # is_left_forward = (inputs['left'] == 'forward')
        # is_light_green = (inputs['light'] == 'green')
        #
        # state = (waypoint, is_light_green, is_oncoming_left, \
        #         is_left_forward)

        dir_oncoming = inputs['oncoming']
        dir_left = inputs['left']
        is_light_green = (inputs['light']=='green')
        state = (waypoint, is_light_green, dir_oncoming, dir_left)

        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
            
        maxQ = max(self.Q[state].values()) if state in self.Q else None

        return maxQ 


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
        
        if self.learning:
            if state not in self.Q:
                self.Q[state] = {None:0.0, 'forward':0.0, 'left':0.0, 'right':0.0}
                # self.Q[state] = {None:20.0, 'forward':20.0, 'left':20.0, 'right':20.0}

        return


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state

        if self.learning:
            tmp = random.uniform(0,1)
            if tmp < self.epsilon:
                action = random.choice(self.env.valid_actions)
            else:
                maxq = self.get_maxQ(state)

                if self.optimized:
                    action = random.choice([act for act, score in self.Q[state].iteritems() if score == maxq])
                else:
                    action = self.Q[state].keys()[self.Q[state].values().index(maxq)]

        else: 
            action = random.choice(self.env.valid_actions)
 
        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')

        if self.learning:
            if self.previous_state is not None:             
                self.Q[self.previous_state][self.previous_action] = \
                    (1 - self.alpha) * self.Q[self.previous_state][self.previous_action] + \
                    self.alpha * self.previous_reward
            
            self.previous_state = state
            self.previous_action = action
            self.previous_reward = reward
        
        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    is_optimized = True
    alpha_func = [f5]
    # safety = []
    # reliability = []
    # csv_filename = "sim_improved-learning.csv"

    for test_func in alpha_func:
        ##############
        # Create the environment
        # Flags:
        #   verbose     - set to True to display additional output from the simulation
        #   num_dummies - discrete number of dummy agents in the environment, default is 100
        #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
        env = Environment()

        # For an optimized learner:
        if is_optimized:

            ##############
            # Create the driving agent
            # Flags:
            #   learning   - set to True to force the driving agent to use Q-learning
            #    * epsilon - continuous value for the exploration factor, default is 1
            #    * alpha   - continuous value for the learning rate, default is 0.5

            #agent = env.create_agent(LearningAgent)
            agent = env.create_agent(LearningAgent, learning=True, optimized=True, \
                                     eps_func=test_func)

            ##############
            # Follow the driving agent
            # Flags:
            #   enforce_deadline - set to True to enforce a deadline metric

            #env.set_primary_agent(agent)
            env.set_primary_agent(agent, enforce_deadline=True)

            ##############
            # Create the simulation
            # Flags:
            #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
            #   display      - set to False to disable the GUI if PyGame is enabled
            #   log_metrics  - set to True to log trial and simulation results to /logs
            #   optimized    - set to True to change the default log file name

            #sim = Simulator(env)
            sim = Simulator(env, update_delay=0.01, log_metrics=True, optimized=True)

        # For a default learner:
        else:
            agent = env.create_agent(LearningAgent, learning=True, optimized=False)
            env.set_primary_agent(agent, enforce_deadline=True)
            sim = Simulator(env, update_delay=0.01, log_metrics=True, optimized=False)


        ##############
        # Run the simulator
        # Flags:
        #   tolerance  - epsilon tolerance before beginning testing, default is 0.05
        #   n_test     - discrete number of testing trials to perform, default is 0

        #sim.run()
        sim.run(n_test=10)


if __name__ == '__main__':
    run()
