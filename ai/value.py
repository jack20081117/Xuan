from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import *
from config import *

class Value():
    def __init__(self,inplane):
        self.model=Sequential()
        self.model.add(Conv2D(1,kernel_size=(1,1),padding='same',input_shape=(BOARD_LENGTH,BOARD_LENGTH,inplane),activation='relu'))
        self.model.add(Flatten())
        self.model.add(Dense(256,activation='relu'))
        self.model.add(Dense(1,activation='tanh'))
        self.model.compile(
            loss='mse',
            optimizer=Adam(learning_rate=float(CONFIG['ai'].get('LR',1e-4))),
            metrics=['accuracy']
        )