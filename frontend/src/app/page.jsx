"use client";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import SearchBar from "./components/SearchBar";
import LoadingSpinner from "./components/LoadingSpinner";
import MovieList from "./movies/components/MovieList";
import Head from 'next/head';

export default function MoviesPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch("http://localhost:5001/api/history");
        const data = await response.json();
        setHistory(data);
      } catch (error) {
        console.error("Error fetching history:", error);
      }
    };
    fetchHistory();
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:5001/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setResult(data);
      if (!history.includes(query)) {
        setHistory((prev) => [...prev, query]);
      }
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center px-2 pb-20 sm:px-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start w-full">
        <div className="p-6 w-full">
          <header className="text-center">
            <h1 className="text-5xl font-bold mb-4">
              Welcome to <span className="text-red-500">Movix</span>
            </h1>
            <p className="text-lg font-medium mb-4">
              Your AI-Powered Movie Recommendation Website
            </p>
            <p className="text-md mb-8">
              Just type a genre, actor, or theme — and let our smart system suggest the perfect movie for your mood!
            </p>
          </header>

          <SearchBar
            query={query}
            setQuery={setQuery}
            handleSearch={handleSearch}
            history={history}
            showHistory={showHistory}
            setShowHistory={setShowHistory}
          />

          <button
            className={`px-5 py-2 rounded-lg font-medium transition-colors duration-200 shadow-sm
              ${loading
                ? "bg-red-400 text-white cursor-not-allowed opacity-70"
                : "bg-red-500 hover:bg-red-600 text-white"}
            `}
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? "Loading..." : "Get Recommendations"}
          </button>


          {loading && <LoadingSpinner />}

          {result && !loading && (
            <div className="mt-6 space-y-6">
              <div className="movie-recommendation markdown-red bg-gray-900/60 p-6 rounded-lg shadow-md border border-gray-700">
                <h2 className="text-2xl font-bold text-white mb-4 border-b border-gray-600 pb-2">
                  🎥 LLM Movie Recommendation
                </h2>
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown>{result.recommendation}</ReactMarkdown>
                </div>

              </div>

              <div>
                <h3 className="text-xl font-semibold text-white mb-3">🍿 Top Movies:</h3>
                <MovieList movies={result.similar_movies} />
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
