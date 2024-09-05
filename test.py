import re
import os
import nltk
import joblib
import requests
import numpy as np
from bs4 import BeautifulSoup
import urllib.request as urllib
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from wordcloud import WordCloud,STOPWORDS
from flask import Flask,render_template,request
import time


# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')

# app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# word_2_int = joblib.load('word2int.sav')
# model = joblib.load('sentiment.sav')
# stop_words = set(open('stopwords.txt'))

def clean(x):
    x = re.sub(r'[^a-zA-Z ]', ' ', x) # replace evrything thats not an alphabet with a space
    x = re.sub(r'\s+', ' ', x) #replace multiple spaces with one space
    x = re.sub(r'READ MORE', '', x) # remove READ MORE
    x = x.lower()
    x = x.split()
    y = []
    for i in x:
        if len(i) >= 3:
            if i == 'osm':
                y.append('awesome')
            elif i == 'nyc':
                y.append('nice')
            elif i == 'thanku':
                y.append('thanks')
            elif i == 'superb':
                y.append('super')
            else:
                y.append(i)
    return ' '.join(y)


def extract_all_reviews(url, clean_reviews, org_reviews,customernames,commentheads,ratings):
    with urllib.urlopen(url) as u:
        page = u.read()
        page_html = BeautifulSoup(page, "html.parser")
    reviews = page_html.find_all('div', {'class': 't-ZTKy'})
    commentheads_ = page_html.find_all('p',{'class':'_2-N8zT'})
    customernames_ = page_html.find_all('p',{'class':'_2sc7ZR _2V5EHH'})
    ratings_ = page_html.find_all('div',{'class':['_3LWZlK _1BLPMq','_3LWZlK _32lA32 _1BLPMq','_3LWZlK _1rdVr6 _1BLPMq']})

    for review in reviews:
        x = review.get_text()
        org_reviews.append(re.sub(r'READ MORE', '', x))
        clean_reviews.append(clean(x))
    
    for cn in customernames_:
        customernames.append('~'+cn.get_text())
    
    for ch in commentheads_:
        commentheads.append(ch.get_text())
    
    ra = []
    for r in ratings_:
        try:
            if int(r.get_text()) in [1,2,3,4,5]:
                ra.append(int(r.get_text()))
            else:
                ra.append(0)
        except:
            ra.append(r.get_text())
        
    ratings += ra
    print(ratings)

def tokenizer(s):
    s = s.lower()      # convert the string to lower case
    tokens = nltk.tokenize.word_tokenize(s) # make tokens ['dogs', 'the', 'plural', 'for', 'dog']
    tokens = [t for t in tokens if len(t) > 2] # remove words having length less than 2
    tokens = [t for t in tokens if t not in stop_words] # remove stop words like is,and,this,that etc.
    return tokens

def tokens_2_vectors(token):
    X = np.zeros(len(word_2_int)+1)
    for t in token:
        if t in word_2_int:
            index = word_2_int[t]
        else:
            index = 0
        X[index] += 1
    X = X/X.sum()
    return X

def result():    
    url = 'https://www.flipkart.com/samsung-galaxy-s21-fe-5g-snapdragon-888-lavender-128-gb/p/itm9189006529d08?pid=MOBGTKQGKGYZDJZY&lid=LSTMOBGTKQGKGYZDJZYQFCUMH&marketplace=FLIPKART&q=samsung+s21+fe+5g&store=tyy%2F4io&srno=s_1_1&otracker=AS_QueryStore_OrganicAutoSuggest_1_11_na_na_ps&otracker1=AS_QueryStore_OrganicAutoSuggest_1_11_na_na_ps&fm=Search&iid=bb8cdd59-3ba8-4f79-9b6e-55b60ed421f4.MOBGTKQGKGYZDJZY.SEARCH&ppt=sp&ppn=sp&ssid=ew8rfrbb400000001711008439879&qH=3382a307cdb7e16b'

    nreviews = 10
    clean_reviews = []
    org_reviews = []
    customernames = []
    commentheads = []
    ratings = []

    with urllib.urlopen(url) as u:
        page = u.read()
        page_html = BeautifulSoup(page, "html.parser")

    proname = page_html.find_all('span', {'class': 'B_NuCI'})[0].get_text()
    price = page_html.find_all('div', {'class': '_30jeq3 _16Jk6d'})[0].get_text()
    
    # getting the link of see all reviews button
    all_reviews_url = page_html.find_all('div', {'class': 'col JOpGWq'})[0]
    all_reviews_url = all_reviews_url.find_all('a')[-1]
    all_reviews_url = 'https://www.flipkart.com'+all_reviews_url.get('href')
    # url2 = all_reviews_url+'&page=1'
    url2 = 'https://www.flipkart.com/samsung-galaxy-s21-fe-5g-snapdragon-888-lavender-128-gb/product-reviews/itm9189006529d08?pid=MOBGTKQGKGYZDJZY&lid=LSTMOBGTKQGKGYZDJZYQFCUMH&marketplace=FLIPKART&page=1'
    
    

    # start reading reviews and go to next page after all reviews are read 
    while True:
        x = len(clean_reviews)
        # extracting the reviews
        extract_all_reviews(url2, clean_reviews, org_reviews,customernames,commentheads,ratings)
        url2 = url2[:-1]+str(int(url2[-1])+1)
        if x == len(clean_reviews) or len(clean_reviews)>=nreviews:break

    org_reviews = org_reviews[:nreviews]
    clean_reviews = clean_reviews[:nreviews]
    customernames = customernames[:nreviews]
    commentheads = commentheads[:nreviews]
    ratings = ratings[:nreviews]


    # building our wordcloud and saving it
    # for_wc = ' '.join(clean_reviews)
    # wcstops = set(STOPWORDS)
    # wc = WordCloud(width=1400,height=800,stopwords=wcstops,background_color='white').generate(for_wc)
    # plt.figure(figsize=(20,10), facecolor='k', edgecolor='k')
    # plt.imshow(wc, interpolation='bicubic') 
    # plt.axis('off')
    # plt.tight_layout()
    # CleanCache(directory='static/images')
    # plt.savefig('static/images/woc.png')
    # plt.close()


    # predictions = []
    # for i in range(len(org_reviews)):
    #     vector = tokens_2_vectors(tokenizer(clean_reviews[i]))
    #     vector = vector[:-1]
    #     if model.predict([vector])[0] == 1:
    #         predictions.append('POSITIVE')
    #     else:
    #         predictions.append('NEGATIVE')
    
    # making a dictionary of product attributes and saving all the products in a list
    d = []
    for i in range(len(org_reviews)):
        x = {}
        x['review'] = org_reviews[i]
        # x['sent'] = predictions[i]
        x['cn'] = customernames[i]
        x['ch'] = commentheads[i]
        x['stars'] = ratings[i]
        d.append(x)
    

    # for i in d:
    #     if i['stars']!=0:
    #         if i['stars'] in [1,2]:
    #             i['sent'] = 'NEGATIVE'
    #         else:
    #             i['sent'] = 'POSITIVE'
    

    # np,nn =0,0
    # for i in d:
    #     if i['sent']=='NEGATIVE':nn+=1
    #     else:np+=1

    # return render_template('result.html',dic=d,n=len(clean_reviews),nn=nn,np=np,proname=proname,price=price)
    print(d);
    
result();