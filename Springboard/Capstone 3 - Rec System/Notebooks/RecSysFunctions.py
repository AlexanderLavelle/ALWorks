# -*- coding: utf-8 -*-
"""
Created on Wed May 19 06:35:07 2021

Functions for RecSys

@author: Alexander
"""
import pandas as pd
import datetime as dt
import numpy as np



def last_movie(usrId, movies=movies, ratings=ratings):
    df = ratings[ratings.userId == usrId].sort_values('timestamp')
    last = pd.DataFrame(df.iloc[-1]).T.merge(movies[['movieId', 'title']], on='movieId')
    return last

def user_rated(usrId, movies=movies, ratings=ratings):
    rated = ratings[ratings.userId == usrId].merge(
        movies[['movieId', 'title']], on='movieId')[['title', 'movieId']].set_index('title')
    return rated

def diversity_handling(input_list:list):
    for item in input_list:
        df = pd.DataFrame(item[0])
        for i in range(1, len(item)):
            df = df.append(item[i])
    return df

def add_movies(usrId, movId, rating, ratingsdf=ratingsdf):
    #dictionary = {'usrId':usrId, ...}
    df = pd.DataFrame([usrId, movId, rating, dt.datetime.now(), ratingsdf.rating_new.mean()]).T
    df.columns = ratingsdf.columns
    return df

def search_movieId(moviedf=movies.dropna()):
    string = input("Enter a search phrase for title.\n")
    if string == 'exit':
        pass
    else:
        moviedf['title'] = moviedf.title.str.lower()
        lowString = string.lower()
        df = moviedf[moviedf.title.str.contains(lowString)]
        df['title'] = df.title.str.title()
        df = df[['title', 'year', 'movieId']]
    return df

def ID_setup(ratdf=rated):
    exit_phrase = 'Thank you for trying!\n'
    value = input("Hello! Are you a 'known' user or 'new' user?:\n")
    if value == 'known':
        idno = input("Good to see you! Let's keep recommending! Please enter your ID.\n")
        print(f'You entered {idno}. We will use this until exit. If not you, please exit.')
        idno = int(idno)
    elif value == 'exit':
        print(exit_phrase)
    else:
        value = input("Would you like to set a 'custom' id # or 'no' custom id?\n")
        if value == 'custom':
            idno = input('Enter custom id as an integer greater than 650')
            print(f'Your ID is: {idno}')
        elif value == 'exit':
            print(exit_phrase)
        else:
            idno = ratdf.userId.max()+1
            print(f'Your ID is: {idno}')
        print("Let's start recommending!")
    return idno

def find_user(idno, ratings=ratings):
    df = ratings[ratings.userId == idno]
    switch = 0
    while len(df) < 3:
        print('Need minimum 3 movies to start')
    else:
        print("Starting RecSys")
        switch = 1
    return switch

def choose_append(idno):

    restart = True
    while True:
        options = search_movieId()
        display(options)
        choice = input("If we found the movie, type its movieId, else type 'choose again'.\n")
        if choice == 'exit':
            break
        else:
            try:
                choice = int(choice)
                restart = False
                rating = input('Adding to your ratings. Please rate now, .5 to 5.0\n')
                if rating == 'exit':
                    break
                else:
                    try:
                        rating = float(rating)
                        updated_ratings = add_movies(idno, choice, rating)
                        display(updated_ratings)
                        return updated_ratings
                    except:
                        print('Must input float in [.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]')
                        #This is just going to have to be annoying, sorry
            except:
                print('Choice must be an integer. Please try again.')
                continue
    
    return updated_ratings

def serve_recs(idno, counter=None, algolist=algos, ratedf=rated, dlmodel=adaModel, movies=movies):
    i = counter
    if counter is None:
        i=0
    SVDpreds = algo_preds(algolist[i], idno)
    SVDpreds = SVDpreds[['title', 'movieId']]
    SVDpreds = SVDpreds[~SVDpreds.movieId.isin(ratedf[ratedf.userId == idno].movieId)]
    
    dlpreds = dl_preds(dlmodel, idno)
    dlpreds = dlpreds[~dlpreds.movieId.isin(ratedf[ratedf.userId == idno].movieId)]
    dlpreds = dlpreds[~dlpreds.movieId.isin(SVDpreds.movieId)]
    
    lenSVDpreds = 20 - len(dlpreds) - 1
    SVDpreds = SVDpreds[:lenSVDpreds]
    
    output = SVDpreds.append(dlpreds)
    output.drop_duplicates(inplace=True)
    
    while len(output) < 20:
        recentmovie = movies[movies.year == max(movies.year)][['title', 'movieId']].sample()
        output = output.append(recentmovie)

    return output

