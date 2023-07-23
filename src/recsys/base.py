from typing import List, Set, Optional, Any

import pandas as pd
from .utils import parse


class ContentBaseRecSys:

    def __init__(self, movies_dataset_filepath: str, distance_filepath: str):
        self.distance = pd.read_csv(distance_filepath, index_col='id')
        self.distance.index = self.distance.index.astype(int)
        self.distance.columns = self.distance.columns.astype(int)
        self._init_movies(movies_dataset_filepath)

    def _init_movies(self, movies_dataset_filepath) -> None:
        self.movies = pd.read_csv(movies_dataset_filepath, index_col='id')
        self.movies.index = self.movies.index.astype(int)
        self.movies['genres'] = self.movies['genres'].apply(parse)

    def get_title(self) -> List[str]:
        return self.movies['original_title'].values

    def get_genres(self) -> Set[str]:
        genres = [item for sublist in self.movies['genres'].values.tolist() for item in sublist]
        return set(genres)

    def recommendation(self, title: str, top_k: int = 5, genres: Set[str] = None, director: str = None) -> List[str]:
        movie_index = self.movies[self.movies['original_title'] == title].index[0]
        if genres and director: 
            filtered_movies = self.filter_movies_by_genre_and_director(genres, director)
        elif genres:
            filtered_movies = self.filter_movies_by_genre(genres)
        elif director:
            filtered_movies = self.filter_movies_by_director(director)
        else:
            filtered_movies = None
        top_movies_indoces = self.get_top_k_movies(movie_index, top_k, filtered_movies, genres, director)
        return self.movies.loc[top_movies_indoces, 'original_title'].tolist()
    
    def get_top_k_movies(self, movie_index:int, top_k:int, filtered_movies: List[int] = None, genres: Set[str] = None, director: str = None):
        distances = self.distance.loc[movie_index].sort_values(ascending=False)
        if filtered_movies:
            distances = distances[distances.index.isin(filtered_movies)]
        if genres:
            filtered_indices = []
            for index in distances.index:
                if any(genre in self.movies.loc[index, 'genres'] for genre in genres):
                    filtered_indices.append(index)
            distances = distances[distances.index.isin(filtered_indices)]
        if director:
            filtered_indices = []
            for index in distances.index:
                crew = eval(self.movies.loc[index, 'crew'])
                if any(person['name'] == director and person['job'] == 'Director' for person in crew):
                    filtered_indices.append(index)
            distances = distances[distances.index.isin(filtered_indices)]
        top_movies_indices = distances.index[1:top_k+1]

        return top_movies_indices
    
    def update_recommentations(self, new_title: str, top_k: int = 5, genres: Set[str] = None, director: str = None) -> List[str]:
            return self.recommentation(new_title, top_k, genres, director)
    
    def filter_movies_by_genre(self, genres: Set[str]) -> List[int]:
        filtered_movies = []
        for index, row in self.movies.iterrows():
            if any(genre in row['genres'] for genre in genres):
                filtered_movies.append(index)
        return filtered_movies

    def filter_movies_by_director(self, director):
        filtered_movies = []
        for index, row in self.movies.iterrows():
            crew= eval(row['crew'])
            if any(person['name'] == director and person['job'] == 'Director' for person in crew):
                filtered_movies.append(index)
        return filtered_movies
    
    def filter_movies_by_genre_and_director(self, genres: Set[str], director: str) -> List[int]:
        filtered_movies=[]
        for index, row in self.movies.iterrows():
            if any(genre in row['genres'] for genre in genres):
                filtered_movies.append(index)
            if isinstance(row['crew'], list) and any(person['name'] == director and person['job'] == 'Director' for person in row['crew']):
                filtered_movies.append(index)
        return filtered_movies
    