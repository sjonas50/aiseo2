import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Copy, Check, Download, Maximize2 } from 'lucide-react';
import { QueryResult } from '../services/api';

interface ResponseDisplayProps {
  provider: string;
  result: QueryResult | null;
  isLoading: boolean;
  onExpand?: () => void;
}

const ResponseDisplay: React.FC<ResponseDisplayProps> = ({
  provider,
  result,
  isLoading,
  onExpand,
}) => {
  const [copied, setCopied] = useState(false);
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (result?.response) {
      setIsTyping(true);
      setDisplayedText('');
      
      // Typewriter effect
      const text = result.response;
      let index = 0;
      const typingSpeed = 10; // Faster typing for better UX
      
      const interval = setInterval(() => {
        if (index < text.length) {
          setDisplayedText((prev) => prev + text.slice(index, Math.min(index + 5, text.length)));
          index += 5;
        } else {
          setIsTyping(false);
          clearInterval(interval);
        }
      }, typingSpeed);

      return () => clearInterval(interval);
    }
  }, [result?.response]);

  const handleCopy = () => {
    if (result?.response) {
      navigator.clipboard.writeText(result.response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getProviderColor = (providerId: string) => {
    switch (providerId.toLowerCase()) {
      case 'openai':
        return 'border-green-500/30 bg-green-500/5';
      case 'anthropic':
        return 'border-orange-500/30 bg-orange-500/5';
      case 'google':
        return 'border-blue-500/30 bg-blue-500/5';
      case 'perplexity':
        return 'border-purple-500/30 bg-purple-500/5';
      case 'google_search':
        return 'border-yellow-500/30 bg-yellow-500/5';
      default:
        return 'border-gray-500/30 bg-gray-500/5';
    }
  };

  const renderGoogleSearchResults = () => {
    if (!result?.response || typeof result.response !== 'string') return null;
    
    try {
      // Parse Google Search results if they're in a specific format
      const searchResults = JSON.parse(result.response);
      if (Array.isArray(searchResults)) {
        return (
          <div className="space-y-3">
            {searchResults.map((item: any, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-3 bg-background/50 rounded-lg hover:bg-background/80 transition-colors"
              >
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent hover:underline font-medium"
                >
                  {item.title}
                </a>
                <p className="text-sm text-gray-400 mt-1">{item.snippet}</p>
                <p className="text-xs text-gray-500 mt-1">{item.link}</p>
              </motion.div>
            ))}
          </div>
        );
      }
    } catch {
      // If not JSON, render as regular text
      return null;
    }
    
    return null;
  };

  return (
    <motion.div
      className={`card ${getProviderColor(provider)} relative`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white capitalize">{provider}</h3>
          {result?.model && (
            <p className="text-sm text-gray-400">{result.model}</p>
          )}
        </div>
        
        {/* Action Buttons */}
        <div className="flex gap-2">
          {onExpand && (
            <button
              onClick={onExpand}
              className="p-2 bg-background/50 rounded-lg hover:bg-background/80 transition-colors"
              title="Expand"
            >
              <Maximize2 className="w-4 h-4 text-gray-400" />
            </button>
          )}
          <button
            onClick={handleCopy}
            className="p-2 bg-background/50 rounded-lg hover:bg-background/80 transition-colors"
            disabled={!result?.response}
            title="Copy"
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-500" />
            ) : (
              <Copy className="w-4 h-4 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="relative">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center py-12"
            >
              <div className="flex space-x-2">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-3 h-3 bg-accent rounded-full"
                    animate={{
                      y: [0, -10, 0],
                    }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.1,
                    }}
                  />
                ))}
              </div>
            </motion.div>
          ) : result?.error ? (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="py-6"
            >
              <p className="text-red-400">Error: {result.error}</p>
            </motion.div>
          ) : result?.response ? (
            <motion.div
              key="content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="prose prose-invert max-w-none"
            >
              {provider.toLowerCase() === 'google_search' ? (
                renderGoogleSearchResults() || (
                  <div className="whitespace-pre-wrap text-gray-300 text-sm">
                    {displayedText}
                    {isTyping && <span className="animate-pulse">▊</span>}
                  </div>
                )
              ) : (
                <div className="whitespace-pre-wrap text-gray-300 text-sm leading-relaxed">
                  {displayedText}
                  {isTyping && <span className="animate-pulse">▊</span>}
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="py-6"
            >
              <p className="text-gray-500">Waiting for response...</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default ResponseDisplay;