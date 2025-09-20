import React, { useEffect, useState } from "react";

export default function TechCareerFeed() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const API_BASE_URL = 'http://localhost:5000';
  const STREAM_URL = `${API_BASE_URL}/api/stream/career-feed`;
  const REST_URL = `${API_BASE_URL}/api/career-feed`;

  // Manual fetch fallback
  const fetchOnce = async () => {
    try {
      const res = await fetch(REST_URL);
      const json = await res.json();
      setItems(json.data || []);
      setLastUpdated(new Date().toISOString());
      setError(null);
    } catch (e) {
      setError(String(e));
    }
  };

  useEffect(() => {
    // initial fetch quickly to populate
    fetchOnce();

    let es;
    try {
      es = new EventSource(STREAM_URL);
      es.onmessage = (evt) => {
        try {
          const payload = JSON.parse(evt.data);
          if (payload?.success) {
            setItems(payload.data || []);
            setLastUpdated(payload.metadata?.timestamp || new Date().toISOString());
            setError(null);
          }
        } catch (e) {
          console.warn('career-feed SSE parse error', e);
        }
      };
      es.onerror = () => {
        console.warn('career-feed SSE error, falling back to REST polling');
      };
    } catch (e) {
      console.warn('EventSource unsupported/error', e);
    }
    return () => {
      try { es && es.close(); } catch {}
    };
  }, []);

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b 0%, #4c1d95 50%, #1e293b 100%)',
      padding: '2rem',
      fontFamily: 'Arial, sans-serif'
    },
    inner: { width: '100%', maxWidth: '100%', margin: 0, padding: '0 2rem' },
    header: { textAlign: 'center', marginBottom: '2rem' },
    title: {
      fontSize: '2.5rem', fontWeight: 'bold',
      background: 'linear-gradient(45deg, #22c55e, #3b82f6, #a855f7)',
      WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', margin: 0
    },
    subtitle: { color: '#d1d5db' },
    metaBar: {
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      background: 'rgba(55,65,81,0.6)', border: '1px solid rgba(107,114,128,0.3)',
      borderRadius: '0.75rem', padding: '0.5rem 1rem', marginBottom: '1rem'
    },
    list: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' },
    card: {
      background: 'linear-gradient(135deg, rgba(55,65,81,0.5), rgba(17,24,39,0.5))',
      border: '1px solid rgba(107,114,128,0.3)', borderRadius: '0.75rem', padding: '1rem'
    },
    source: { color: '#9ca3af', fontSize: '0.85rem' },
    link: { color: '#a855f7', textDecoration: 'none', fontWeight: 'bold' },
    desc: { color: '#d1d5db', marginTop: '0.25rem' },
    badge: { color: 'white', background: 'rgba(59,130,246,0.3)', padding: '0.25rem 0.5rem', borderRadius: '9999px', fontSize: '0.8rem' },
    controls: { textAlign: 'right', marginTop: '0.5rem' },
    button: { background: 'linear-gradient(45deg, #059669, #10b981)', color: 'white', padding: '0.5rem 1rem', border: 'none', borderRadius: '0.5rem', cursor: 'pointer' }
  };

  return (
    <div style={styles.container}>
      <div style={styles.inner}>
        <div style={styles.header}>
          <h1 style={styles.title}>Tech & Careers – Live Feed</h1>
          <p style={styles.subtitle}>Hacker News, GitHub Trending, and Stack Overflow updates</p>
        </div>

        <div style={styles.metaBar}>
          <div>
            <span style={{ color: '#d1d5db' }}>Sources: </span>
            <span className="font-bold">HN</span>, <span className="font-bold">GitHub</span>, <span className="font-bold">Stack Overflow</span>
          </div>
          <div style={{ color: '#9ca3af' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981', display: 'inline-block', boxShadow: '0 0 8px #10b981' }}></span>
              Live
            </span>
            {lastUpdated && <span style={{ marginLeft: '0.75rem' }}>Updated: {new Date(lastUpdated).toLocaleTimeString()}</span>}
          </div>
        </div>

        {error && (
          <div style={{ ...styles.metaBar, borderColor: 'rgba(220,38,38,0.4)', background: 'rgba(220,38,38,0.15)' }}>
            <span style={{ color: '#fecaca' }}>Error: {error}</span>
          </div>
        )}

        <div style={styles.list}>
          {items.map((it, idx) => (
            <div key={idx} style={styles.card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '0.5rem' }}>
                <a href={it.url} target="_blank" rel="noopener noreferrer" style={styles.link}>{it.title || 'Untitled'}</a>
                {typeof it.score === 'number' && it.score > 0 && (
                  <span style={styles.badge}>Score: {it.score}</span>
                )}
              </div>
              {it.description && <div style={styles.desc}>{it.description}</div>}
              <div style={{ marginTop: '0.5rem', display: 'flex', justifyContent: 'space-between', color: '#9ca3af', fontSize: '0.85rem' }}>
                <span>{it.source}{it.language ? ` • ${it.language}` : ''}</span>
                <span>{it.author || ''}</span>
              </div>
            </div>
          ))}
        </div>

        <div style={styles.controls}>
          <button style={styles.button} onClick={fetchOnce}>Refresh Now</button>
        </div>
      </div>
    </div>
  );
}