def rec_sys(ratingsdf=ratingsdf, algolist=algos):
    rated = ratingsdf
    print("Welcome to this recommendation system. Type 'exit' to leave at any time.\n")
    idno = ID_setup(rated)
    switch = find_user(idno)
    
    while switch == 0:
        update = choose_append(idno)
        rated = rated.append(update) #this part is weak to incorrect numbers in the long run and duplicate entries
        metric = rated[rated.userId == idno]
        if len(metric) < 3:
            continue
        else:
            switch = 1
            print('Thank you for rating. Preparing to recommend!')
            
    while switch == 1:
        recommend = True
        counter = 0
        while recommend == True:
            recs = serve_recs(idno, counter, ratedf=rated)
            display(recs)
            print('Above are your 20 ratings. Choose a movie to rate to proceed')
            
            newRated = input('Input movieId you wish to rate. Type "exit" to leave.\n')
            if newRated == 'exit':
                recommend = False
                return rated
            newRated = int(newRated)
            
            rat = input('Input rating from .5 to 5.0. Type "exit" to leave.\n')
            if rat == 'exit':
                recommend = False
                return rated
            
            rat = float(rat)
            new_mov = add_movies(idno, newRated, rat)
            rated = rated.append(new_mov)
            
            if counter == 4:
                counter = 0
            else:
                counter+=1

    
    return rated

def cos_sim_preds(usrId, limit:int=None, similarities=similarities):
    df = last_movie(usrId)
    ID = df.movieId[0]
    
    output = similarities.loc[ID].sort_values(ascending=False)
    if limit is not None:
        output = output[:limit]
    
    return output

def rec_movie(movie_id, moviedf=movies, movie_based_similarity=movie_based_similarity):
    temp_table = pd.DataFrame(columns = moviedf.columns)
    movies = movie_based_similarity[movie_id].sort_values(ascending = False).index.tolist()[:11]
    for mov in movies:
#         display(items[items['movie id'] == mov])
        temp_table = temp_table.append(moviedf[moviedf['movieId'] == mov], ignore_index=True)
    return temp_table

def rec_user(user_id, ratingdf=ratings, user_based_similarity=user_based_similarity):
    temp_table = pd.DataFrame(columns = ratingdf.columns)
    us = user_based_similarity[user_id].sort_values(ascending = False).index.tolist()[:101]
    for u in us:
#         display(items[items['movie id'] == mov])
        temp_table = temp_table.append(ratingdf[ratingdf['userId'] == u], ignore_index=True)
    return temp_table

def movieCF_preds(usrId):
    userCF = rec_movie(last_movie(usrId).movieId[0])
    return userCF

def algo_preds(algo, usrId, limit:int=None, movies=movies):
    preds = []
    
    for i in movies.movieId.unique():    
        preds.append(algo.predict(usrId, i))
    
    preds = pd.DataFrame(preds).sort_values('est', ascending=False)  
    
    if limit is not None:
        preds = preds[:limit]
        
    preds = preds.merge(movies[['movieId', 'title']], left_on='iid', right_on='movieId')
    preds.drop(['r_ui', 'details'], axis=1, inplace=True)
    preds['rank'] = preds.est.rank(ascending=False)
    
    return preds

def dl_preds(algo, usrId, movie_df=moviesWithRaw):
    scores, titles = algo([str(usrId)])
    titles = titles.numpy()
    titles_processed = []
    
    for i in range(len(titles[0])):
        tit = titles[0][i].decode('utf-8')
        titles_processed.append(tit)
        
    titles_processed = pd.DataFrame(titles_processed, 
                                    columns=['title']
                                   ).merge(movie_df[['movieId', 'raw_title']],
                                           left_on='title', right_on='raw_title'
                                          ).drop('raw_title', axis=1)
    
    return titles_processed

