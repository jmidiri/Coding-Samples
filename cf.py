import argparse
import re
import os
import csv
import math
import collections as coll


def parse_argument():
    """
    Code for parsing arguments
    """
    parser = argparse.ArgumentParser(description='Parsing a file.')
    parser.add_argument('--train', nargs=1, required=True)
    parser.add_argument('--test', nargs=1, required=True)
    args = vars(parser.parse_args())
    return args


def parse_file(filename):
    """
    Given a filename outputs user_ratings and movie_ratings dictionaries
    
    The files have the format: MovieID, CustomerID, Rating

    Input: filename

    Output: user_ratings, movie_ratings
        where:
            user_ratings[user_id] = {movie_id: rating}
            movie_ratings[movie_id] = {user_id: rating}
    """
    user_ratings = {}
    movie_ratings = {}
    with open(filename, 'r') as csvfile:
        info_row = csv.reader(csvfile)
        for row in info_row:
            if int(row[1]) in user_ratings:
                user_ratings[int(row[1])][int(row[0])] = float(row[2])
            else:
                user_ratings[int(row[1])] = {int(row[0]): float(row[2])}
            if int(row[0]) in movie_ratings:
                movie_ratings[int(row[0])][int(row[1])] = float(row[2])
            else:
                movie_ratings[int(row[0])] = {int(row[1]): float(row[2])}
    return user_ratings, movie_ratings


def compute_average_user_ratings(user_ratings):
    """ Given a the user_rating dict compute average user ratings

    Input: user_ratings (dictionary of user, movies, ratings)
    Output: ave_ratings (dictionary of user and ave_ratings)
    """
    ave_ratings = {}
    for user_key in user_ratings:
        avg = sum(user_ratings[user_key].values())/len(user_ratings[user_key].values())
        ave_ratings[user_key] = avg
    return ave_ratings


def compute_user_similarity(d1, d2, ave_rat1, ave_rat2):
    """ Computes similarity between two users

        Input: d1, d2, (dictionary of user ratings per user) 
            ave_rat1, ave_rat2 average rating per user (float)
        Ouput: user similarity (float)
    """
    intersect = list(set(d1.keys()).intersection(d2.keys()))
    if len(intersect) == 0:
        return 0.0
    else:
        numerator = 0
        denominator_d1 = 0
        denominator_d2 = 0
        for movieId in intersect:
            numerator += (d1[movieId]-ave_rat1)*(d2[movieId]-ave_rat2)
            denominator_d1 += (d1[movieId]-ave_rat1)**2
            denominator_d2 += (d2[movieId]-ave_rat2)**2
        if ((denominator_d1 * denominator_d2) ** 0.5) != 0:
            return numerator / ((denominator_d1 * denominator_d2) ** 0.5)
        else:
            return 0.0

def main():
    """
    This function is called from the command line via
    
    python cf.py --train [path to filename] --test [path to filename]
    """
    args = parse_argument()
    train_file = args['train'][0]
    test_file = args['test'][0]
    print train_file, test_file
    train_user, train_movie = parse_file(train_file)
    test_user, test_movie = parse_file(test_file)
    predicted_movie_user_ratings = []
    avg_user_ratings = compute_average_user_ratings(train_user)
    for user in test_user:  # will grab the user id from the test set
        for movie in test_user[user].keys():
            user_avg = avg_user_ratings[user]
            user_sim_sum = 0
            user_sim_ratdiff_sum = 0
            for sim_user in train_movie[movie].keys():  # all the users who saw that movie
                user_sim_value = compute_user_similarity(train_user[user], train_user[sim_user], avg_user_ratings[user],
                                                         avg_user_ratings[sim_user])
                user_sim_sum += abs(user_sim_value)
                user_sim_ratdiff_sum += user_sim_value * (train_user[sim_user][movie] - avg_user_ratings[sim_user])
            if user_sim_sum != 0:
                predicted_rating = user_avg + (user_sim_ratdiff_sum) / (user_sim_sum)
            else:
                predicted_rating = user_avg
            predicted_movie_user_ratings.append([movie, user, test_movie[movie][user], predicted_rating])
    # generating the output file
    with open("predictions.txt", "w") as output_file:  # generates the output csv
        writer = csv.writer(output_file)
        writer.writerows(predicted_movie_user_ratings)
    # calculating the rmse and mae
    sum_squared_error = 0
    sum_abs_error = 0
    for predicates in predicted_movie_user_ratings:
        sum_squared_error += (predicates[3] - test_movie[predicates[0]][predicates[1]]) ** 2
        sum_abs_error += abs(predicates[3] - test_movie[predicates[0]][predicates[1]])
    rmse = (sum_squared_error / len(predicted_movie_user_ratings)) ** 0.5
    mae = sum_abs_error / len(predicted_movie_user_ratings)
    print "RMSE", rmse
    print "MAE", mae

if __name__ == '__main__':
    main()

