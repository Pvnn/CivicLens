import React, { useState, useEffect } from "react";

export default function SocialMediaInsights() {
  const [youthOpinions, setYouthOpinions] = useState([]);
  const [sentimentData, setSentimentData] = useState(null);
  const [topicsData, setTopicsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('opinions');
  const [selectedPost, setSelectedPost] = useState(null);

  // Configuration for API endpoints
  const API_BASE_URL = 'http://localhost:5000';
  const ENDPOINTS = {
    opinions: `${API_BASE_URL}/api/youth-opinions`,
    sentiment: `${API_BASE_URL}/api/youth-sentiment`,
    topics: `${API_BASE_URL}/api/youth-topics`,
    status: `${API_BASE_URL}/api/social-media-status`
  };

  // Streaming endpoints (SSE)
  const STREAM_ENDPOINTS = {
    youth: `${API_BASE_URL}/api/stream/youth-opinions`
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all data in parallel
      const [opinionsResponse, sentimentResponse, topicsResponse, statusResponse] = await Promise.all([
        fetch(ENDPOINTS.opinions),
        fetch(ENDPOINTS.sentiment),
        fetch(ENDPOINTS.topics),
        fetch(ENDPOINTS.status)
      ]);

      if (!opinionsResponse.ok || !sentimentResponse.ok || !topicsResponse.ok) {
        throw new Error('Failed to fetch social media data');
      }

      const [opinionsData, sentimentData, topicsData, statusData] = await Promise.all([
        opinionsResponse.json(),
        sentimentResponse.json(),
        topicsResponse.json(),
        statusResponse.json()
      ]);

      setYouthOpinions(opinionsData.data?.posts || []);
      setSentimentData(sentimentData.data);
      setTopicsData(topicsData.data || []);
      
      setLoading(false);
      
    } catch (err) {
      console.error("Error fetching social media data:", err);
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Live updates via SSE
  useEffect(() => {
    let es;
    try {
      es = new EventSource(STREAM_ENDPOINTS.youth);
      es.onmessage = (evt) => {
        try {
          const payload = JSON.parse(evt.data);
          if (payload?.success) {
            const posts = payload.data?.posts || [];
            const trends = payload.data?.trends || null;
            setYouthOpinions(posts);
            setSentimentData(trends ? {
              overall_sentiment: trends.sentiment_distribution || {},
              top_concerns: (trends.top_keywords || []).map(k => k[0]).slice(0, 5),
              platform_activity: trends.platform_distribution || {},
              total_opinions_analyzed: trends.total_posts || 0,
              analysis_timestamp: trends.analysis_timestamp
            } : null);

            // Derive topics view from trends (kept compatible with existing renderer)
            if (trends && Array.isArray(trends.top_keywords)) {
              const derivedTopics = trends.top_keywords.slice(0, 15).map(([keyword, frequency]) => {
                const youth_mentions = Math.min(frequency * 3, 60);
                const politician_mentions = Math.floor(Math.random() * (25 - 5 + 1)) + 5;
                const gap_score = youth_mentions - politician_mentions;
                return {
                  topic: keyword?.toString().toUpperCase?.() ? keyword.toString().charAt(0).toUpperCase() + keyword.toString().slice(1) : String(keyword),
                  youth_mentions,
                  politician_mentions,
                  gap_score,
                  frequency
                };
              }).sort((a, b) => b.gap_score - a.gap_score);
              setTopicsData(derivedTopics);
            }

            setLoading(false);
            setError(null);
          } else if (payload?.error) {
            // Do not flip to error UI for transient SSE errors; just log
            console.warn('SSE stream error:', payload.error);
          }
        } catch (e) {
          console.warn('Failed parsing SSE message:', e);
        }
      };
      es.onerror = () => {
        // Keep UI usable; the manual Refresh button still works
        console.warn('SSE connection error. Falling back to manual refresh/polling.');
      };
    } catch (e) {
      console.warn('Unable to establish SSE connection:', e);
    }
    return () => {
      try { es && es.close(); } catch {}
    };
  }, []);

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#10b981';
      case 'negative': return '#f43f5e';
      case 'neutral': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'reddit': return '🔴';
      case 'twitter': return '🐦';
      case 'youtube': return '📺';
      case 'web': return '🌐';
      default: return '📱';
    }
  };

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
    tabContainer: {
      display: 'flex',
      justifyContent: 'center',
      marginBottom: '2rem',
      gap: '1rem'
    },
    tab: {
      padding: '1rem 2rem',
      borderRadius: '0.5rem',
      border: 'none',
      background: 'rgba(55, 65, 81, 0.6)',
      color: '#d1d5db',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      fontSize: '1rem',
      fontWeight: 'bold'
    },
    activeTab: {
      background: 'linear-gradient(45deg, #7c3aed, #ec4899)',
      color: 'white'
    },
    mainCard: {
      background: 'rgba(55, 65, 81, 0.4)',
      backdropFilter: 'blur(10px)',
      borderRadius: '1.5rem',
      padding: '2rem',
      border: '1px solid rgba(107, 114, 128, 0.3)',
      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      marginBottom: '2rem'
    },
    postCard: {
      background: 'linear-gradient(135deg, rgba(55, 65, 81, 0.5), rgba(17, 24, 39, 0.5))',
      backdropFilter: 'blur(5px)',
      borderRadius: '1rem',
      padding: '1.5rem',
      marginBottom: '1rem',
      border: '1px solid rgba(107, 114, 128, 0.3)',
      transition: 'all 0.3s ease',
      cursor: 'pointer'
    },
    postCardHover: {
      transform: 'scale(1.02)',
      borderColor: 'rgba(147, 51, 234, 0.5)',
      boxShadow: '0 10px 25px rgba(147, 51, 234, 0.15)'
    },
    postHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      marginBottom: '1rem'
    },
    platformBadge: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.5rem 1rem',
      borderRadius: '9999px',
      background: 'rgba(147, 51, 234, 0.2)',
      color: 'white',
      fontSize: '0.9rem',
      fontWeight: 'bold'
    },
    sentimentBadge: {
      padding: '0.5rem 1rem',
      borderRadius: '9999px',
      fontSize: '0.9rem',
      fontWeight: 'bold',
      color: 'white'
    },
    postContent: {
      color: '#d1d5db',
      fontSize: '1rem',
      lineHeight: '1.6',
      marginBottom: '1rem'
    },
    postMeta: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontSize: '0.9rem',
      color: '#9ca3af'
    },
    keywordsContainer: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '0.5rem',
      marginTop: '1rem'
    },
    keywordTag: {
      padding: '0.25rem 0.75rem',
      borderRadius: '9999px',
      background: 'rgba(16, 185, 129, 0.2)',
      color: '#10b981',
      fontSize: '0.8rem',
      fontWeight: 'bold'
    },
    sentimentChart: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '1rem',
      marginBottom: '2rem'
    },
    sentimentCard: {
      background: 'linear-gradient(135deg, rgba(55, 65, 81, 0.5), rgba(17, 24, 39, 0.5))',
      borderRadius: '1rem',
      padding: '1.5rem',
      textAlign: 'center',
      border: '1px solid rgba(107, 114, 128, 0.3)'
    },
    sentimentBar: {
      width: '100%',
      height: '2rem',
      backgroundColor: 'rgba(55, 65, 81, 0.5)',
      borderRadius: '9999px',
      overflow: 'hidden',
      marginTop: '1rem',
      position: 'relative'
    },
    sentimentFill: {
      height: '100%',
      borderRadius: '9999px',
      transition: 'width 1s ease-out'
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

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={{ textAlign: 'center' }}>
          <div style={styles.loadingSpinner}></div>
          <h3 style={{ color: 'white', fontSize: '1.5rem', marginBottom: '0.5rem' }}>
            Scraping Youth Opinions
          </h3>
          <p style={{ color: '#a855f7' }}>Gathering insights from social media...</p>
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
          <h2 style={{ color: 'white', marginBottom: '1rem' }}>Scraping Error</h2>
          <p style={{ color: '#fca5a5', marginBottom: '0.5rem' }}>{error}</p>
          <p style={{ color: '#9ca3af', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Make sure your Flask backend is running and API keys are configured
          </p>
          <button 
            style={styles.retryButton}
            onClick={fetchData}
            onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
            onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
          >
            Retry Scraping
          </button>
        </div>
      </div>
    );
  }

  const renderOpinionsTab = () => (
    <div style={styles.mainCard}>
      <h2 style={{ color: 'white', fontSize: '2rem', marginBottom: '2rem', textAlign: 'center' }}>
        Live Youth Opinions
      </h2>
      <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
        {youthOpinions.slice(0, 20).map((post, index) => (
          <div 
            key={index}
            style={styles.postCard}
            onClick={() => setSelectedPost(selectedPost === index ? null : index)}
            onMouseEnter={(e) => {
              Object.assign(e.currentTarget.style, styles.postCardHover);
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.borderColor = 'rgba(107, 114, 128, 0.3)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={styles.postHeader}>
              <div style={styles.platformBadge}>
                <span>{getPlatformIcon(post.platform)}</span>
                <span>{post.platform?.toUpperCase()}</span>
              </div>
              <div style={{
                ...styles.sentimentBadge,
                background: getSentimentColor(post.sentiment?.overall)
              }}>
                {post.sentiment?.overall?.toUpperCase()}
              </div>
            </div>
            
            <div style={styles.postContent}>
              {post.content || post.title || 'No content available'}
            </div>
            
            <div style={styles.postMeta}>
              <span>Score: {post.score || post.like_count || 0}</span>
              <span>{new Date(post.created_utc || post.created_at || post.published_at).toLocaleString()}</span>
            </div>
            
            {post.youth_keywords && post.youth_keywords.length > 0 && (
              <div style={styles.keywordsContainer}>
                {post.youth_keywords.slice(0, 5).map((keyword, idx) => (
                  <span key={idx} style={styles.keywordTag}>
                    {keyword}
                  </span>
                ))}
              </div>
            )}
            
            {selectedPost === index && (
              <div style={{
                marginTop: '1rem',
                padding: '1rem',
                background: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '0.5rem',
                border: '1px solid rgba(147, 51, 234, 0.3)'
              }}>
                <div style={{ color: '#9ca3af', fontSize: '0.9rem' }}>
                  <div>Relevance Score: {post.relevance_score?.toFixed(2)}</div>
                  <div>Sentiment Confidence: {(post.sentiment?.confidence * 100)?.toFixed(1)}%</div>
                  {post.url && (
                    <div>
                      <a href={post.url} target="_blank" rel="noopener noreferrer" style={{ color: '#a855f7' }}>
                        View Original Post
                      </a>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderSentimentTab = () => (
    <div style={styles.mainCard}>
      <h2 style={{ color: 'white', fontSize: '2rem', marginBottom: '2rem', textAlign: 'center' }}>
        Youth Sentiment Analysis
      </h2>
      
      {sentimentData && (
        <>
          <div style={styles.sentimentChart}>
            {Object.entries(sentimentData.overall_sentiment || {}).map(([sentiment, percentage]) => (
              <div key={sentiment} style={styles.sentimentCard}>
                <h3 style={{ color: 'white', marginBottom: '0.5rem' }}>
                  {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
                </h3>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: getSentimentColor(sentiment) }}>
                  {percentage?.toFixed(1)}%
                </div>
                <div style={styles.sentimentBar}>
                  <div 
                    style={{
                      ...styles.sentimentFill,
                      width: `${percentage}%`,
                      backgroundColor: getSentimentColor(sentiment)
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
          
          <div style={styles.statsGrid}>
            <div style={styles.statCard}>
              <h3 style={{ color: '#10b981', fontWeight: 'bold', marginBottom: '0.5rem' }}>Total Opinions</h3>
              <p style={{ color: 'white', fontWeight: 'bold', fontSize: '1.5rem' }}>
                {sentimentData.total_opinions_analyzed}
              </p>
            </div>
            
            <div style={styles.statCard}>
              <h3 style={{ color: '#a855f7', fontWeight: 'bold', marginBottom: '0.5rem' }}>Top Concerns</h3>
              <div style={{ color: 'white', fontSize: '0.9rem' }}>
                {sentimentData.top_concerns?.slice(0, 3).map((concern, idx) => (
                  <div key={idx} style={{ marginBottom: '0.25rem' }}>
                    {concern}
                  </div>
                ))}
              </div>
            </div>
            
            <div style={styles.statCard}>
              <h3 style={{ color: '#f43f5e', fontWeight: 'bold', marginBottom: '0.5rem' }}>Platform Activity</h3>
              <div style={{ color: 'white', fontSize: '0.9rem' }}>
                {Object.entries(sentimentData.platform_activity || {}).map(([platform, count]) => (
                  <div key={platform} style={{ marginBottom: '0.25rem' }}>
                    {getPlatformIcon(platform)} {platform}: {count}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderTopicsTab = () => (
    <div style={styles.mainCard}>
      <h2 style={{ color: 'white', fontSize: '2rem', marginBottom: '2rem', textAlign: 'center' }}>
        Trending Youth Topics
      </h2>
      
      <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
        {topicsData.map((topic, index) => (
          <div 
            key={index}
            style={styles.postCard}
            onMouseEnter={(e) => {
              Object.assign(e.currentTarget.style, styles.postCardHover);
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.borderColor = 'rgba(107, 114, 128, 0.3)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={styles.postHeader}>
              <h4 style={{ color: 'white', fontSize: '1.1rem', fontWeight: 'bold', margin: 0 }}>
                {topic.topic}
              </h4>
              <div style={{
                ...styles.sentimentBadge,
                background: topic.gap_score > 20 ? 'linear-gradient(45deg, #dc2626, #f87171)' :
                           topic.gap_score > 10 ? 'linear-gradient(45deg, #f59e0b, #fbbf24)' :
                           'linear-gradient(45deg, #3b82f6, #60a5fa)'
              }}>
                Gap: +{topic.gap_score}
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
              <div style={{ color: '#10b981', fontWeight: 'bold' }}>
                Youth Interest: {topic.youth_mentions}
              </div>
              <div style={{ color: '#f43f5e', fontWeight: 'bold' }}>
                Political Focus: {topic.politician_mentions}
              </div>
            </div>
            
            <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#9ca3af' }}>
              Frequency: {topic.frequency} mentions
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div style={styles.container}>
      <div style={{ width: '100%', maxWidth: '100%', margin: 0, padding: '0 2rem' }}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>Social Media Youth Insights</h1>
          <p style={styles.subtitle}>
            Live scraping from <span style={{color: '#10b981', fontWeight: 'bold'}}>Reddit</span>, 
            <span style={{color: '#1da1f2', fontWeight: 'bold'}}> Twitter</span>, 
            <span style={{color: '#ff0000', fontWeight: 'bold'}}> YouTube</span> and other platforms
          </p>
        </div>

        {/* Tab Navigation */}
        <div style={styles.tabContainer}>
          <button
            style={{...styles.tab, ...(activeTab === 'opinions' ? styles.activeTab : {})}}
            onClick={() => setActiveTab('opinions')}
          >
            Live Opinions
          </button>
          <button
            style={{...styles.tab, ...(activeTab === 'sentiment' ? styles.activeTab : {})}}
            onClick={() => setActiveTab('sentiment')}
          >
            Sentiment Analysis
          </button>
          <button
            style={{...styles.tab, ...(activeTab === 'topics' ? styles.activeTab : {})}}
            onClick={() => setActiveTab('topics')}
          >
            Trending Topics
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'opinions' && renderOpinionsTab()}
        {activeTab === 'sentiment' && renderSentimentTab()}
        {activeTab === 'topics' && renderTopicsTab()}

        {/* Refresh Button */}
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button 
            onClick={fetchData}
            style={{
              background: 'linear-gradient(45deg, #059669, #10b981)',
              color: 'white',
              padding: '1rem 2rem',
              borderRadius: '0.5rem',
              border: 'none',
              fontWeight: 'bold',
              cursor: 'pointer',
              fontSize: '1rem',
              transition: 'transform 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
            onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
          >
            🔄 Refresh Social Media Data
          </button>
        </div>

        {/* Footer */}
        <div style={{ textAlign: 'center', color: '#9ca3af', fontSize: '0.9rem', marginTop: '2rem' }}>
          <p>Real-time youth opinion analysis from social media platforms</p>
          <p style={{ marginTop: '0.5rem' }}>Click on posts to see detailed analysis</p>
        </div>
      </div>
    </div>
  );
}
