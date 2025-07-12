import React, { useState } from 'react';
import { Star, Calendar, Users } from 'lucide-react';

export default function MovieList({ movies }) {
  const [hoveredMovie, setHoveredMovie] = useState(null);

  const getRatingColor = (rating) => {
    if (rating >= 8) return 'text-green-400';
    if (rating >= 7) return 'text-yellow-400';
    if (rating >= 6) return 'text-orange-400';
    return 'text-red-400';
  };

  const getRatingBadgeColor = (rating) => {
    if (rating >= 8) return 'bg-green-500';
    if (rating >= 7) return 'bg-yellow-500';
    if (rating >= 6) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4 p-4">
      {movies
        .filter((movie) => movie.vote_average !== 0)
        .map((movie, index) => (
          <div key={movie.id || index}>
            <div
              className="group relative bg-slate-800 rounded-2xl overflow-hidden border border-slate-700 hover:border-slate-600 transition-all duration-300 hover:shadow-xl"
              onMouseEnter={() => setHoveredMovie(index)}
              onMouseLeave={() => setHoveredMovie(null)}
            >
              {/* Movie Poster */}
              <div className="relative aspect-[2/3] overflow-hidden">
                <img
                  src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                  alt={`${movie.title} poster`}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                />
            
                {/* Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
            
                {/* Rating Badge */}
                <div className={`absolute top-3 right-3 ${getRatingBadgeColor(movie.vote_average)} rounded-full px-2 py-1 flex items-center gap-1`}>
                  <Star className="w-3 h-3 text-white fill-white" />
                  <span className="text-white text-xs font-bold">
                    {movie.vote_average.toFixed(1)}
                  </span>
                </div>
                {/* Movie Info Overlay */}
                <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                  {/* Only show on hover */}
                  <div className="transform translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
                    {/* Overview Movie
                    <p className="text-gray-200 text-sm leading-relaxed mb-3 line-clamp-3">
                      {movie.overview?.length > 120
                        ? `${movie.overview.substring(0, 120)}...`
                        : movie.overview}
                    </p> */}
            
                    {/* Add to List Button */}
                    <button
                      className="w-full bg-white/20 backdrop-blur-sm border border-white/30 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-white/30 transition-colors duration-200"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Fungsi akan ditambahkan nanti
                      }}
                    >
                      + Add to List
                    </button>
                  </div>
                </div>
                {/* Hover Overlay Effect */}
                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>
            </div>
            <div>
              <h3 className="font-bold text-base mb-1 line-clamp-1 mt-2">
                {movie.title}
              </h3>
              <div className="flex items-center gap-3 text-sm text-gray-300">
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  <span>{movie.release_date?.split("-")[0]}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="w-3 h-3" />
                  <span>{movie.vote_count} votes</span>
                </div>
              </div>
            </div>
          </div>
      ))}
    </div>
  );
}