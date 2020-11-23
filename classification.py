import sys
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout
from tensorflow.keras import layers
from keras.layers import Input,UpSampling2D
from keras.utils import to_categorical
import numpy as np
from keras.models import load_model
import matplotlib.pyplot as plt
from autoencoder import getInfo
import ast 
from autoencoder import createNParray
from autoencoder import Encoder

def Opening_set_file(file):
	image_number,rows_number,columns_number=getInfo(file)
	return image_number,rows_number,columns_number

def Opening_labels_file(f):
	temp = f.read(4) 
	temp = f.read(4) 
	temp = np.frombuffer(temp,dtype = np.uint8).astype(np.int64)
	number_of_items=(temp[0]<<24)|(temp[1]<<16)|(temp[2]<<8)|temp[3]
	return number_of_items

def fc(enco):
    flat = Flatten()(enco)
    den = Dense(128, activation='relu')(flat)
    num_classes=10
    out = Dense(num_classes, activation='softmax')(den)
    return out

def createNParray_of_Labels_set(f,number):
	e=f.read(number)
	e=np.frombuffer(e,dtype = np.uint8).astype(np.int64)  
	return e



def reshaping(e1,e2,e3,e4,x1,y1,x2,y2):
	e1=e1.reshape(-1,x1,y1,1)
	e2=e2.reshape(-1,1)
	e3=e3.reshape(-1,x2,y2,1)
	e4=e4.reshape(-1,1)
	return e1,e2,e3,e4

def main():
	training_set=""
	training_labels=""
	test_set=""
	test_labels=""
	model=""    
	coun1=False
	coun2=False
	inChannel=1
	coun3=False
	coun4=False
	coun5=False
	for i in range(0,10):
		if sys.argv[i]=='-d' and coun1==False:
			coun1=True
			training_set=sys.argv[i+1]
		elif sys.argv[i]=='-d1' and coun2==False:
			coun2=True
			training_labels=sys.argv[i+1]
		elif sys.argv[i]=='-t' and coun3==False:
			coun3=True
			test_set=sys.argv[i+1]
		elif sys.argv[i]=='-t1' and coun4==False:
			coun4=True
			test_labels=sys.argv[i+1]
		elif sys.argv[i]=='-model' and coun5==False:
			coun5=True
			model_string=sys.argv[i+1]
		if coun1==True and coun2==True and coun3==True and coun4==True and coun5==True:
			break
	######Data   Preprocessing
	f1=open(training_set,'rb')
	f2=open(training_labels,'rb')
	f3=open(test_set,'rb')
	f4=open(test_labels,'rb')
	image_number_train_set,rows_number_train_set,columns_number_train_set=Opening_set_file(f1)
	image_number_test_set,rows_number_test_set,columns_number_test_set=Opening_set_file(f3)
	number_of_items_training_label=Opening_labels_file(f2)
	number_of_items_test_label=Opening_labels_file(f4)
	e1=createNParray(f1,image_number_train_set,rows_number_train_set,columns_number_train_set)
	e3=createNParray(f3,image_number_test_set,rows_number_test_set,columns_number_test_set)
	e2=createNParray_of_Labels_set(f2,number_of_items_training_label)
	e4=createNParray_of_Labels_set(f4,number_of_items_test_label)
	e1,e2,e3,e4=reshaping(e1,e2,e3,e4,rows_number_train_set,columns_number_train_set,rows_number_test_set,columns_number_test_set)
	f1.close()
	f2.close()
	f3.close()
	f4.close()
	###########################
	f=open("info.txt","r")
	newlist = [line.rstrip() for line in f.readlines()]
	numOfLayers=newlist[0]
	x_filter=newlist[1]
	y_filter=newlist[2]
	filtersPerLayer=newlist[3]
	epochs=newlist[4]
	batch_size=newlist[5]
	ConvLayersEnc=newlist[6]
	ConvLayersDec=newlist[7]
	res = ast.literal_eval(filtersPerLayer)
	f.close()
	model = keras.models.load_model(model_string)
	input_img = Input(shape = (rows_number_train_set, columns_number_train_set, inChannel))
	enco=Encoder(input_img, res,int(ConvLayersEnc),int(x_filter),int(y_filter))
	full_model = model(input_img,fc(enco))
	for l1,l2 in zip(full_model.layers[:2*int(ConvLayersEnc)+3],autoencoder.layers[0:2*int(ConvLayersEnc)+3]):
		l1.set_weights(l2.get_weights())
	for layer in full_model.layers[0:2*int(ConvLayersEnc)+3]:
   		layer.trainable = False
	full_model.compile(loss=keras.losses.categorical_crossentropy, optimizer=keras.optimizers.Adam(),metrics=['accuracy'])
	classify_train = full_model.fit(train_X, train_label, batch_size=batch_size,epochs=epochs,verbose=1,validation_data=(valid_X, valid_label))
	for layer in full_model.layers[0:2*int(ConvLayersEnc)+3]:
   		layer.trainable = True
	full_model.compile(loss=keras.losses.categorical_crossentropy, optimizer=keras.optimizers.Adam(),metrics=['accuracy'])
	classify_train=full_model.fit(train_X, train_label, batch_size=batch_size,epochs=epochs,verbose=1,validation_data=(valid_X, valid_label))
   	

if __name__ == "__main__":
    main()
