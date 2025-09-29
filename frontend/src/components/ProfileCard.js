import React, { useState } from 'react';
import { MapPin, Building, GraduationCap, Linkedin, MessageSquare } from 'lucide-react';

function ProfileCard({ profile, apiBaseUrl = 'http://localhost:3001' }) {
  const [showFull, setShowFull] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // helper function to extract education from embedding_text
  const extractEducation = (embeddingText) => {
    if (!embeddingText) return '';
    const line = embeddingText.split('\n').find(l => l.startsWith('Education Details:'));
    if (!line) return '';
    const first = line.replace('Education Details: ', '').split(' | ')[0];
    return first
      .replace(/,?\s*Major:.*?(?:\)|$)/, '')
      .replace(/\s*\((?:\d{4}|\?)[–-](?:\d{4}|\?)\)\s*$/, '')
      .trim();
  };

  // message generation function with alerts
  const generateMessage = async () => {
    // get user context
    const yourContext = window.prompt('Tell us about yourself (e.g. software engineer at Microsoft, interested in AI, recent CS grad from UW...):');
    if (!yourContext || !yourContext.trim()) {
      window.alert('Please provide some context about yourself to personalize the message.');
      return;
    }

    // Get message tone
    const toneOptions = [
      'curious',
      'networking', 
      'collaborative',
      'casual'
    ];
    
    const toneLabels = [
      'Curious / Informational',
      'Job Seeking / Networking',
      'Collaborative / Partnership', 
      'Casual / Friendly'
    ];
    
    const toneIndex = window.prompt(`Choose message tone:\n1. Curious / Informational\n2. Job Seeking / Networking\n3. Collaborative / Partnership\n4. Casual / Friendly\n\nEnter number (1-4):`);
    
    if (!toneIndex || isNaN(toneIndex) || toneIndex < 1 || toneIndex > 4) {
      window.alert('Please select a valid tone option (1-4).');
      return;
    }
    
    const messageTone = toneOptions[toneIndex - 1];

    setIsGenerating(true);
    try {
      console.log('sending request to generate message:', { profile: profile.name, tone: messageTone, yourContext });
      
      const response = await fetch(`${apiBaseUrl}/api/generate-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          profile: profile,
          tone: messageTone,
          yourContext: yourContext
        }),
      });

      console.log('response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('error generating message:', errorData);
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('generated message:', data);
      
      // show generated message in alert
      const copyToClipboard = window.confirm(`Generated Message:\n\n${data.message}\n\n\nClick OK to copy to clipboard, or Cancel to just view.`);
      
      if (copyToClipboard) {
        try {
          await navigator.clipboard.writeText(data.message);
          window.alert('Message copied to clipboard!');
        } catch (err) {
          window.alert(`Message generated but couldn't copy to clipboard:\n\n${data.message}`);
        }
      }
      
    } catch (error) {
      console.error('error generating message:', error);
      window.alert(`Failed to generate message: ${error.message}. Please try again.`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <React.Fragment>
      <div className="break-inside-avoid bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-brew-brown-100 hover:border-brew-blue-200 mb-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h4 className="text-lg font-bold text-brew-brown-900 mb-1 truncate">
            {profile.name || 'Unknown'}
          </h4>
          <div className="flex items-center text-brew-brown-600 text-sm mb-2">
            <MapPin className="w-4 h-4 mr-1 flex-shrink-0" />
            <span className="truncate">
              {profile.city && profile.country_code 
                ? `${profile.city}, ${profile.country_code}`
                : 'Location not specified'
              }
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-1 bg-brew-blue-100 text-brew-blue-700 px-3 py-1 rounded-full text-sm font-medium ml-2">
          <span>{(profile.similarity_score * 100).toFixed(0)}% match</span>
        </div>
      </div>

      {/* Position & Company */}
      <div className="mb-3">
        <div className="flex items-start text-brew-brown-700 font-medium mb-1">
          <Building className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
          <span className="text-sm leading-tight">
            {profile.position || 'Position not specified'}
          </span>
        </div>
      </div>

      {/* Skills */}
      {profile.skills && profile.skills.length > 0 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {profile.skills.slice(0, 5).map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-brew-brown-100 text-brew-brown-700 rounded-md text-xs"
              >
                {skill}
              </span>
            ))}
            {profile.skills.length > 5 && (
              <span className="px-2 py-1 bg-brew-brown-200 text-brew-brown-600 rounded-md text-xs">
                +{profile.skills.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* About */}
      {profile.about && (
        <div className="mb-4">
          <p className="text-brew-brown-600 text-sm leading-relaxed">
            {showFull ? profile.about : `${profile.about.substring(0, 120)}...`}
          </p>
          {profile.about.length > 120 && (
            <button
              onClick={() => setShowFull(!showFull)}
              className="text-brew-blue-600 hover:text-brew-blue-700 text-sm font-medium mt-1"
            >
              {showFull ? 'Show less' : 'Read more'}
            </button>
          )}
        </div>
      )}

      {/* Education */}
      <div className="mb-4">
        <div className="flex items-start text-brew-brown-600 text-sm">
          <GraduationCap className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
          <span className="line-clamp-3">
            {extractEducation(profile.embedding_text) || 'Education not specified'}
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="pt-4 border-t border-brew-brown-100">
        <div className="space-y-3">
          {/* LinkedIn Link */}
          {profile.profile_url ? (
            <a
              href={profile.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-brew-blue-600 to-brew-blue-700 text-white py-2 px-4 rounded-xl hover:from-brew-blue-700 hover:to-brew-blue-800 transition-all duration-200 text-sm font-medium"
            >
              <Linkedin className="w-4 h-4" />
              <span>View LinkedIn Profile</span>
            </a>
          ) : (
            <div className="w-full flex items-center justify-center space-x-2 bg-gray-300 text-gray-500 py-2 px-4 rounded-xl text-sm font-medium cursor-not-allowed">
              <Linkedin className="w-4 h-4" />
              <span>LinkedIn not available</span>
            </div>
          )}

          {/* Message Generation */}
          <button
            onClick={generateMessage}
            disabled={isGenerating}
            className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-brew-brown-600 to-brew-brown-700 text-white py-2 px-4 rounded-xl hover:from-brew-brown-700 hover:to-brew-brown-800 transition-all duration-200 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <MessageSquare className="w-4 h-4" />
            <span>{isGenerating ? 'Generating...' : 'Generate Message'}</span>
          </button>

        </div>
      </div>
      </div>

    </React.Fragment>
  );
}

export default ProfileCard;