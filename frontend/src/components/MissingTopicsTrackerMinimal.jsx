import React, { useState, useEffect } from "react";

export default function MissingTopicsTracker() {
  const [topicsData, setTopicsData] = useState([]);
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  // Configuration for API endpoint
  const API_BASE_URL = 'http://localhost:5000';
  const API_ENDPOINT = `${API_BASE_URL}/api/missing-topics`;
  const REAL_GAP_ENDPOINT = `${API_BASE_URL}/api/real-gap-analysis`;

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to fetch real gap analysis first
      let response;
      try {
        response = await fetch(REAL_GAP_ENDPOINT, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          console.log('Using real gap analysis data');
        } else {
          throw new Error('Real gap analysis failed');
        }
      } catch (e) {
        console.log('Falling back to regular endpoint');
        response = await fetch(API_ENDPOINT, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Fetched data:', data);
      
      if (data.success && data.data) {
        setTopicsData(data.data);
        setMetadata(data.metadata);
      } else {
        throw new Error(data.error || 'Failed to fetch data');
      }
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message);
      
      // Retry logic
      if (retryCount < 3) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          fetchData();
        }, (retryCount + 1) * 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getGapBadgeStyle = (gapScore) => {
    if (gapScore > 20) {
      return { backgroundColor: '#ef4444', color: '#ffffff' };
    } else if (gapScore > 10) {
      return { backgroundColor: '#f59e0b', color: '#ffffff' };
    } else if (gapScore > 0) {
      return { backgroundColor: '#10b981', color: '#ffffff' };
    } else {
      return { backgroundColor: '#6b7280', color: '#ffffff' };
    }
  };

  const getGapText = (gapScore) => {
    if (gapScore > 20) return 'Critical Gap';
    if (gapScore > 10) return 'High Gap';
    if (gapScore > 0) return 'Moderate Gap';
    return 'Low Gap';
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.loadingSpinner}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <div style={styles.errorMessage}>Error: {error}</div>
        <button style={styles.retryButton} onClick={fetchData}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Youth vs Political Focus Gap</h1>
        <p style={styles.subtitle}>
          Real-time analysis of topics where youth and political priorities differ
        </p>
      </div>

      {/* Metadata */}
      {metadata && (
        <div style={styles.dataSourceCard}>
          <div style={styles.metadataTitle}>Data Source</div>
          <div style={styles.metadataContent}>
            <div>Source: {metadata.data_source || 'Real-time analysis'}</div>
            <div>Last Updated: {new Date(metadata.timestamp).toLocaleString()}</div>
            {metadata.reliability_score && (
              <div>Reliability: {(metadata.reliability_score * 100).toFixed(0)}%</div>
            )}
            {metadata.data_points && (
              <div>Data Points: {metadata.data_points}</div>
            )}
          </div>
        </div>
      )}

      {/* Topics Grid */}
      <div style={styles.mainCard}>
        <h2 style={styles.sectionTitle}>Topic Analysis</h2>
        
        <div style={styles.topicsGrid}>
          {topicsData.map((item, index) => (
            <div key={index} style={styles.topicCard}>
              <div style={styles.topicHeader}>
                <div style={styles.topicTitle}>{item.topic}</div>
                <div style={{...styles.gapBadge, ...getGapBadgeStyle(item.gap_score)}}>
                  {getGapText(item.gap_score)}
                </div>
              </div>
              
              <div style={styles.progressSection}>
                <div style={styles.progressRow}>
                  <div style={styles.progressLabel}>
                    <span style={styles.progressText}>Youth Focus</span>
                    <span style={styles.progressText}>{item.youth_mentions}</span>
                  </div>
                  <div style={styles.progressBar}>
                    <div 
                      style={{
                        ...styles.progressFill,
                        ...styles.youthProgress,
                        width: `${Math.min((item.youth_mentions / 100) * 100, 100)}%`
                      }}
                    ></div>
                  </div>
                </div>
                
                <div style={styles.progressRow}>
                  <div style={styles.progressLabel}>
                    <span style={styles.progressText}>Political Focus</span>
                    <span style={styles.progressText}>{item.politician_mentions}</span>
                  </div>
                  <div style={styles.progressBar}>
                    <div 
                      style={{
                        ...styles.progressFill,
                        ...styles.politicianProgress,
                        width: `${Math.min((item.politician_mentions / 100) * 100, 100)}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
              
              {item.reliability && (
                <div style={{ marginTop: '8px', fontSize: '0.7rem', color: '#6b7280' }}>
                  Reliability: {(item.reliability * 100).toFixed(0)}%
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: '100%',
    padding: '24px',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
  },
  header: {
    marginBottom: '32px'
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: '300',
    color: '#ffffff',
    marginBottom: '8px'
  },
  subtitle: {
    fontSize: '0.9rem',
    color: '#6b7280',
    marginBottom: '24px'
  },
  dataSourceCard: {
    background: '#111111',
    borderRadius: '8px',
    padding: '16px',
    marginBottom: '24px',
    border: '1px solid #1f1f1f'
  },
  metadataTitle: {
    fontSize: '0.9rem',
    fontWeight: '500',
    color: '#ffffff',
    marginBottom: '8px'
  },
  metadataContent: {
    fontSize: '0.75rem',
    color: '#6b7280',
    lineHeight: '1.5'
  },
  mainCard: {
    background: '#111111',
    borderRadius: '8px',
    padding: '24px',
    border: '1px solid #1f1f1f'
  },
  sectionTitle: {
    fontSize: '1.2rem',
    fontWeight: '400',
    color: '#ffffff',
    marginBottom: '24px'
  },
  topicsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '16px'
  },
  topicCard: {
    background: '#111111',
    borderRadius: '8px',
    padding: '16px',
    border: '1px solid #1f1f1f',
    transition: 'all 0.2s ease',
    cursor: 'pointer'
  },
  topicHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '12px'
  },
  topicTitle: {
    color: '#ffffff',
    fontSize: '0.9rem',
    fontWeight: '400',
    maxWidth: '70%',
    lineHeight: '1.4'
  },
  gapBadge: {
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '0.75rem',
    fontWeight: '500',
    color: '#ffffff'
  },
  progressSection: {
    marginTop: '12px'
  },
  progressRow: {
    marginBottom: '12px'
  },
  progressLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '6px'
  },
  progressBar: {
    width: '100%',
    height: '4px',
    backgroundColor: '#1f1f1f',
    borderRadius: '2px',
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    borderRadius: '2px',
    transition: 'width 0.3s ease'
  },
  youthProgress: {
    background: '#10b981'
  },
  politicianProgress: {
    background: '#3b82f6'
  },
  progressText: {
    color: '#6b7280',
    fontSize: '0.75rem',
    fontWeight: '400'
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '200px'
  },
  loadingSpinner: {
    width: '24px',
    height: '24px',
    border: '2px solid #1f1f1f',
    borderTop: '2px solid #ffffff',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },
  errorContainer: {
    textAlign: 'center',
    padding: '40px',
    color: '#ef4444'
  },
  errorMessage: {
    fontSize: '0.9rem',
    marginBottom: '16px'
  },
  retryButton: {
    backgroundColor: '#ffffff',
    color: '#000000',
    padding: '8px 16px',
    borderRadius: '4px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '0.8rem',
    fontWeight: '400',
    transition: 'all 0.2s ease'
  }
};
