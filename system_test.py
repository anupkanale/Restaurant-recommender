import numpy as np


class Agent:
    def __init__(self, food_options, price_options, location_options):
        self.actions_sentence = {"REQ_FOOD_TYPE": "What kind of food would you like?",
                                 "CONF_FOOD_TYPE": "You said ",
                                 "REQ_PRICE": "How expensive a restaurant do you want?",
                                 "CONF_PRICE": "You said ",
                                 "REQ_LOCATION": "Where would you like the restaurant to be?",
                                 "CONF_LOCATION": " location is ok"}
        self.slots = {"FOOD_TYPE": '', "CONF_FOOD_TYPE": 0,
                      "PRICE": '', "CONF_PRICE": 0,
                      "LOCATION": '', "CONF_LOCATION": 0}
        self.food_options = food_options
        self.price_options = price_options
        self.location_options = location_options

        self.policy = {}
        f = open("policy.csv", 'r')
        lines = f.readlines()
        for line in lines:
            lineList = line.split(',')
            state = [int(val) for val in lineList[0:6]]
            action = lineList[-1].strip('\n')

            self.policy[tuple(state)] = action

    def get_slots(self):
        return self.slots

    def get_action(self, curr_state):
        return self.policy[tuple(curr_state)]

    def get_question(self, action):
        if action=="REQ_FOOD_TYPE" or action=="REQ_PRICE" or action=="REQ_LOCATION":
            q = self.actions_sentence[action]
        elif action=="CONF_FOOD_TYPE":
            q = self.actions_sentence[action] + self.slots["FOOD_TYPE"] + " cuisine, right?"
        elif action=="CONF_PRICE":
            q = self.actions_sentence[action] + self.slots["PRICE"] + " price, right?"
        elif action=="CONF_LOCATION":
            q = self.slots["LOCATION"] + self.actions_sentence[action] + ", right?"

        return q

    def eval_answer(self, curr_state, action_from_system, response_from_user):
        # replace punctuations
        split_response = response_from_user.replace(',', ' ')
        split_response = split_response.replace('?', ' ')
        split_response = split_response.replace('.', ' ')

        # Split into list of words to look for keyword
        split_response = split_response.lower()

        if action_from_system=="REQ_FOOD_TYPE":
            split_response = split_response.split()
            for val in self.food_options:
                if val in split_response:
                    curr_state[0] = 1
                    self.slots["FOOD_TYPE"] = val

        if action_from_system=="REQ_PRICE":
            split_response = split_response.split()
            for val in self.price_options:
                if val in split_response:
                    curr_state[1] = 1
                    self.slots["PRICE"] = val

            # SPECIAL CASE
            if "medium" in split_response:
                index = split_response.index("medium")
                if index!=len(split_response)-1:
                    if split_response[index+1]=="priced" or split_response[index+1]=="price":
                        curr_state[1] = 1
                        self.slots["PRICE"] = "medium-priced"

        if action_from_system=="REQ_LOCATION":
            for val in self.location_options:
                if val in split_response:
                    curr_state[2] = 1
                    self.slots["LOCATION"] = val

        if action_from_system=="CONF_FOOD_TYPE":
            if "yes" in split_response:
                curr_state[3] = 1
                self.slots["CONF_FOOD_TYPE"] = 1
            if "no" in split_response:
                curr_state[0] = 0
                self.slots["FOOD_TYPE"] = ''

                curr_state[3] = 0
                self.slots["CONF_FOOD_TYPE"] = 0

        if action_from_system=="CONF_PRICE":
            if "yes" in split_response:
                curr_state[4] = 1
                self.slots["CONF_PRICE"] = 1
            if "no" in split_response:
                curr_state[1] = 0
                self.slots["PRICE"] = ''

                curr_state[4] = 0
                self.slots["CONF_PRICE"] = 0

        if action_from_system=="CONF_LOCATION":
            if "yes" in split_response:
                curr_state[5] = 1
                self.slots["CONF_LOCATION"] = 1
            if "no" in split_response:
                curr_state[2] = 0
                self.slots["LOCATION"] = ''

                curr_state[5] = 0
                self.slots["CONF_LOCATION"] = 0

        return curr_state


def recommend_restaurant(ag):
    curr_state = [0] * 6
    while np.sum(curr_state) != 6:
        action = ag.get_action(curr_state)
        question = ag.get_question(action)
        print("%s" % question)
        # print(curr_state)
        answer = input()
        new_state = ag.eval_answer(curr_state, action, answer)
        # print(curr_state)
        curr_state = new_state

    slots = ag.get_slots()
    specs = [slots['FOOD_TYPE'], slots['PRICE'], slots['LOCATION']]
    print("So you want %s food, %s price at %s location.\n" %(specs[0], specs[1], specs[2]))

    restaurantList = []
    f = open('restaurantDatabase.txt', 'r')
    lines = f.readlines()
    f.close()
    for line in lines[1:]:
        lineList = line.split('\t')
        cuisine = lineList[2].lower()
        price = lineList[3].lower()
        location = lineList[-1].strip('\n').lower()
        if (specs[0]==cuisine or specs[0]=='any') and\
                (specs[1]==price or specs[1]=="any") and\
                (specs[2]==location or specs[2]=="any"):
            restaurantList.append(lineList)

    if len(restaurantList)==0:
        print("Sorry, I found no restaurants in the database matching your requirements!")
    else:
        for ii in range(len(restaurantList)):
            print("-- %s is a %s %s restaurant in %s. The telephone number is %s." %
                  (restaurantList[ii][0], restaurantList[ii][3],
                   restaurantList[ii][2], restaurantList[ii][4],
                   restaurantList[ii][1]))


if __name__=="__main__":

    # Read and store list of valid user responses for Slots
    food_options = ["any"]
    price_options = ["any"]
    location_options = ["any"]
    f = open('restaurantDatabase.txt', 'r')
    lines = f.readlines()
    numLines = len(lines)
    f.close()
    for line in lines[1:numLines]:
        lineList = line.split('\t')
        food_options.append(lineList[2].lower())
        price_options.append(lineList[3].lower())
        if lineList[-1].strip('\n').lower()!='':
            location_options.append(lineList[-1].strip('\n').lower())

    food_options = list(set(food_options))
    price_options = list(set(price_options))
    location_options = list(set(location_options))

    # Start interaction with user
    anotherTurn = "y"
    while anotherTurn=="y":
        ag = Agent(food_options, price_options, location_options)
        recommend_restaurant(ag)

        print("\nWould you like to find another restaurant? (y/n)")
        anotherTurn = input()

    print("Okay, have a great day! :)")
