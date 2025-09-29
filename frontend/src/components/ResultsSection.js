import React from 'react';
import { Search } from 'lucide-react';
import ProfileCard from './ProfileCard';

function ResultsSection({ results, loading, query, apiBaseUrl }) {
  if (results.length > 0) {
    return (
      <div className="animate-fadeInUp">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-brew-brown-900">
            Found {results.length} profiles
          </h3>
          <div className="text-brew-brown-600">
            Sorted by relevance
          </div>
        </div>
        
        {/* 3 Column Grid */}
        <div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
          {results.map((profile, index) => (
            <ProfileCard key={index} profile={profile} apiBaseUrl={apiBaseUrl} />
          ))}
        </div>
      </div>
    );
  }

  if (!loading && results.length === 0 && query) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 bg-brew-brown-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Search className="w-12 h-12 text-brew-brown-400" />
        </div>
        <h3 className="text-xl font-semibold text-brew-brown-700 mb-2">
          No profiles found
        </h3>
        <p className="text-brew-brown-500">
          Try a different search term or check the examples above.
        </p>
      </div>
    );
  }

  // show loading state or default state
  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 bg-brew-brown-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Search className="w-12 h-12 text-brew-brown-400 animate-spin" />
        </div>
        <h3 className="text-xl font-semibold text-brew-brown-700 mb-2">
          Searching...
        </h3>
        <p className="text-brew-brown-500">
          Finding the perfect coffee chat matches for you.
        </p>
      </div>
    );
  }

  // default state when no search has been made
  return (
    <div className="text-center py-12">
      <div className="w-24 h-24 bg-brew-brown-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <Search className="w-12 h-12 text-brew-brown-400" />
      </div>
      <h3 className="text-xl font-semibold text-brew-brown-700 mb-2">
        Ready to find your perfect coffee chat?
      </h3>
      <p className="text-brew-brown-500">
        Use the search bar above or try one of the example queries.
      </p>
    </div>
  );
}

export default ResultsSection;