import io
import random
import string # to process standard python strings
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
import re
from colorama import Fore, Back, Style 

rawData = {}
raw = ""
with open("onlyTopicsData.json") as json_file:
    data = json.load(json_file)
    rawData = data
    for bigTopic, topics in data.items():
        for topic, text in topics.items():
            if text.strip() != "":
                raw += " \n " + " ".join(text.strip().split("\n"))

#Tokenization
sent_tokens = []
articles = []
articleToText = {}
with open("onlyTopicsData.json") as json_file:
    data = json.load(json_file)
    for category, topics in data.items():
        for topic, text in topics.items():
            if text.strip() != "" and text.strip() != " ":
                text = " ".join([w for w in text.split(" ") if w.strip() != "" and "[" not in w])
                doc = " ".join([p for p in text.strip().split("\n") if p.strip() != ""])
                sentences = [sent for sent in nltk.sent_tokenize(doc) if len(sent) > 5]
                article = [topic for _ in range(len(sentences))]
                sent_tokens.extend(sentences)
                articles.extend(article)
                articleToText[topic] = text

lemmer = WordNetLemmatizer()

# take as input the tokens and return normalized tokens
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

# tokens normalized
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

greeting_in = ("hello", "hi", "greetings", "sup", "yo", "hey", " what's up")
# array form because random.choice()
greeting_out = ["hi", "hey there", " hello", "I'm glad we are conversing."]

rejection_words = ["no", "nah", "nope", "not really", "not quite"]
approval_words = ["yes", "yeah", "yea", "yep", "ya", "ye", "kinda", "a little"]

#if user types in greeting, send a greeting out
def introduction(sentence):
    for word in sentence.split():
        if word.lower() in greeting_in:
            return random.choice(greeting_out);

TfidfVect = TfidfVectorizer(tokenizer = LemNormalize, stop_words = 'english')
# TfidfVect = TfidfVectorizer(stop_words = 'english', ngram_range=(1,2))
tfidf = TfidfVect.fit_transform(sent_tokens)

#response
def get_user_input():
    print(Style.RESET_ALL + ">", end = " ")
    userinput = input().lower()
    print(Fore.RED)
    return userinput

#original response
def response(user_text):
    robo_text = ''
    sent_tokens.append(user_text)
    values = cosine_similarity(TfidfVect.transform([user_text]), tfidf)
    indexes = values.argsort()[0]
    index = values.argsort()[0][-1]
    flat = values.flatten()
    flat.sort()
    if (flat[-1] == 0):
        robo_text = robo_text + "I\'m sorry, I do not understand you. The query you have inputted is incomprehensible. \n Please try again. "
        return robo_text
    else:
        print("I found these articles most similar to your input.") 
        
        # print top 5 most related articles
        for i in range(1,6): #print 5 most related sentences
            index = indexes[-i]
            print("Article {}: {}".format(i, articles[index]))
            print("Similar Sentence:" + sent_tokens[index])
            
        print()
        print("Do any of these match your interest?")
        
        user_text = get_user_input() # request user's approval
        
        # validate input
        while user_text not in rejection_words and user_text not in approval_words:
            print("I'm sorry, I did not understand whether you found these interesting. Please say yes or no!")
            user_text = get_user_input()
        
        if user_text in rejection_words:
            print("Let me find a few more articles.")
            
            # print articles 6-10
            for i in range(6,11):
                index = indexes[-i]
                print("Article {}: {}".format(i, articles[index]))
                print("Similar Sentence:" + sent_tokens[index])
            
            print()
            print("Do any of these match your interest?")

            user_text = get_user_input() # request user's approval
            
            while user_text not in rejection_words and user_text not in approval_words:
                print("I'm sorry, I did not understand whether you found these interesting. Please say yes or no!")
                user_text = get_user_input()
            
            if user_text in rejection_words:
                print("I'm sorry I couldn't find any good results. Could you please rephrase your inquiry or try something else?")
                user_text = get_user_input() 
                response(user_text) # starting over
            elif user_text in approval_words:
                print("Awesome! Please state the article number you would like to explore more.")
                user_text = get_user_input() 
                next_response(user_text, indexes, 10)
                  
        elif user_text in approval_words:
            print("Awesome! Please state the article number you would like to explore more.")
            user_text = get_user_input()
            next_response(user_text, indexes, 5)
            
    return robo_text

def next_response(user_text, indexes, rank):
    if not user_text.isdigit():
        print("invalid input")
        return
    i = int(re.findall(r"\d+", user_text)[0])
    if i > rank:#TODO
        print("invalid input")
        return
    index = indexes[-i]
    sentence = sent_tokens[index]
    articleText = articleToText[articles[index]]
    paragraphs = [p for p in articleText.split("\n") if p != ""]
    
    articleSents = nltk.sent_tokenize(" ".join(paragraphs))
    articleVect = TfidfVectorizer(stop_words = "english")
    articleTfidf = articleVect.fit_transform(articleSents)
    values = cosine_similarity(articleVect.transform([sentence, user_text]), articleTfidf)
    indexes = values.argsort()[0]
    bestIndex = values.argsort()[0][-1]
    while bestIndex < len(values[0]) and values[0][bestIndex] > 0:
        print(articleSents[bestIndex])
        bestIndex += 1

user_exit = False
if __name__ == "__main__":
    #first message to user 
    print(Fore.RED + "Hi! My name is KnowBot, I am an AI powered chatbot that can provide you with interesting knowledge. \n  I can answer queries about the following topics: Mathematics, Science, Music, Politics, History (USA), Computer Science. \n If you would like to exit, please type \"bye\". If you need help, please type \"help\". ")

    while (user_exit == False):
            user_text = get_user_input()
            user_text = user_text.lower()
            # user want to leave
            if (user_text == 'bye'):
                user_exit = True
                print("KnowBot: Bye! Take care and come back soon. ")
            # replying to gratitude
            elif(user_text == 'thanks' or user_text == 'thank you'):
                print("KnowBot: You\'re welcome! Ask me another query!")
            # user needs more instructions
            elif (user_text == 'help'):
                print("KnowBot: I\'m sorry the instructions were unclear. \n I am a robot designed to answer queries you have about the following subjects: Matematics, Science, Music, Politics, History (USA), Computer Science. \n You can type in keyword(s) (i.e. multiplication, linear algebra, boolean, 1844) to learn more about that subject. \n If you would like to leave, please type \"bye\".")
            # user has typed in a greeting
            elif (introduction(user_text) != None):
                print("KnowBot: " + introduction(user_text))
            # user has typed in a keyword, generate a response
            else:
                print("KnowBot: " , end= "")
                print(response(user_text))