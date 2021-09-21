import numpy as np
import matplotlib.pyplot as plt
import itertools


class QAgent:
    def __init__(self, gamma=0.99, epsilon=0.05):
        self.gamma = gamma  # discount rate
        self.epsilon = epsilon  # exploration rate
        self.possible_actions = ["REQ_FOOD_TYPE", "CONF_FOOD_TYPE",
                                 "REQ_PRICE", "CONF_PRICE",
                                 "REQ_LOCATION", "CONF_LOCATION"]
        self.q_table = {}
        possible_states = list(itertools.product([0, 1], repeat=6))
        for ii in range(len(possible_states)):
            self.q_table[possible_states[ii]] = {}
            for a in range(6):
                self.q_table[possible_states[ii]][self.possible_actions[a]] = 0

    def chooseBestAction(self, current_state):
        if np.random.uniform(0, 1) < self.epsilon:
            action = np.random.choice(self.possible_actions)
        else:
            q_values_of_state = self.q_table[current_state]
            maxValue = max(q_values_of_state.values())
            action = np.random.choice([k for k, v in q_values_of_state.items() if v == maxValue])
        return action

    def learn(self, old_state, reward, new_state, action, alph):
        q_values_new_state = self.q_table[new_state]
        max_q_value_new_state = max(q_values_new_state.values())
        current_q_value = self.q_table[old_state][action]

        self.q_table[old_state][action] = (1 - alph) * current_q_value + alph * (
                    reward + self.gamma * max_q_value_new_state)

    def write_policy_to_file(self):
        f = open("policy.csv", 'w')
        policy = {}
        for key in self.q_table:
            s = ",".join(map(str, key))
            q_values_of_state = self.q_table[key]
            maxValue = max(q_values_of_state.values())
            action = np.random.choice([k for k, v in q_values_of_state.items() if v == maxValue])
            policy[s] = action
            f.write("%s,%s\n"% (s, action))

        f.close()


class simUser:
    def __init__(self, food_type, price, location):
        self.food_type = food_type
        self.price = price
        self.location = location

    def getAnswer(self, question):
        if question=="REQ_FOOD_TYPE":
            return np.random.choice([self.food_type, "IRRELEVANT"], p=[0.7, 0.3])
        if question=="REQ_PRICE":
            return np.random.choice([self.price, "IRRELEVANT"], p=[0.7, 0.3])
        if question=="REQ_LOCATION":
            return np.random.choice([self.location, "IRRELEVANT"], p=[0.7, 0.3])
        if "CONF" in question.split('_'):
            return np.random.choice(["yes", "no", "IRRELEVANT"], p=[0.4, 0.4, 0.2])

        return "Failed to pick question....!!"


