# Import necessary libraries
import requests  # For making HTTP requests to external APIs

#connect to mongodb (vector db)
#get data movies from TMDB API
#embedding data movies
#store embedding data to mongodb (vector db)

from pymongo import MongoClient  # To interact with MongoDB database
from sentence_transformers import SentenceTransformer  # For generating embeddings from text
from apiKey import TMDB_API_KEY, MONGO_CONNECTION_STRING  # Import API keys and connection strings from a separate file
import logging  # For logging information during execution

# Set up logging configuration to display logs at the INFO level
logging.basicConfig(level=logging.INFO)

# Connect to MongoDB using the provided connection string
client = MongoClient(MONGO_CONNECTION_STRING)
db = client["movie_app"]  # Access the "movie_app" database
movies_collection = db["movies"]  # Access the "movies" collection within the database

# Assign the TMDB API key from the imported variables
TMDB_API_KEY = TMDB_API_KEY

# Load a pre-trained sentence transformer model for generating embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to fetch movie genres from The Movie Database (TMDb) API
def fetch_tmdb_genres():
    url = "https://api.themoviedb.org/3/genre/movie/list"  # Endpoint for fetching genres
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}  # Parameters including API key and language preference
    response = requests.get(url, params=params)  # Send GET request to the TMDb API
    
    # If the request is successful (status code 200), process the response
    if response.status_code == 200:
        logging.info("Fetched genres from TMDB.")  # Log success message
        genres = response.json().get("genres", [])  # Extract genres from the response
        # Return a dictionary mapping genre IDs to their names
        return {genre["id"]: genre["name"] for genre in genres}
    else:
        # Log an error if the request fails
        logging.error(f"Failed to fetch genres from TMDB: {response.status_code}")
        return {}  # Return an empty dictionary in case of failure

# Function to fetch popular movies from TMDb API
def fetch_tmdb_movies(page=1):
    url = "https://api.themoviedb.org/3/movie/popular"  # Endpoint for fetching popular movies
    params = {"api_key": TMDB_API_KEY, "language": "en-US", "page": page}  # Parameters including API key, language, and page number
    response = requests.get(url, params=params)  # Send GET request to the TMDb API
    
    # If the request is successful (status code 200), process the response
    if response.status_code == 200:
        logging.info(f"Fetched movies from TMDB (page {page}).")  # Log success message
        movies = response.json().get("results", [])  # Extract movie results from the response
        # Filter out adult movies by checking the 'adult' field
        filtered_movies = [movie for movie in movies if not movie.get("adult", False)]
        return filtered_movies  # Return the filtered list of movies
    else:
        # Log an error if the request fails
        logging.error(f"Failed to fetch movies from TMDB: {response.status_code}")
        return []  # Return an empty list in case of failure

# Function to fetch detail movies from TMDb API
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        logging.warning(f"Failed to fetch details for movie ID {movie_id}")
        return {}

# Function to seed the MongoDB database with fetched movies and their details
def seed_movies(movies, genres):
    for movie in movies:
        movie_id = movie["id"]
        details = fetch_movie_details(movie_id)
        production_countries = details.get("production_countries", [])
        country_names = [c["name"] for c in production_countries]
        original_language = details.get("original_language", "")
        # Extract genre IDs from the movie data
        genre_ids = movie.get("genre_ids", [])
        # Map genre IDs to genre names using the genres dictionary
        genre_names = [genres[genre_id] for genre_id in genre_ids if genre_id in genres]
        # Join genre names into a comma-separated string for easier readability
        genre_text = ", ".join(genre_names)
        logging.info(f"genre_text {genre_text}.")  # Log the genre text
        
        # Create a text representation of the movie by combining title and overview
        movie_text = f"{movie['title']} {movie.get('overview', '')}"
        # Generate an embedding for the movie text using the sentence transformer model
        movie_embedding = model.encode(movie_text)
        
        # Create a document to be inserted into the MongoDB collection
        movie_doc = {
            "tmdb_id": movie["id"],  # Unique ID from TMDb
            "title": movie["title"],  # Movie title
            "overview": movie.get("overview", ""),  # Movie overview/description
            "release_date": movie.get("release_date", ""),  # Release date of the movie
            "popularity": movie.get("popularity", 0),  # Popularity score
            "poster_path": movie.get("poster_path", ""),  # Path to the movie poster image
            "vote_average": movie.get("vote_average", 0),  # Average user rating
            "vote_count": movie.get("vote_count", 0),  # Number of votes
            "genre_ids": genre_ids,  # List of genre IDs
            "genre_names": genre_names,  # List of genre names
            "movie_embedding": movie_embedding.tolist(),  # Embedding of the movie text as a list
             "origin": {
                "original_language": original_language,        # contoh: 'ko' untuk Korea
                "country_names": country_names                 # contoh: ['South Korea']
            }
        }
        
        # Insert or update the movie document in the MongoDB collection
        # Use `update_one` with `upsert=True` to insert new documents or update existing ones
        movies_collection.update_one(
            {"tmdb_id": movie["id"]},  # Query by TMDb ID to avoid duplicates
            {"$set": movie_doc},  # Update the document with the new data
            upsert=True  # Create a new document if it doesn't exist
        )

# Function to seed the database with multiple pages of movies from TMDb
def seed_database_from_tmdb(pages=1):
    # Fetch the list of genres once and reuse it for all movies
    genres = fetch_tmdb_genres()
    
    # Loop through the specified number of pages to fetch movies
    for page in range(1, pages + 1):
        logging.info(f"Inserted Page number: {page}")  # Log the current page being processed
        movies = fetch_tmdb_movies(page)  # Fetch movies for the current page
        
        # If no movies are returned, break out of the loop
        if not movies:
            break
        
        # Seed the fetched movies into the database
        seed_movies(movies, genres)

# Seed the database with movies from the first 500 pages of TMDb's popular movies
seed_database_from_tmdb(pages=500)

# Print a completion message after seeding the database
print("Database seeding completed!")