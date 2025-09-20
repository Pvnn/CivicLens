import React, { useState, useEffect } from "react";

export default function SocialMediaInsights() {
  const [youthOpinions, setYouthOpinions] = useState([]);
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('opinions');

  // Configuration for API endpoints
  const API_BASE_URL = 'http://localhost:5000';
  const ENDPOINTS = {
    opinions: `${API_BASE_URL}/api/youth-opinions`,
    sentiment: `${API_BASE_URL}/api/youth-sentiment`,
    status: `${API_BASE_URL}/api/social-media-status`
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch data in parallel
      const [opinionsResponse, sentimentResponse] = await Promise.all([
        fetch(ENDPOINTS.opinions),
        fetch(ENDPOINTS.sentiment)
      ]);

      if (!opinionsResponse.ok || !sentimentResponse.ok) {
        throw new Error('Failed to fetch social media data');
      }

      const [opinionsData, sentimentData] = await Promise.all([
        opinionsResponse.json(),
        sentimentResponse.json()
      ]);

      setYouthOpinions(opinionsData.data?.posts || []);
      setSentimentData(sentimentData.data);
      
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching social media data:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#10b981';
      case 'negative': return '#ef4444';
      case 'neutral': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      case 'neutral': return '😐';
      default: return '😐';
    }
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
        <h1 style={styles.title}>Social Media Insights</h1>
        <p style={styles.subtitle}>
          Real-time analysis of youth opinions from social media platforms
        </p>
      </div>

      {/* Tabs */}
      <div style={styles.tabsContainer}>
        <button
          style={{
            ...styles.tabButton,
            ...(activeTab === 'opinions' ? styles.tabButtonActive : {})
          }}
          onClick={() => setActiveTab('opinions')}
        >
          Posts ({youthOpinions.length})
        </button>
        <button
          style={{
            ...styles.tabButton,
            ...(activeTab === 'sentiment' ? styles.tabButtonActive : {})
          }}
          onClick={() => setActiveTab('sentiment')}
        >
          Sentiment Analysis
        </button>
      </div>

      {/* Content */}
      {activeTab === 'opinions' && (
        <div style={styles.content}>
          <div style={styles.postsGrid}>
            {youthOpinions.map((post, index) => (
              <div key={index} style={styles.postCard}>
                <div style={styles.postHeader}>
                  <div style={styles.platformBadge}>
                    {post.platform}
                  </div>
                  <div style={{
                    ...styles.sentimentBadge,
                    backgroundColor: getSentimentColor(post.sentiment?.overall)
                  }}>
                    {getSentimentIcon(post.sentiment?.overall)} {post.sentiment?.overall}
                  </div>
                </div>
                
                <div style={styles.postContent}>
                  {post.content?.substring(0, 200)}
                  {post.content?.length > 200 && '...'}
                </div>
                
                <div style={styles.postMeta}>
                  <div style={styles.relevanceScore}>
                    Relevance: {post.relevance_score}/10
                  </div>
                  {post.sentiment?.confidence && (
                    <div style={styles.confidenceScore}>
                      Confidence: {(post.sentiment.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'sentiment' && sentimentData && (
        <div style={styles.content}>
          <div style={styles.sentimentContainer}>
            <div style={styles.sentimentCard}>
              <h3 style={styles.sentimentTitle}>Overall Sentiment</h3>
              <div style={styles.sentimentStats}>
                <div style={styles.sentimentStat}>
                  <div style={styles.sentimentLabel}>Positive</div>
                  <div style={styles.sentimentValue}>
                    {sentimentData.positive_percentage?.toFixed(1) || 0}%
                  </div>
                </div>
                <div style={styles.sentimentStat}>
                  <div style={styles.sentimentLabel}>Neutral</div>
                  <div style={styles.sentimentValue}>
                    {sentimentData.neutral_percentage?.toFixed(1) || 0}%
                  </div>
                </div>
                <div style={styles.sentimentStat}>
                  <div style={styles.sentimentLabel}>Negative</div>
                  <div style={styles.sentimentValue}>
                    {sentimentData.negative_percentage?.toFixed(1) || 0}%
                  </div>
                </div>
              </div>
            </div>
            
            <div style={styles.sentimentCard}>
              <h3 style={styles.sentimentTitle}>Analysis Details</h3>
              <div style={styles.analysisDetails}>
                <div style={styles.analysisItem}>
                  <span style={styles.analysisLabel}>Total Posts:</span>
                  <span style={styles.analysisValue}>{sentimentData.total_posts || 0}</span>
                </div>
                <div style={styles.analysisItem}>
                  <span style={styles.analysisLabel}>Analysis Method:</span>
                  <span style={styles.analysisValue}>VADER + TextBlob</span>
                </div>
                <div style={styles.analysisItem}>
                  <span style={styles.analysisLabel}>Last Updated:</span>
                  <span style={styles.analysisValue}>
                    {new Date(sentimentData.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
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
  tabsContainer: {
    display: 'flex',
    gap: '8px',
    marginBottom: '24px',
    borderBottom: '1px solid #1f1f1f',
    paddingBottom: '16px'
  },
  tabButton: {
    padding: '8px 16px',
    fontSize: '0.8rem',
    fontWeight: '400',
    color: '#6b7280',
    backgroundColor: 'transparent',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  },
  tabButtonActive: {
    color: '#ffffff',
    borderBottom: '2px solid #ffffff'
  },
  content: {
    flex: 1
  },
  postsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '16px'
  },
  postCard: {
    background: '#111111',
    borderRadius: '8px',
    padding: '16px',
    border: '1px solid #1f1f1f',
    transition: 'all 0.2s ease'
  },
  postHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px'
  },
  platformBadge: {
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '0.7rem',
    fontWeight: '500',
    backgroundColor: '#1f1f1f',
    color: '#ffffff'
  },
  sentimentBadge: {
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '0.7rem',
    fontWeight: '500',
    color: '#ffffff'
  },
  postContent: {
    fontSize: '0.8rem',
    color: '#ffffff',
    lineHeight: '1.5',
    marginBottom: '12px'
  },
  postMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.7rem',
    color: '#6b7280'
  },
  relevanceScore: {
    fontWeight: '500'
  },
  confidenceScore: {
    fontWeight: '500'
  },
  sentimentContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '16px'
  },
  sentimentCard: {
    background: '#111111',
    borderRadius: '8px',
    padding: '16px',
    border: '1px solid #1f1f1f'
  },
  sentimentTitle: {
    fontSize: '1rem',
    fontWeight: '400',
    color: '#ffffff',
    marginBottom: '16px'
  },
  sentimentStats: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '16px'
  },
  sentimentStat: {
    textAlign: 'center'
  },
  sentimentLabel: {
    fontSize: '0.7rem',
    color: '#6b7280',
    marginBottom: '4px'
  },
  sentimentValue: {
    fontSize: '1.2rem',
    fontWeight: '500',
    color: '#ffffff'
  },
  analysisDetails: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  analysisItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.8rem'
  },
  analysisLabel: {
    color: '#6b7280'
  },
  analysisValue: {
    color: '#ffffff',
    fontWeight: '500'
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