class DialogueManager:
    def __init__(self):
        self.state = [0]*6
        self.slots = {"FOOD_TYPE": '', "CONF_FOOD_TYPE": 0,
                      "PRICE": '', "CONF_PRICE": 0,
                      "LOCATION": '', "CONF_LOCATION": 0}
        self.actions_sentence = {"REQ_FOOD_TYPE": "What kind of food would you like?",
                                 "CONF_FOOD_TYPE": "You said ",
                                 "REQ_PRICE": "How expensive a restaurant do you want?",
                                 "CONF_PRICE": "You said ",
                                 "REQ_LOCATION": "Where would you like the restaurant to be?",
                                 "CONF_LOCATION": "You said "}
        self.food_options = ["Indian"]
        self.price_options = ["Medium"]
        self.location_options = ["Palms"]

    def reset(self):
        self.state = [0] * 6
        self.slots = {"FOOD_TYPE": '', "CONF_FOOD_TYPE": 0,
                      "PRICE": '', "CONF_PRICE": 0,
                      "LOCATION": '', "CONF_LOCATION": 0}

    def getCurrentState(self):
        return tuple(self.state)

    def getQuestion(self, action):
        if action == "REQ_FOOD_TYPE" or "REQ_PRICE" or "REQ_LOCATION":
            return self.actions_sentence[action]

        if action == "CONF_FOOD_TYPE":
            if self.state[0]:
                return self.actions_sentence[action] + self.slots["FOOD_TYPE"] + ", right?"
            else:
                return self.actions_sentence[action] + "..., right?"
        if action == "CONF_PRICE":
            if self.state[1]:
                return self.actions_sentence[action] + self.slots["PRICE"] + ", right?"
            else:
                return self.actions_sentence[action] + "..., right?"
        if action == "CONF_LOCATION":
            if self.state[2]:
                return self.actions_sentence[action] + self.slots["LOCATION"] + ", right?"
            else:
                return self.actions_sentence[action] + "..., right?"

    def evalAnswer(self, action_from_system, response_from_user):
        """
        Evaluates the user response to update state

        :param question: string
        :param answer: string
        :return: None
        """
        if action_from_system == "REQ_FOOD_TYPE":
            for ii in self.food_options:
                if ii in response_from_user:
                    self.state[0] = 1
                    self.slots["FOOD_TYPE"] = ii

        if action_from_system == "REQ_PRICE":
            for ii in self.price_options:
                if ii in response_from_user:
                    self.state[1] = 1
                    self.slots["PRICE"] = ii

        if action_from_system == "REQ_LOCATION":
            for ii in self.location_options:
                if ii in response_from_user:
                    self.state[2] = 1
                    self.slots["LOCATION"] = ii

        if action_from_system == "CONF_FOOD_TYPE":
            if self.state[0] == 1:
                if "yes" in response_from_user.split():
                    self.state[3] = 1
                    self.slots["CONF_FOOD_TYPE"] = 1
                if "no" in response_from_user.split():
                    self.state[0] = 0
                    self.slots["FOOD_TYPE"] = ''

                    self.state[3] = 0
                    self.slots["CONF_FOOD_TYPE"] = 0

        if action_from_system == "CONF_PRICE":
            if self.state[1] == 1:
                if "yes" in response_from_user.split():
                    self.state[4] = 1
                    self.slots["CONF_PRICE"] = 1
                if "no" in response_from_user.split():
                    # print(self.state)
                    self.state[1] = 0
                    self.slots["PRICE"] = ''

                    self.state[4] = 0
                    self.slots["CONF_PRICE"] = 0
                    # print(self.state)

        if action_from_system == "CONF_LOCATION":
            if self.state[2] == 1:
                if "yes" in response_from_user.split():
                    self.state[5] = 1
                    self.slots["CONF_LOCATION"] = 1
                if "no" in response_from_user.split():
                    # print(self.state)
                    self.state[2] = 0
                    self.slots["LOCATION"] = ''

                    self.state[5] = 0
                    self.slots["CONF_LOCATION"] = 0
                    # print(self.state)

    def getReward(self):
        """
        Large positive reward if dialogue ended with all states filled.
        Small negative reward per question.
        :return: reward
        """
        if np.sum(self.state) == 6:
            return 495, True
        return -5, False


def train(nEpisodes):
    smartAgent = QAgent()
    randomAgent = simUser("Indian", "Medium", "Palms")
    system = DialogueManager()

    f = open("rewards.csv", 'w')
    f.write("CURRENT_EPISODE_NUMBER,TOTAL_REWARD_AT_END_OF_THIS_EPISODE\n")
    reward_per_episode = [0] * nEpisodes

    for ii in range(nEpisodes):
        alph = 1/(1+ii)
        total_reward = 0
        system.reset()
        isTerminal = False
        while not isTerminal:
            current_state = system.getCurrentState()
            action = smartAgent.chooseBestAction(current_state)

            question = system.getQuestion(action)
            answer = randomAgent.getAnswer(action)

            # if ii==nEpisodes-1:
            #     print("Before eval: ", system.getCurrentState())
            #     print("%s: %s" %(action, answer))
            system.evalAnswer(action, answer)
            # if ii==nEpisodes-1:
            #     print("After eval: ", system.getCurrentState())
            #     print("\n")

            reward, isTerminal = system.getReward()
            total_reward += reward

            new_state = system.getCurrentState()
            smartAgent.learn(current_state, reward, new_state, action, alph)

        reward_per_episode[ii] = total_reward
        f.write("%d,%d \n" % (ii, reward_per_episode[ii]))

    f.close()
    # Write policy to file
    smartAgent.write_policy_to_file()

    # print(np.amax(reward_per_episode))
    # plt.plot(reward_per_episode)
    # plt.show()

if __name__=="__main__":
    nEpisodes = 1000

    err1_count = 0
    err2_count = 0
    for kk in range(100):
        np.random.seed(kk)
        train(nEpisodes)

        f = open("policy.csv", 'r')
        lines = f.readlines()
        if "CONF" in lines[18].split(',')[-1].strip('\n'):
            err1_count += 1
            # print(lines[18])
        if "CONF" in lines[36].split(',')[-1].strip('\n'):
            err2_count += 1
            # print(lines[36])

        f.close()

    print("err1 = %d, err2 = %d" %(err1_count, err2_count))
