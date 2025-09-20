import React, { useState, useEffect } from "react";

export default function MissingTopicsTracker() {
  const [topicsData, setTopicsData] = useState([]);
  const [metadata, setMetadata] = useState(null);
  const [maxValue, setMaxValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [selectedTopic, setSelectedTopic] = useState(null);

  // Configuration for API endpoint
  const API_BASE_URL = 'http://localhost:5000';
  const API_ENDPOINT = `${API_BASE_URL}/api/missing-topics`;

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching data from:', API_ENDPOINT);
      
      // First check if backend is healthy
      const healthResponse = await fetch(`${API_BASE_URL}/api/health`);
      if (!healthResponse.ok) {
        throw new Error('Backend health check failed');
      }
      
      // Fetch the main data
      const response = await fetch(API_ENDPOINT, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const responseData = await response.json();
      console.log('Received data:', responseData);
      
      // Handle new API response format
      const data = responseData.data || responseData;
      const meta = responseData.metadata || null;
      
      if (!Array.isArray(data) || data.length === 0) {
        throw new Error('No data received from backend');
      }

      setMetadata(meta);

      // Sort by gap score (highest first - topics youth care about but politicians don't)
      const sortedData = data.sort((a, b) => (b.gap_score || 0) - (a.gap_score || 0));
      
      // Take top 10 topics for better visualization
      const topTopics = sortedData.slice(0, 10);
      
      setTopicsData(topTopics);
      setMaxValue(Math.max(...topTopics.map(t => Math.max(t.youth_mentions || 0, t.politician_mentions || 0))));
      
      setLoading(false);
      setRetryCount(0);
      
    } catch (err) {
      console.error("Error fetching data:", err);
      setError(err.message);
      setLoading(false);
      
      // Auto-retry up to 3 times with increasing delay
      if (retryCount < 3) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          fetchData();
        }, (retryCount + 1) * 2000);
      }
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Inline styles for better compatibility
  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b 0%, #4c1d95 50%, #1e293b 100%)',
      padding: '2rem',
      fontFamily: 'Arial, sans-serif'
    },
    header: {
      textAlign: 'center',
      marginBottom: '3rem'
    },
    title: {
      fontSize: '3.5rem',
      fontWeight: 'bold',
      background: 'linear-gradient(45deg, #a855f7, #ec4899, #8b5cf6)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      color: 'transparent',
      marginBottom: '1rem'
    },
    subtitle: {
      fontSize: '1.2rem',
      color: '#d1d5db',
      maxWidth: '600px',
      margin: '0 auto',
      lineHeight: '1.6'
    },
    dataSourceCard: {
      background: 'rgba(55, 65, 81, 0.6)',
      backdropFilter: 'blur(10px)',
      borderRadius: '1rem',
      padding: '1rem',
      marginBottom: '2rem',
      border: '1px solid rgba(147, 51, 234, 0.3)'
    },
    mainCard: {
      background: 'rgba(55, 65, 81, 0.4)',
      backdropFilter: 'blur(10px)',
      borderRadius: '1.5rem',
      padding: '2rem',
      border: '1px solid rgba(107, 114, 128, 0.3)',
      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
    },
    sectionTitle: {
      fontSize: '2rem',
      fontWeight: 'bold',
      color: 'white',
      textAlign: 'center',
      marginBottom: '2rem'
    },
    topicCard: {
      background: 'linear-gradient(135deg, rgba(55, 65, 81, 0.5), rgba(17, 24, 39, 0.5))',
      backdropFilter: 'blur(5px)',
      borderRadius: '1rem',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      border: '1px solid rgba(107, 114, 128, 0.3)',
      transition: 'all 0.3s ease',
      cursor: 'pointer'
    },
    topicCardHover: {
      transform: 'scale(1.02)',
      borderColor: 'rgba(147, 51, 234, 0.5)',
      boxShadow: '0 10px 25px rgba(147, 51, 234, 0.15)'
    },
    topicHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: '1rem'
    },
    topicTitle: {
      color: 'white',
      fontSize: '1.1rem',
      fontWeight: 'bold',
      maxWidth: '70%',
      lineHeight: '1.4'
    },
    gapBadge: {
      padding: '0.5rem 1rem',
      borderRadius: '9999px',
      fontSize: '0.9rem',
      fontWeight: 'bold',
      color: 'white'
    },
    progressSection: {
      marginTop: '1rem'
    },
    progressRow: {
      marginBottom: '1rem'
    },
    progressLabel: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '0.5rem'
    },
    progressBar: {
      width: '100%',
      height: '1rem',
      backgroundColor: 'rgba(55, 65, 81, 0.5)',
      borderRadius: '9999px',
      overflow: 'hidden',
      position: 'relative'
    },
    progressFill: {
      height: '100%',
      borderRadius: '9999px',
      transition: 'width 1s ease-out',
      position: 'relative',
      overflow: 'hidden'
    },
    youthBar: {
      background: 'linear-gradient(90deg, #10b981, #34d399, #6ee7b7)'
    },
    politicianBar: {
      background: 'linear-gradient(90deg, #f43f5e, #fb7185, #fda4af)'
    },
    expandedDetails: {
      marginTop: '1rem',
      padding: '1rem',
      background: 'rgba(0, 0, 0, 0.3)',
      borderRadius: '0.5rem',
      border: '1px solid rgba(147, 51, 234, 0.3)'
    },
    loadingContainer: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b 0%, #4c1d95 50%, #1e293b 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    },
    loadingSpinner: {
      width: '4rem',
      height: '4rem',
      border: '4px solid rgba(147, 51, 234, 0.2)',
      borderTop: '4px solid #a855f7',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite',
      marginBottom: '1rem'
    },
    errorContainer: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b 0%, #dc2626 20%, #1e293b 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    },
    errorCard: {
      background: 'rgba(55, 65, 81, 0.6)',
      backdropFilter: 'blur(10px)',
      borderRadius: '1rem',
      padding: '2rem',
      border: '1px solid rgba(220, 38, 38, 0.3)',
      maxWidth: '400px',
      textAlign: 'center'
    },
    retryButton: {
      background: 'linear-gradient(45deg, #7c3aed, #ec4899)',
      color: 'white',
      padding: '0.75rem 1.5rem',
      borderRadius: '0.5rem',
      border: 'none',
      fontWeight: 'bold',
      cursor: 'pointer',
      transition: 'transform 0.2s ease',
      fontSize: '1rem'
    },
    statsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '1rem',
      marginTop: '2rem'
    },
    statCard: {
      background: 'linear-gradient(135deg, rgba(147, 51, 234, 0.2), rgba(59, 130, 246, 0.2))',
      borderRadius: '1rem',
      padding: '1.5rem',
      border: '1px solid rgba(147, 51, 234, 0.3)',
      textAlign: 'center'
    }
  };

  const getGapBadgeStyle = (gapScore) => {
    const baseStyle = { ...styles.gapBadge };
    if (gapScore > 20) {
      baseStyle.background = 'linear-gradient(45deg, #dc2626, #f87171)';
    } else if (gapScore > 10) {
      baseStyle.background = 'linear-gradient(45deg, #f59e0b, #fbbf24)';
    } else if (gapScore > 0) {
      baseStyle.background = 'linear-gradient(45deg, #3b82f6, #60a5fa)';
    } else {
      baseStyle.background = 'linear-gradient(45deg, #6b7280, #9ca3af)';
    }
    return baseStyle;
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={{ textAlign: 'center' }}>
          <div style={styles.loadingSpinner}></div>
          <h3 style={{ color: 'white', fontSize: '1.5rem', marginBottom: '0.5rem' }}>
            Analyzing Youth-Politics Gap
          </h3>
          <p style={{ color: '#a855f7' }}>Gathering insights from Indian sources...</p>
          {retryCount > 0 && (
            <p style={{ color: '#ec4899', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Retry attempt {retryCount}/3
            </p>
          )}
        </div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <div style={styles.errorCard}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
          <h2 style={{ color: 'white', marginBottom: '1rem' }}>Connection Error</h2>
          <p style={{ color: '#fca5a5', marginBottom: '0.5rem' }}>{error}</p>
          <p style={{ color: '#9ca3af', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Make sure your Flask backend is running on http://localhost:5000
          </p>
          <button 
            style={styles.retryButton}
            onClick={fetchData}
            onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
            onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>Youth vs Politics</h1>
          <p style={styles.subtitle}>
            Discovering the gap between what <span style={{color: '#10b981', fontWeight: 'bold'}}>Indian youth care about</span> and 
            what <span style={{color: '#f43f5e', fontWeight: 'bold'}}>politicians discuss</span>
          </p>
        </div>

        {/* Data Source Info */}
        {metadata && (
          <div style={styles.dataSourceCard}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{
                  width: '12px', 
                  height: '12px', 
                  borderRadius: '50%',
                  backgroundColor: metadata.data_source === 'live_scraped' ? '#10b981' : 
                                 metadata.data_source === 'enhanced_fallback' ? '#3b82f6' : '#f59e0b'
                }}></div>
                <span style={{ color: 'white', fontWeight: 'bold' }}>
                  {metadata.data_source === 'live_scraped' ? '🔴 Live Data' : 
                   metadata.data_source === 'enhanced_fallback' ? '📊 Curated Data' : '⚠️ Fallback Data'}
                </span>
                {metadata.sources && (
                  <span style={{ color: '#d1d5db', fontSize: '0.9rem' }}>• {metadata.sources}</span>
                )}
              </div>
              <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>
                {new Date(metadata.timestamp).toLocaleString()}
              </span>
            </div>
            {metadata.note && (
              <p style={{ color: '#d1d5db', fontSize: '0.9rem', marginTop: '0.5rem', marginLeft: '1.2rem' }}>
                {metadata.note}
              </p>
            )}
          </div>
        )}

        {/* Main Content */}
        <div style={styles.mainCard}>
          <h2 style={styles.sectionTitle}>The Gap Analysis</h2>
          
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {topicsData.map((item, index) => (
              <div 
                key={index}
                style={styles.topicCard}
                onClick={() => setSelectedTopic(selectedTopic === index ? null : index)}
                onMouseEnter={(e) => {
                  Object.assign(e.currentTarget.style, styles.topicCardHover);
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.borderColor = 'rgba(107, 114, 128, 0.3)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={styles.topicHeader}>
                  <h4 style={styles.topicTitle}>{item.topic}</h4>
                  <div style={getGapBadgeStyle(item.gap_score)}>
                    Gap: {item.gap_score > 0 ? '+' : ''}{item.gap_score}
                  </div>
                </div>

                <div style={styles.progressSection}>
                  {/* Youth Progress Bar */}
                  <div style={styles.progressRow}>
                    <div style={styles.progressLabel}>
                      <span style={{ color: '#10b981', fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                        <span style={{ width: '8px', height: '8px', backgroundColor: '#10b981', borderRadius: '50%', marginRight: '0.5rem' }}></span>
                        Youth Voice
                      </span>
                      <span style={{ color: '#6ee7b7', fontWeight: 'bold' }}>{item.youth_mentions}</span>
                    </div>
                    <div style={styles.progressBar}>
                      <div 
                        style={{
                          ...styles.progressFill,
                          ...styles.youthBar,
                          width: `${maxValue > 0 ? (item.youth_mentions / maxValue) * 100 : 0}%`
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* Politicians Progress Bar */}
                  <div style={styles.progressRow}>
                    <div style={styles.progressLabel}>
                      <span style={{ color: '#f43f5e', fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                        <span style={{ width: '8px', height: '8px', backgroundColor: '#f43f5e', borderRadius: '50%', marginRight: '0.5rem' }}></span>
                        Political Focus
                      </span>
                      <span style={{ color: '#fda4af', fontWeight: 'bold' }}>{item.politician_mentions}</span>
                    </div>
                    <div style={styles.progressBar}>
                      <div 
                        style={{
                          ...styles.progressFill,
                          ...styles.politicianBar,
                          width: `${maxValue > 0 ? (item.politician_mentions / maxValue) * 100 : 0}%`
                        }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {selectedTopic === index && (
                  <div style={styles.expandedDetails}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.9rem' }}>
                      <div>
                        <span style={{ color: '#9ca3af' }}>Youth Interest Level:</span>
                        <div style={{ color: '#10b981', fontWeight: 'bold' }}>
                          {item.youth_mentions > 40 ? 'Very High' : 
                           item.youth_mentions > 25 ? 'High' : 
                           item.youth_mentions > 15 ? 'Moderate' : 'Low'}
                        </div>
                      </div>
                      <div>
                        <span style={{ color: '#9ca3af' }}>Political Attention:</span>
                        <div style={{ color: '#f43f5e', fontWeight: 'bold' }}>
                          {item.politician_mentions > 30 ? 'High Focus' : 
                           item.politician_mentions > 20 ? 'Moderate' : 
                           item.politician_mentions > 10 ? 'Low' : 'Neglected'}
                        </div>
                      </div>
                    </div>
                    {metadata?.sources && (
                      <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#6b7280' }}>
                        Source: {metadata.sources}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Stats Section */}
        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <h3 style={{ color: '#f43f5e', fontWeight: 'bold', marginBottom: '0.5rem' }}>Most Neglected</h3>
            <p style={{ color: 'white', fontWeight: 'bold' }}>{topicsData[0]?.topic}</p>
            <p style={{ color: '#fda4af', fontSize: '0.9rem' }}>Gap: +{topicsData[0]?.gap_score}</p>
          </div>
          
          <div style={styles.statCard}>
            <h3 style={{ color: '#a855f7', fontWeight: 'bold', marginBottom: '0.5rem' }}>Analysis</h3>
            <p style={{ color: 'white', fontWeight: 'bold' }}>{topicsData.length} Topics Analyzed</p>
            <p style={{ color: '#c084fc', fontSize: '0.9rem' }}>
              Avg Gap: {Math.round(topicsData.reduce((a, b) => a + (b.gap_score || 0), 0) / topicsData.length)}
            </p>
          </div>
          
          <div style={styles.statCard}>
            <h3 style={{ color: '#10b981', fontWeight: 'bold', marginBottom: '0.5rem' }}>Live Updates</h3>
            <button 
              onClick={fetchData}
              style={{
                background: 'linear-gradient(45deg, #059669, #10b981)',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '0.5rem',
                border: 'none',
                fontWeight: 'bold',
                cursor: 'pointer',
                width: '100%',
                transition: 'transform 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
              onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            >
              Refresh Data
            </button>
          </div>
        </div>

        {/* Footer */}
        <div style={{ textAlign: 'center', color: '#9ca3af', fontSize: '0.9rem', marginTop: '2rem' }}>
          <p>Data reflects the conversation gap between Indian youth priorities and political discourse</p>
          <p style={{ marginTop: '0.5rem' }}>Click on any topic above to see detailed breakdown</p>
        </div>
      </div>
    </div>
  );
}