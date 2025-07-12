# Import necessary libraries
from flask import Flask, request, jsonify  # For creating the Flask API server and handling HTTP requests
from pymongo import MongoClient, TEXT  # To interact with MongoDB database
from bson import ObjectId  # To handle MongoDB Object IDs
from sentence_transformers import SentenceTransformer  # For generating embeddings from text
import numpy as np  # For numerical operations (though not directly used in this snippet)
from generator import converse_with_llm  # Custom module to interact with an LLM for movie recommendations
from apiKey import MONGO_CONNECTION_STRING  # Import MongoDB connection string from a separate file
from flask_cors import CORS  # To enable Cross-Origin Resource Sharing (CORS) for the API
import spacy  # For natural language processing (NLP) tasks like tokenization and keyword extraction
import logging  # For logging information during execution

# Set up logging configuration to display logs at the INFO level
logging.basicConfig(level=logging.INFO)

# Connect to MongoDB using the provided connection string
client = MongoClient(MONGO_CONNECTION_STRING)
db = client["movie_app"]  # Access the "movie_app" database
movies_collection = db["movies"]  # Access the "movies" collection within the database
history_collection = db["search_history"]  # Access the "search_history" collection for storing query history

# Load a pre-trained spaCy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Load a pre-trained sentence transformer model for generating embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS for all routes under /api/*
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Define genre synonyms to map user input to specific genres
GENRE_SYNONYMS = {
    "romance": ["romance", "romantic", "love", "rom-com", "relationship", "heartwarming"],
    "action": ["action", "adventure", "fight", "combat", "explosions", "chase", "martial arts"],
    "comedy": ["comedy", "funny", "humor", "satire", "laugh", "parody", "slapstick"],
    "horror": ["horror", "scary", "thriller", "fear", "ghost", "haunted", "supernatural"],
    "sci-fi": ["sci-fi", "science fiction", "space", "alien", "future", "technology", "time travel", "robot"],
    "fantasy": ["fantasy", "magic", "mythical", "dragons", "sorcery", "medieval", "epic quest"],
    "drama": ["drama", "emotional", "realistic", "life story", "tragedy", "family drama", "serious tone", "slice of life"],
    "mystery": ["mystery", "detective", "investigation", "whodunit", "suspense", "unsolved", "clues"],
    "crime": ["crime", "mafia", "heist", "gangster", "law", "courtroom", "underworld", "criminal"],
    "animation": ["animation", "animated", "cartoon", "pixar", "disney", "anime", "family-friendly"],
    "documentary": ["documentary", "true story", "non-fiction", "biography", "docuseries", "real events"],
    "biography": ["biography", "based on true story", "real life", "famous person", "historical figure"],
    "war": ["war", "military", "battle", "soldier", "army", "conflict", "historical war"],
    "history": ["history", "historical", "period drama", "ancient", "past events", "timepiece"],
    "family": ["family", "kids", "wholesome", "all ages", "lighthearted", "feel-good"],
    "musical": ["musical", "singing", "dancing", "music", "performance", "broadway", "songs"],
    "sports": ["sports", "athlete", "competition", "football", "basketball", "boxing", "team", "coach"],
    "western": ["western", "cowboy", "wild west", "gunslinger", "sheriff", "desert"],
    "spy": ["spy", "espionage", "secret agent", "CIA", "MI6", "undercover", "covert"],
    "post-apocalyptic": ["post-apocalyptic", "wasteland", "end of the world", "dystopian", "collapse", "survival"],
    "psychological": ["psychological", "mind-bending", "twist", "mental", "inner conflict", "inception-like"],
    "superhero": ["superhero", "marvel", "dc", "powers", "hero", "villain", "mutant", "saving the world"],
    "zombie": ["zombie", "undead", "infected", "outbreak", "virus", "walking dead", "apocalypse"],
    "samurai": ["samurai", "ronin", "katana", "feudal japan", "bushido", "shogun", "edo era"],
}

ORIGIN_SYNONYMS = {
    "korean": ["korean", "south korea", "k-drama", "k-movie", "film korea"],
    "japanese": ["japanese", "japan", "j-drama", "japanese film", "film jepang"],
    "indonesian": ["indonesian", "indonesia", "indo", "local film", "film indonesia"],
    "french": ["french", "france", "film prancis"],
    "indian": ["indian", "bollywood", "india", "hindi film", "tamil", "telugu", "film india"],
    "thai": ["thai", "thailand", "film thailand", "thai drama", "thai movie"],
    "chinese": ["chinese", "china", "film china", "chinese movie", "c-drama"],
    "british": ["british", "uk", "united kingdom", "film inggris", "british film"],
    "american": ["american", "usa", "united states", "hollywood", "film amerika"],
    "spanish": ["spanish", "spain", "film spanyol", "spanish movie"],
    "german": ["german", "germany", "film jerman"],
    "turkish": ["turkish", "turkey", "film turki", "turkish drama"],
    "iranian": ["iranian", "iran", "film iran"],
    "russian": ["russian", "russia", "film rusia"],
    "philippine": ["philippine", "filipino", "philippines", "film filipina"]
}

