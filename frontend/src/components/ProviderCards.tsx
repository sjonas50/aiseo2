import React from 'react';
import { motion } from 'framer-motion';
import { Check, X, Loader2, Bot, Globe, Search, Brain } from 'lucide-react';
import { Provider } from '../services/api';

interface ProviderCardsProps {
  providers: Provider[];
  selectedProviders: string[];
  onToggleProvider: (providerId: string) => void;
  providerStatus: Record<string, 'idle' | 'loading' | 'success' | 'error'>;
}

const ProviderCards: React.FC<ProviderCardsProps> = ({
  providers,
  selectedProviders,
  onToggleProvider,
  providerStatus,
}) => {
  const getProviderIcon = (providerId: string) => {
    switch (providerId) {
      case 'openai':
        return <Bot className="w-8 h-8" />;
      case 'anthropic':
        return <Brain className="w-8 h-8" />;
      case 'google':
        return <Globe className="w-8 h-8" />;
      case 'google_search':
        return <Search className="w-8 h-8" />;
      default:
        return <Bot className="w-8 h-8" />;
    }
  };

  const getProviderColor = (providerId: string) => {
    switch (providerId) {
      case 'openai':
        return 'from-green-500 to-emerald-600';
      case 'anthropic':
        return 'from-orange-500 to-red-600';
      case 'google':
        return 'from-blue-500 to-indigo-600';
      case 'perplexity':
        return 'from-purple-500 to-pink-600';
      case 'google_search':
        return 'from-yellow-500 to-orange-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'loading':
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            <Loader2 className="w-5 h-5 text-accent" />
          </motion.div>
        );
      case 'success':
        return <Check className="w-5 h-5 text-green-500" />;
      case 'error':
        return <X className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {providers.map((provider, index) => {
        const isSelected = selectedProviders.includes(provider.id);
        const status = providerStatus[provider.id] || 'idle';

        return (
          <motion.div
            key={provider.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <button
              onClick={() => onToggleProvider(provider.id)}
              className={`w-full p-6 rounded-xl border transition-all duration-300 ${
                isSelected
                  ? 'bg-card border-accent shadow-lg'
                  : 'bg-card/50 border-border hover:border-accent/50'
              }`}
              disabled={status === 'loading'}
            >
              {/* Provider Icon with Gradient Background */}
              <div className="flex justify-between items-start mb-4">
                <div
                  className={`p-3 rounded-lg bg-gradient-to-br ${getProviderColor(
                    provider.id
                  )} text-white`}
                >
                  {getProviderIcon(provider.id)}
                </div>
                
                {/* Status Indicator */}
                <div className="flex items-center space-x-2">
                  {getStatusIcon(status)}
                  {isSelected && status === 'idle' && (
                    <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
                  )}
                </div>
              </div>

              {/* Provider Name */}
              <h3 className="text-lg font-semibold text-white mb-1 text-left">
                {provider.name}
              </h3>

              {/* Model Info */}
              {provider.model && (
                <p className="text-sm text-gray-400 text-left truncate">
                  {provider.model}
                </p>
              )}

              {/* Selection Indicator */}
              <div className="mt-4 flex justify-between items-center">
                <span
                  className={`text-xs font-medium ${
                    isSelected ? 'text-accent' : 'text-gray-500'
                  }`}
                >
                  {isSelected ? 'Selected' : 'Click to select'}
                </span>
                
                {/* Checkbox */}
                <div
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-200 ${
                    isSelected
                      ? 'bg-accent border-accent'
                      : 'border-gray-600 hover:border-accent/50'
                  }`}
                >
                  {isSelected && <Check className="w-3 h-3 text-white" />}
                </div>
              </div>
            </button>
          </motion.div>
        );
      })}
    </div>
  );
};

export default ProviderCards;