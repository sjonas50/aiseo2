import React, { useState, useEffect, useCallback } from 'react';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import QueryInput from './components/QueryInput';
import ProviderCards from './components/ProviderCards';
import ResponseDisplay from './components/ResponseDisplay';
import { apiService, wsManager, Provider, QueryResult } from './services/api';
import { Sparkles } from 'lucide-react';

// Create a query client
const queryClient = new QueryClient();

function AppContent() {
  const [selectedProviders, setSelectedProviders] = useState<string[]>([]);
  const [currentQueryId, setCurrentQueryId] = useState<string | null>(null);
  const [isQuerying, setIsQuerying] = useState(false);
  const [providerStatus, setProviderStatus] = useState<Record<string, 'idle' | 'loading' | 'success' | 'error'>>({});
  const [results, setResults] = useState<Record<string, QueryResult>>({});

  // Fetch providers
  const { data: providersData, isLoading: isLoadingProviders } = useQuery({
    queryKey: ['providers'],
    queryFn: apiService.getProviders,
  });

  // Auto-select all providers on load
  useEffect(() => {
    if (providersData?.providers) {
      setSelectedProviders(providersData.providers.map(p => p.id));
    }
  }, [providersData]);

  // Set up WebSocket connection
  useEffect(() => {
    const socket = wsManager.connect();

    // Listen for WebSocket events
    wsManager.on('provider_start', (data: any) => {
      setProviderStatus(prev => ({ ...prev, [data.provider]: 'loading' }));
    });

    wsManager.on('provider_complete', (data: any) => {
      setProviderStatus(prev => ({ ...prev, [data.provider]: 'success' }));
      setResults(prev => ({ ...prev, [data.provider]: data.result }));
    });

    wsManager.on('query_complete', (data: any) => {
      setIsQuerying(false);
    });

    wsManager.on('query_error', (data: any) => {
      setIsQuerying(false);
      console.error('Query error:', data.error);
    });

    return () => {
      wsManager.disconnect();
    };
  }, []);

  const handleSubmitQuery = useCallback(async (query: string) => {
    if (selectedProviders.length === 0) {
      alert('Please select at least one provider');
      return;
    }

    setIsQuerying(true);
    setResults({});
    setProviderStatus({});

    try {
      const response = await apiService.submitQuery(query, selectedProviders);
      setCurrentQueryId(response.query_id);
      
      // Join the WebSocket room for this query
      wsManager.joinQuery(response.query_id);
    } catch (error) {
      console.error('Failed to submit query:', error);
      setIsQuerying(false);
    }
  }, [selectedProviders]);

  const toggleProvider = (providerId: string) => {
    setSelectedProviders(prev =>
      prev.includes(providerId)
        ? prev.filter(id => id !== providerId)
        : [...prev, providerId]
    );
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      {/* Hero Section */}
      <section className="pt-24 pb-12 px-4">
        <div className="container mx-auto">
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <motion.div
              className="inline-flex items-center justify-center space-x-2 mb-6"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Sparkles className="w-8 h-8 text-accent" />
              <h1 className="text-5xl font-bold gradient-text">AI Multi-Query Tool</h1>
              <Sparkles className="w-8 h-8 text-purple-500" />
            </motion.div>
            
            <motion.p
              className="text-xl text-gray-400 max-w-2xl mx-auto"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              Compare responses from multiple AI providers and search engines in real-time
            </motion.p>
          </motion.div>

          {/* Query Input */}
          <QueryInput onSubmit={handleSubmitQuery} isLoading={isQuerying} />
        </div>
      </section>

      {/* Providers Section */}
      {!isLoadingProviders && providersData?.providers && (
        <section className="py-8 px-4">
          <div className="container mx-auto">
            <motion.h2
              className="text-2xl font-semibold mb-6 text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              Select AI Providers
            </motion.h2>
            
            <ProviderCards
              providers={providersData.providers}
              selectedProviders={selectedProviders}
              onToggleProvider={toggleProvider}
              providerStatus={providerStatus}
            />
          </div>
        </section>
      )}

      {/* Results Section */}
      {(Object.keys(results).length > 0 || isQuerying) && (
        <section className="py-8 px-4">
          <div className="container mx-auto">
            <motion.h2
              className="text-2xl font-semibold mb-6 text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              Responses
            </motion.h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AnimatePresence>
                {selectedProviders.map((providerId) => (
                  <ResponseDisplay
                    key={providerId}
                    provider={providerId}
                    result={results[providerId] || null}
                    isLoading={providerStatus[providerId] === 'loading'}
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>
        </section>
      )}

      {/* Animated Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-primary opacity-10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-accent opacity-10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;