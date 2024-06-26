# -*- coding: utf-8 -*-
"""Untitled13.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jLz3eJVleQFmHROvtnWXUsmhWRySozkl
"""

pip install pronouncing

import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, LSTM, Dense, Bidirectional
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
import numpy as np
import urllib.request
import random
import pronouncing  # import the pronouncing package

# Download the data and read a subset of lines
url = 'https://ocw.mit.edu/ans7870/6/6.006/s08/lecturenotes/files/t8.shakespeare.txt'
response = urllib.request.urlopen(url)
data = response.readlines()
data = [line.decode('utf-8') for line in data]
data = random.sample(data, 1000)

# Tokenize the data
tokenizer = Tokenizer()
tokenizer.fit_on_texts(data)
total_words = len(tokenizer.word_index) + 1

input_sequences = []
for line in data:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# Pad sequences
max_sequence_len = max([len(x) for x in input_sequences])
input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

# Create predictors and label
xs, labels = input_sequences[:,:-1],input_sequences[:,-1]

ys = tf.keras.utils.to_categorical(labels, num_classes=total_words)

# Define the model
model = Sequential()
model.add(Embedding(total_words, 100, input_length=max_sequence_len-1))
model.add(Bidirectional(LSTM(150)))
model.add(Dense(total_words, activation='softmax'))
adam = Adam(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
history = model.fit(xs, ys, epochs=50, verbose=1)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GRU, Dense
from tensorflow.keras.optimizers import Adam

# Define the model architecture
model1 = Sequential()
model1.add(Embedding(total_words, 100, input_length=max_sequence_len-1))
model1.add(GRU(150, return_sequences=True))
model1.add(GRU(150))
model1.add(Dense(total_words, activation='softmax'))

# Compile the model
adam = Adam(lr=0.01)
model1.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])

history = model1.fit(xs, ys, epochs=50, verbose=1)

def filter_predicted_words(predicted_probs, rhyming_words, threshold=0.1):
    filtered_probs = np.zeros_like(predicted_probs)
    for word, prob in rhyming_words.items():
        if prob > threshold:
            index = tokenizer.word_index.get(word)
            if index is not None:
                filtered_probs[index] = predicted_probs[index]
    return filtered_probs

def generate_poem(model, tokenizer, max_sequence_len, seed_text, next_words, rhyme_scheme=None):
    generated_text = seed_text
    for i in range(next_words):
        token_list = tokenizer.texts_to_sequences([generated_text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len - 1, padding='pre')
        predicted_probs = model.predict(token_list, verbose=0)[0]
        
        if rhyme_scheme:
            last_word = generated_text.split()[-1]
            last_rhyme = rhyme_scheme.get(last_word)
            if last_rhyme is not None:
                rhyming_words = rhyme_scheme[last_rhyme]
                predicted_probs = filter_predicted_words(predicted_probs, rhyming_words)
        
        predicted_index = np.argmax(predicted_probs)
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted_index:
                output_word = word
                break
        generated_text += " " + output_word
    return generated_text

# Generate a poem using LSTM Model
seed_text = "Oh where thou art"
next_words = 100
generated_poem = generate_poem(model, tokenizer, max_sequence_len, seed_text, next_words)
print(generated_poem)

# Generate a poem using GRU Model
seed_text = "Oh where thou art"
next_words = 100
generated_poem = generate_poem(model1, tokenizer, max_sequence_len, seed_text, next_words)
print(generated_poem)