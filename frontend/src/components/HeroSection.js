import React from 'react';
import { Search } from 'lucide-react';

function HeroSection({ query, setQuery, handleSearch, loading, numResults, setNumResults, handleExampleClick, exampleQueries }) {
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch(e);
        }
        };

  return (
    <div className="relative mb-16">
      {/* Main Content */}
      <div className="relative z-10 text-center">
        {/* Animated Title */}
        <div className="mb-12">
          <h2 className="text-5xl md:text-7xl font-black text-brew-brown-900 mb-8 mt-6 leading-tight">
            Find Your Perfect
            <br />
            <span className="bg-gradient-to-r from-brew-brown-600 via-brew-blue-600 to-brew-brown-600 bg-clip-text text-transparent animate-gradient">
              Coffee Chat
            </span>
          </h2>
          <p className="text-lg md:text-xl text-brew-brown-600 max-w-3xl mx-auto leading-relaxed">
            Discover interesting people to connect with based on their experiences, 
            interests, and career paths.
          </p>
        </div>

        {/* Search Section */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="relative">
            {/* Search Input */}
            <div className="relative bg-white/20 backdrop-blur-md rounded-3xl p-2 shadow-2xl border border-white/30">
              <div className="absolute inset-0 bg-gradient-to-r from-brew-brown-500/10 to-brew-blue-500/10 rounded-3xl"></div>
              <div className="relative flex items-center">
                <div className="absolute left-6 flex items-center pointer-events-none">
                  <Search className="h-6 w-6 text-brew-brown-400" />
                </div>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder='e.g. "Waterloo grad interested in fintech"'
                  className="w-full pl-16 pr-32 py-4 text-lg bg-transparent border-0 focus:outline-none placeholder-brew-brown-400 text-brew-brown-900"
                />
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="absolute right-2 top-2 bottom-2 px-8 bg-gradient-to-r from-brew-brown-600 to-brew-blue-600 text-white rounded-2xl font-semibold hover:from-brew-brown-700 hover:to-brew-blue-700 transition-all duration-300 disabled:opacity-50 shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>

            {/* Number of Results */}
            <div className="mt-10">
              <div className="flex items-center justify-center space-x-4">
                <span className="text-brew-brown-700 font-medium">Results:</span>
                <div className="flex items-center space-x-2">
                  <input
                    type="range"
                    min="5"
                    max="20"
                    value={numResults}
                    onChange={(e) => setNumResults(parseInt(e.target.value))}
                    className="w-48 h-2 bg-gradient-to-r from-brew-brown-200 to-brew-blue-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <span className="text-brew-brown-900 font-bold text-lg min-w-[3rem]">{numResults}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Example Queries */}
        <div className="mb-8">
          <p className="text-brew-blue-600 mb-6 text-lg font-medium">Try these examples:</p>
          <div className="flex flex-wrap justify-center gap-3">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="group px-6 py-3 bg-white/40 hover:bg-white/60 backdrop-blur-sm text-brew-brown-700 rounded-2xl border border-white/50 hover:border-brew-blue-300 transition-all duration-300 text-sm font-medium shadow-lg hover:shadow-xl transform hover:scale-105 hover:-translate-y-1"
              >
                <span className="group-hover:text-brew-blue-600 transition-colors duration-300">
                  {example}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default HeroSection;