THEME_SYNONYMS = {
    "mind-bending": [
        "mind-bending", "thought-provoking", "complex", "inception", "makes you think", 
        "twisted plot", "puzzle", "psychological twist", "confusing at first"
    ],
    "emotional": [
        "emotional", "heartbreaking", "tearjerker", "sad", "touching", "soul-crushing", 
        "makes you cry", "melancholy", "heartfelt", "tragic"
    ],
    "inspirational": [
        "inspiring", "motivational", "life-changing", "uplifting", "powerful message", 
        "based on true events", "overcoming odds", "heroic journey", "resilience"
    ],
    "moral": [
        "moral lesson", "philosophical", "deep message", "values", "ethical dilemma", 
        "teaches something", "social commentary", "life meaning", "reflective"
    ],
    "psychological": [
        "psychological", "mental", "manipulative", "dark thoughts", "dual personality", 
        "internal conflict", "identity crisis", "emotional breakdown", "mind games"
    ],
    "twist": [
        "plot twist", "unexpected ending", "shocking", "surprising turn", "unpredictable", 
        "revealing twist", "big reveal", "twisted", "double meaning"
    ]
}

def match_origin(keywords):
    """
    Match user input keywords to an origin (country) using predefined synonyms.
    Args:
        keywords (list): List of keywords extracted from the query.
    Returns:
        str or None: Matched origin or None if no match is found.
    """
    for keyword in keywords:
        for origin, synonyms in ORIGIN_SYNONYMS.items():
            if keyword.lower() in synonyms:
                return origin
    return None

def match_theme(keywords):
    """
    Match user input keywords to a theme/mood using predefined synonyms.
    Args:
        keywords (list): List of keywords extracted from the query.
    Returns:
        str or None: Matched theme or None if no match is found.
    """
    for keyword in keywords:
        for theme, synonyms in THEME_SYNONYMS.items():
            if keyword.lower() in synonyms:
                return theme
    return None

# Function to parse advanced filters from the user query
def parse_advanced_filters(query):
    """
    Parse the query to extract advanced filters for movie search.
    Args:
        query (str): User input query.
    Returns:
        dict: Filters like minimum rating or vote count.
    """
    filters = {}
    if "top" in query.lower() or "high-rated" in query.lower():
        filters["vote_average"] = {"$gte": 8.5}  # Filter for high-rated movies
    if "popular" in query.lower():
        filters["vote_count"] = {"$gte": 500}  # Filter for popular movies
    if "recent" in query.lower():
        filters["release_date"] = {"$gte": "2020-01-01"}  # Filter for recent movies
    if "old" in query.lower():
        filters["release_date"] = {"$lte": "2000-01-01"}  # Filter for older movies
    
    return filters

# Function to clean MongoDB documents by converting ObjectIDs to strings
def clean_document(doc):
    doc["_id"] = str(doc["_id"])  # Convert MongoDB's ObjectId to a string for JSON serialization
    return doc

# Function to retrieve similar movies based on vector similarity
def retrieve_similar_movies(query, n=5):
    """
    Retrieve similar movies based on vector similarity.
    Args:
        query (str): User input query.
        n (int): Number of similar movies to retrieve.
    Returns:
        list: List of similar movies with metadata.
    """
    query_embedding = model.encode(query).tolist()  # Generate an embedding for the query
    filters = parse_advanced_filters(query)  # Extract advanced filters from the query
    
    # Perform vector similarity search using MongoDB's $vectorSearch operator
    similar_movies_search = movies_collection.aggregate(
        [
            {
                "$vectorSearch": {
                    "index": "movie_index",  # Name of the vector index in MongoDB
                    "queryVector": query_embedding,  # Query vector for similarity search
                    "path": "movie_embedding",  # Path to the movie embeddings in the collection
                    "k": n,  # Number of nearest neighbors to retrieve
                    "numCandidates": 1000,  # Number of candidates to consider during search
                    "limit": 20,  # Limit the number of results returned
                }
            },
            {"$match": filters},  # Apply additional filters (e.g., vote count, release date)
            {
                "$project": {
                    "title": 1,
                    "overview": 1,
                    "poster_path": 1,
                    "vote_average": 1,
                    "vote_count": 1,
                    "release_date": 1,
                    "score": {"$meta": "searchScore"},  # Include the similarity score
                }
            },
        ]
    )
    similar_movies = [clean_document(movie) for movie in similar_movies_search]  # Clean the results
    return similar_movies

