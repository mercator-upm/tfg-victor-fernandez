import os, shutil
import numpy as np
import tensorflow as tf
base_dir = 'tiles'

train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')

#-----------#
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)

#-----------#
import keras
from keras import layers
from keras import models
from keras.applications import VGG16
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator

img_width, img_height = 1024, 1024
conv_base= VGG16(weights=None, include_top=False, input_shape=(img_width,img_height,3))

model = models.Sequential()
model.add(conv_base)
model.add(layers.MaxPooling2D(pool_size=(2,2),strides=(2,2)))
model.add(layers.Flatten())
model.add(layers.Dense(units=2048,activation="relu")) #si no entrena bien: init = 'he_normal'    #he_uniform
model.add(layers.Dense(units=2048,activation="relu"))
model.add(layers.Dense(units=1, activation="sigmoid"))

model.summary()
#-----------#
from keras import optimizers

model.compile(loss='binary_crossentropy', optimizer=optimizers.Adam(lr=5e-5), metrics=['acc']) #si es demasiado lento, Adam(lr=0.001)
#-----------#
from keras.preprocessing.image import ImageDataGenerator
datagen = ImageDataGenerator(rescale=1. /255)
train_datagen = ImageDataGenerator(rescale=1. / 255, rotation_range=25, 
                                   width_shift_range=0.1, height_shift_range=0.1, 
                                   zoom_range=0.1, horizontal_flip=True, vertical_flip=True, 
                                   fill_mode='nearest')

train_generator = train_datagen.flow_from_directory(train_dir, target_size=(1024, 1024),
                                                    batch_size=5, class_mode='binary')
validation_datagen = ImageDataGenerator(rescale=1. / 255)
validation_generator = validation_datagen.flow_from_directory(validation_dir, target_size=(1024, 1024), 
                                                              batch_size=5,class_mode='binary')
#-----------#
train_steps_per_epoch = np.math.ceil(train_generator.samples / train_generator.batch_size)
validation_steps_per_epoch = np.math.ceil(validation_generator.samples / validation_generator.batch_size)

#teniendo en cuenta el desbalanceo de clases
from sklearn.utils import class_weight
class_weights = class_weight.compute_class_weight('balanced',np.unique(train_generator.classes), train_generator.classes)
class_weights
#-----------#
history = model.fit_generator(train_generator, steps_per_epoch= train_steps_per_epoch, 
                              epochs=10, validation_data=validation_generator,
                              validation_steps=validation_steps_per_epoch, class_weight=class_weights) #callbacks = [tensorboard]

#-----------#
#model.save("Models1/vgg16_noweights-1.h5")
model.save("Models1/vgg16_noweights-1.h5")
