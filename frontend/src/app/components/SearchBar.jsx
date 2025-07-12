"use client";
import { ClockIcon } from "@heroicons/react/16/solid";

export default function SearchBar({ query, setQuery, handleSearch, history, showHistory, setShowHistory }) {
  const handleKeyUp = (event) => {
    if (event.key === "Enter") handleSearch();
  };

  return (
    <div className="relative w-full mb-4">
      <div className="flex items-center bg-gray-900/60 rounded-lg border border-gray-700 px-3 py-2 focus-within:ring-2 focus-within:ring-blue-500">
        <input
          type="text"
          className="w-full bg-transparent outline-none text-white placeholder-gray-400"
          placeholder="Recommend me an action movie..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyUp={handleKeyUp}
          onFocus={() => setShowHistory(false)}
        />
        <div
          className="ml-2 cursor-pointer"
          onClick={() => setShowHistory(!showHistory)}
        >
          <ClockIcon className="w-6 h-6 text-gray-400 hover:text-white transition-colors" />
        </div>
      </div>

      {showHistory && (
        <ul className="absolute right-0 top-14 w-full bg-gray-900 border border-gray-700 rounded-md shadow-lg z-10 max-h-48 overflow-y-auto">
          {history.length === 0 ? (
            <li className="p-3 text-gray-500 italic">No search history</li>
          ) : (
            history.map((item, index) => (
              <li
                key={index}
                className="p-3 text-white hover:bg-gray-700 cursor-pointer transition-colors"
                onClick={() => {
                  setQuery(item);
                  handleSearch();
                  setShowHistory(false);
                }}
              >
                {item}
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}
