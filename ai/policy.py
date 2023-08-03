from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import *
from config import *

class Policy():
    def __init__(self,inplane,outplane):
        self.model=Sequential()
        self.model.add(Conv2D(1,kernel_size=(3,3),padding='same',input_shape=(BOARD_LENGTH,BOARD_LENGTH,inplane),activation='relu'))
        self.model.add(BatchNormalization())
        self.model.add(Flatten())
        self.model.add(Dense(outplane))
        self.model.add(Dense(outplane,activation='softmax'))
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=Adam(learning_rate=float(CONFIG['ai'].get('LR',1e-4))),
            metrics=['accuracy']
        )