import React, { useState } from 'react';
import axios from 'axios';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import ResultsSection from './components/ResultsSection';
import './App.css';

const API_BASE_URL = 'http://localhost:3001';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [numResults, setNumResults] = useState(12);

  const exampleQueries = [
    "software engineer interested in AI",
    "marketing professional with startup experience", 
    "data scientist from Toronto",
    "university graduate in computer science",
    "entrepreneur in fintech"
  ];

  const searchProfiles = async (searchQuery) => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/search`, {
        params: { query: searchQuery, num_results: numResults }
      });
      setResults(response.data);
    } catch (err) {
      setError('Unable to connect to the search service. Make sure the backend is running!');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    searchProfiles(query);
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
    searchProfiles(exampleQuery);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brew-brown-50 to-brew-blue-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <HeroSection 
          query={query}
          setQuery={setQuery}
          handleSearch={handleSearch}
          loading={loading}
          numResults={numResults}
          setNumResults={setNumResults}
          handleExampleClick={handleExampleClick}
          exampleQueries={exampleQueries}
        />

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-8 text-red-700">
            {error}
          </div>
        )}

        <ResultsSection 
          results={results}
          loading={loading}
          query={query}
          apiBaseUrl={API_BASE_URL}
        />
      </main>
    </div>
  );
}

export default App;