def movieCF_hitrate(usrId, HR_limit=20):
    userCF = movieCF_preds(usrId)
    userCF = userCF[userCF.movieId != last_movie(usrId).movieId[0]]
    
    if userCF.shape[0] > HR_limit:
        userCF = userCF[:HR_limit]
    
    mask = userCF.movieId.isin(user_rated(80).movieId)

    hrstring = 'Hitrate @'+str(HR_limit)+' is: '+str(mask.sum())
    recShape = str(len(userCF))+' recs generated'
    titlesMatched = 'Movies Matched: '+userCF[mask].title.values
    
    print(hrstring+'; '+recShape+'; '+titlesMatched)
    return mask.sum() / len(userCF)

def algo_hitrate(algo, usrId, HR_limit=20, ratings=ratings):
    preds = algo_preds(algo, usrId, HR_limit)
    rated = user_rated(usrId).movieId
    
    mask = preds.movieId.isin(rated)
    merged = preds[mask].merge(ratings[['userId', 'movieId', 'rating']], 
                                       left_on=['uid', 'iid'], right_on=['userId', 'movieId'])
    display(merged)
    return mask.sum()

def dl_hitrate(algo, usrId, HR_limit=10):
    #note that max output is 10 anyway
    
    preds = dl_preds(algo, usrId)
    rated = user_rated(usrId)
    
    mask = preds.movieId.isin(rated.movieId)  
    masked = preds[mask]
    
    display(masked)
    return mask.sum()

def cos_sim_diversity(usrId, limit:int=20, movie_div=movie_div):
    preds = pd.DataFrame(cos_sim_preds(usrId)[:limit])
    preds = preds.merge(movie_div, left_on=preds.index, right_on=movie_div.movieId)
    
    outputRow = pd.DataFrame(preds.diversity_score.describe()).T
    
    return outputRow
    
def movieCF_diversity(usrId, limit:int=20, movie_div=movie_div):
    preds = movieCF_preds(usrId)[:limit]
    preds = preds.merge(movie_div, on='movieId')
    
    outputRow = pd.DataFrame(preds.diversity_score.describe()).T
    
    return outputRow

def algo_diversity(algo, usrId, limit:int=20, movie_div=movie_div):
    preds = algo_preds(algo, usrId)[:limit]
    preds = preds.merge(movie_div, on='movieId')
    
    outputRow = pd.DataFrame(preds.diversity_score.describe()).T
    
    return outputRow
    
def dl_diversity(algo, usrId, limit:int=20, movie_div=movie_div):
    preds = dl_preds(algo, usrId)[:limit]
    preds = preds.merge(movie_div, on='movieId')
    
    outputRow = pd.DataFrame(preds.diversity_score.describe()).T
    
    return outputRow

def cos_sim_pop(usrId, limit:int=20, popularityTable=popularityTable):
    popularity = []
    for usr in usrId:
        preds = pd.DataFrame(cos_sim_preds(usr)[:limit])
        preds = preds.merge(popularityTable[['movieId', 'ranks']], on='movieId')

        popularity.append(preds.ranks.mean())  

    return np.mean(popularity)

def movieCF_pop(usrId, limit:int=20, popularityTable=popularityTable):
    popularity = []
    for usr in usrId:
        preds = movieCF_preds(usr)[:limit]
        preds = preds.merge(popularityTable[['movieId', 'ranks']], on='movieId')

        popularity.append(preds.ranks.mean())  

    return np.mean(popularity)

def algo_pop(algo, usrId, limit:int=20, popularityTable=popularityTable):
    popularity = []
    for usr in usrId:
        preds = algo_preds(algo, usr)[:limit]
        preds = preds.merge(popularityTable[['movieId', 'ranks']], on='movieId')

        popularity.append(preds.ranks.mean())  

    return np.mean(popularity)

def dl_pop(algo, usrId, limit:int=20, popularityTable=popularityTable):
    popularity = []
    for usr in usrId:
        preds = dl_preds(algo, usr)[:limit]
        preds = preds.merge(popularityTable[['movieId', 'ranks']], on='movieId')

        popularity.append(preds.ranks.mean())  

    return np.mean(popularity)
    
    

