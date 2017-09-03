from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
import image_tools
from scipy import misc
import os
import logger

def create_model(input_shape):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=input_shape))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(128, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(256, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(512, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.1))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))
    return model

#binary_crossentropy
def TrainNN(train_data_dir, validation_data_dir,  model_name, img_width = 150, img_height = 150,nb_train_samples = 1000,nb_validation_samples = 300,
 epochs = 35,batch_size = 10):
    img_width, img_height = img_width, img_height
    train_data_dir = train_data_dir
    validation_data_dir = validation_data_dir
    nb_train_samples = nb_train_samples
    nb_validation_samples = nb_validation_samples
    epochs = epochs
    batch_size = batch_size

    if K.image_data_format() == 'channels_first':
        input_shape = (3, img_width, img_height)
    else:
        input_shape = (img_width, img_height, 3)

    model = create_model(input_shape = input_shape)

    model.compile(loss='binary_crossentropy',
                optimizer='rmsprop',
                metrics=['accuracy'])

    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)

    test_datagen = ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode='binary')

    validation_generator = test_datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode='binary')

    model.fit_generator(
        train_generator,
        steps_per_epoch=nb_train_samples / batch_size,
        epochs=epochs,
        validation_data=validation_generator,
        validation_steps=nb_validation_samples)

    model.save_weights(model_name)



train_data_dir = 'D:\\Img_base\\Classes\\Good_datasets\\Data\\train'
validation_data_dir = 'D:\\Img_base\\Classes\\Good_datasets\\Data\\validation'
weights_path= 'E:\\Master_G\\Moduls\\blonde_35_10_512.h5'

check_folder = 'D:\\Img_base\\Scraping'
junk_folder = 'D:\\Img_base\\Scraping_junk'
check_folder_fin = 'D:\\Img_base\\Scraping\\folder'

#train NN
TrainNN(train_data_dir,validation_data_dir, "test1000.h5" )
'''
img_width, img_height = 150, 150

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

model = create_model(input_shape)
model.load_weights(weights_path)

'''

'''
test_datagen = ImageDataGenerator(rescale=1. / 255)

check_generator = test_datagen.flow_from_directory(
        check_folder,
        target_size=(img_width, img_height),
        batch_size=1,
        class_mode='binary')
'''
#output = model.predict_generator(check_generator, steps = 1, max_queue_size=96,workers=1,use_multiprocessing=False, verbose=0)
#x = image_tools.readImagesAsNumpyArrays(check_folder_fin,150, 150)
#for item in x:
#    output = model.predict_on_batch(item)
#    print(output)


'''
files = os.listdir(check_folder_fin)
for file in files:
    if ".jpg" or ".png" in str(file):
        path = os.path.join(check_folder_fin, file)
        img = misc.imread(path)
        img = misc.imresize(img, (img_height, img_width))
        img = img * (1. / 255)
        img = img[None, :, :,: ]
        output = model.predict_on_batch(img)
        print(file)
        print(output)

'''

'''
counter_a = 0
counter_b = 0
files = os.listdir(check_folder_fin)
for file in files:
    if ".jpg" or ".png" in str(file):
        path = os.path.join(check_folder_fin, file)
        img = misc.imread(path)
        img = misc.imresize(img, (img_height, img_width))
        img = img * (1. / 255)
        img = img[None, :, :,: ]
        output = model.predict_on_batch(img)
        if(output < 0.3):
            counter_a = counter_a + 1
        elif(output > 0.8):
            counter_b = counter_b + 1
print("counter_a:  ")
print(counter_a)
print("counter_b:  ")
print(counter_b)    

#Return list a with true prediction, b - false prediction and c - with idk prediction
def ValidateFolderByNNBinary(theModel ,target_folder, threshold_low, threshold_high, img_height = 150, img_width = 150):
    list_a = list()
    list_b = list()
    list_c = list()
    try:
        files = os.listdir(target_folder)
        for file in files:
            if ".jpg" or ".png" in str(file):
                path = os.path.join(target_folder, file)
                img = misc.imread(path)
                img = misc.imresize(img, (img_height, img_width))
                img = img * (1. / 255)
                img = img[None, :, :,: ]
                #output = model.predict_on_batch(img)
                output = theModel.predict_on_batch(img)
                if(output <= threshold_low):
                    #true
                    list_a.append(path)
                elif(output >= threshold_high):
                    #false
                    list_b.append(path)
                    #idk
                else:
                    list_c.append(path)
    except Exception as ex:
        logger.LogFromTread(ex.args,'error.log')
    return list_a, list_b, list_c

'''