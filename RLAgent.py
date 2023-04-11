import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import random


class RLAgent:
    def __init__(self):
        self.state_size = 4
        self.action_size = 2
        self.memory = []
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def update_target_model(self):
        # copy weights from model to target_model
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def next_move(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values)  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            # using reward + gamma * max Q(s',a') to update the Q value
            # Q(s,a) = r + gamma * max Q(s',a')
            print("next state: ", next_state)
            print("state: ", state)
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.target_model.predict(next_state)))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

    ## implement the q learning algorithm using the bellman equation
    def q_learning(self, batch_size, player):
        player.look_around()  # np.reshape(player.look_around(), [1, self.state_size])
        state = player.sight
        for time in range(500):
            action = self.next_move(state)
            player.flap()
            next_state = player.sight
            done = player.check_crash()
            reward = 1 if not done else -10
            # next_state = np.reshape(next_state, [1, self.state_size])
            self.remember(state, action, reward, next_state, done)
            state = next_state
            if done:
                print(f"episode: {time}/{self.epsilon}, score: {player.score}, e: {self.epsilon}")
                break
        if len(self.memory) > batch_size:
            self.replay(batch_size)
