import React from 'react';
import { Coffee } from 'lucide-react';

function Header() {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-brew-brown-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center h-20">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-brew-brown-600 to-brew-blue-600 rounded-xl">
              <Coffee className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-brew-brown-900">Brew</h1>
              <p className="text-sm text-brew-brown-600">Better Connections</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;