# Function to retrieve similar movies by genre
def retrieve_similar_movies_by_genre(genre, n=150, query=""):
    """
    Retrieve similar movies based on genre matching.
    Args:
        genre (str): Genre to match.
        n (int): Number of similar movies to retrieve.
        query (str): User input query for additional filtering.
    Returns:
        list: List of similar movies with metadata.
    """
    filters = parse_advanced_filters(query)  # Extract advanced filters from the query
    filters["genre_names"] = {"$regex": f"^{genre}", "$options": "i"}  # Match genre names case-insensitively
    
    # Find movies that match the genre and apply additional filters
    matching_movies = (
        movies_collection.find(
            filters,
            {
                "title": 1,
                "overview": 1,
                "poster_path": 1,
                "vote_average": 1,
                "vote_count": 1,
                "release_date": 1,
                "genre_names": 1,
            },
        )
        .sort("popularity", -1)  # Sort by popularity in descending order
        .limit(n)  # Limit the number of results
    )
    similar_movies = [clean_document(movie) for movie in matching_movies]  # Clean the results
    return similar_movies

# Function to process the user query and extract keywords
def process_query(query):
    """
    Process the user query to extract relevant keywords using NLP.
    Args:
        query (str): User input query.
    Returns:
        list: List of extracted keywords.
    """
    doc = nlp(query)  # Process the query using spaCy
    keywords = [
        chunk.text.lower() for chunk in doc.noun_chunks  # Extract noun chunks
    ] + [
        token.text.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop  # Extract nouns, proper nouns, and adjectives, excluding stopwords
    ]
    return list(set(keywords))  # Return unique keywords

# Function to match user input to a genre using genre synonyms
def match_genre(keywords):
    """
    Match user input keywords to a genre using predefined genre synonyms.
    Args:
        keywords (list): List of keywords extracted from the query.
    Returns:
        str or None: Matched genre or None if no match is found.
    """
    for keyword in keywords:
        for genre, synonyms in GENRE_SYNONYMS.items():
            if keyword.lower() in synonyms:  # Check if the keyword matches any genre synonym
                return genre
    return None

# Route to handle user queries and provide movie recommendations
@app.route("/api/query", methods=["POST"])
def handle_query():
    """
    Handle POST requests to /api/query for movie recommendations.
    Expects a JSON payload with a "query" field containing the user's input.
    Returns:
        JSON response with similar movies and a recommendation from the LLM.
    """
    data = request.json  # Parse the incoming JSON payload
    query = data.get("query", "")  # Extract the user's query
    input_prompt = process_query(query)  # Process the query to extract keywords
    
    # Check if the query has been processed before and exists in the history collection
    existing_entry = history_collection.find_one({"query": query})
    if existing_entry:
        return jsonify(existing_entry["result"])  # Return cached result if available
    
    genre_match = match_genre(input_prompt)  # Try to match the query to a genre
    print("genre_match", genre_match)  # Log the matched genre (if any)
    
    theme_match = match_theme(input_prompt)
    print("theme_match:", theme_match)

    origin_match = match_origin(input_prompt)
    print("origin_match:", origin_match)

    # If a genre match is found, retrieve similar movies by genre
    if genre_match or theme_match or origin_match:
        cleaned_query = " ".join(input_prompt)
        parts = [genre_match, theme_match, origin_match]
        enriched_query = " ".join([p for p in parts if p]) + " " + cleaned_query
        similar_movies = retrieve_similar_movies(enriched_query.strip())
    else:
        cleaned_query = " ".join(input_prompt)  # Join keywords into a single string
        similar_movies = retrieve_similar_movies(cleaned_query)  # Retrieve similar movies using vector similarity
    
    # Prepare a prompt for the LLM to generate a recommendation
    similar_movie_info = "\n".join([f"{movie['title']}" for movie in similar_movies])
    prompt = f"""
    Here are some similar movies I found: {similar_movie_info}
    based on user's query :{query}
    and explain why """
    
    # Generate a recommendation using the LLM
    recommendation = converse_with_llm(prompt)
    
    # Prepare the final result containing similar movies and the recommendation
    result = {"similar_movies": similar_movies, "recommendation": recommendation}
    
    # Cache the result in the history collection if there are similar movies
    if len(similar_movies) > 0:
        history_collection.insert_one({"query": query, "result": result})
    
    return jsonify(result)  # Return the result as a JSON response

# Route to fetch the history of previous search queries
@app.route("/api/history", methods=["GET"])
def get_history():
    """
    Fetches all previous search queries and their results.
    Returns:
        JSON response with a list of previous queries.
    """
    history = history_collection.find({}, {"_id": 0, "query": 1})  # Retrieve only the query field from history
    return jsonify([entry["query"] for entry in history])  # Return a list of queries

# Run the Flask app in debug mode on port 5001
if __name__ == "__main__":
    app.run(debug=True, port=5001)