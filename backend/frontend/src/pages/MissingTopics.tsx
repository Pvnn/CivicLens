import { useEffect, useState } from 'react'
import { api } from '@/api/client'
import { Grid, Stack, Typography, Paper, Skeleton, Chip, Divider, Box, Link } from '@mui/material'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

type TopicRow = { topic: string; youth_mentions: number; politician_mentions: number; gap_score: number; description?: string }
type YouthTrends = {
  overall_sentiment?: Record<string, number>
  top_concerns?: string[]
  platform_activity?: Record<string, number>
  total_opinions_analyzed?: number
}
type YouthData = {
  posts?: { platform: string; sentiment: string; content: string; timestamp: string; engagement?: number }[]
  trends?: YouthTrends
}
type TopicsMetadata = { timestamp?: string; data_source?: string; sources?: string; source_links?: string[]; note?: string }

function TopicsTooltip({ active, payload }: any){
  if (!active || !payload || !payload.length) return null
  const d = payload[0].payload as TopicRow
  return (
    <Paper sx={{ p: 1.2, bgcolor:'#0F172A', border:'1px solid rgba(148,163,184,0.25)' }}>
      <Typography variant="subtitle2" sx={{color:'#E2E8F0'}}>{d.topic}</Typography>
      <Typography variant="caption" sx={{color:'#94A3B8'}}>Youth: {d.youth_mentions} • Politicians: {d.politician_mentions}</Typography>
      {d.description && <Typography variant="caption" display="block" sx={{mt:0.5, color:'#94A3B8'}}>{d.description}</Typography>}
    </Paper>
  )
}

export default function MissingTopics(){
  const [rows, setRows] = useState<TopicRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string|undefined>()
  const [youth, setYouth] = useState<YouthData>({})
  const [youthLoading, setYouthLoading] = useState(true)
  const [meta, setMeta] = useState<TopicsMetadata | undefined>()

  useEffect(()=> { (async()=>{
    setLoading(true)
    try {
      const res = await api<{data: TopicRow[]; metadata?: TopicsMetadata}>('/api/missing-topics')
      setRows(res.data || [])
      setMeta(res.metadata)
    } catch(e:any){ setError(e.message) }
    finally { setLoading(false) }
  })() }, [])

  useEffect(()=> { (async()=>{
    setYouthLoading(true)
    try {
      // Try opinions; if fails, try sentiment
      const opinions = await api<{success:boolean; data: YouthData}>('/api/youth-opinions').catch(()=>null)
      const sentiment = await api<{success:boolean; data: YouthTrends}>('/api/youth-sentiment').catch(()=>null)
      // Normalize trends keys from legacy API (sentiment_distribution, top_keywords, total_posts)
      const rawTrends: any = opinions?.data?.trends || sentiment?.data || {}
      const normalized: YouthTrends = {
        overall_sentiment: rawTrends.overall_sentiment || rawTrends.sentiment_distribution || undefined,
        top_concerns: rawTrends.top_concerns || (Array.isArray(rawTrends.top_keywords) ? rawTrends.top_keywords.map((k:any)=> (Array.isArray(k)? k[0] : k)) : undefined),
        platform_activity: rawTrends.platform_activity,
        total_opinions_analyzed: rawTrends.total_opinions_analyzed ?? rawTrends.total_posts,
      }
      setYouth({ posts: opinions?.data?.posts || [], trends: normalized })
    } catch { /* ignore */ }
    finally { setYouthLoading(false) }
  })() }, [])

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Missing Topics (Youth vs Politicians)</Typography>
      {error && <div style={{color:'#f87171'}}>Error: {error}</div>}

      {/* Metadata with source links */}
      {meta && (
        <Paper sx={{ p: 2 }}>
          <Stack direction="row" spacing={2} justifyContent="space-between" alignItems="center" flexWrap="wrap">
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip size="small" label={meta.data_source === 'live_scraped' ? 'Live Data' : meta.data_source === 'curated_fallback' ? 'Curated Data' : 'Fallback'} color={meta.data_source==='live_scraped' ? 'success' : meta.data_source==='curated_fallback' ? 'primary' : 'default'} />
              {meta.sources && <Typography variant="body2" sx={{ color:'#64748B' }}>Sources: {meta.sources}</Typography>}
            </Stack>
            <Typography variant="caption" sx={{ color:'#94A3B8' }}>{meta.timestamp ? new Date(meta.timestamp).toLocaleString() : ''}</Typography>
          </Stack>
          {Array.isArray(meta.source_links) && meta.source_links.length>0 && (
            <Stack direction="row" spacing={1} sx={{mt:1, flexWrap:'wrap'}}>
              {meta.source_links.map((url, i)=> (
                <Chip key={i} size="small" component={Link as any} clickable href={url} target="_blank" rel="noopener" label={new URL(url).hostname} />
              ))}
            </Stack>
          )}
          {meta.note && <Typography variant="caption" display="block" sx={{mt:1, color:'#94A3B8'}}>{meta.note}</Typography>}
        </Paper>
      )}

      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            {loading ? (
              <Box>
                <Skeleton variant="rectangular" height={28} sx={{mb:1}}/>
                <Skeleton variant="rectangular" height={320}/>
              </Box>
            ) : (
              <div style={{height:360}}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={rows.slice(0,12)}>
                    <XAxis dataKey="topic" hide/>
                    <YAxis/>
                    <Tooltip content={<TopicsTooltip/>} wrapperStyle={{ outline:'none' }} />
                    <Bar dataKey="youth_mentions" name="Youth" fill="#5EEAD4" />
                    <Bar dataKey="politician_mentions" name="Politicians" fill="#A78BFA" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" sx={{mb:1}}>Social Media Insights</Typography>
            {youthLoading ? (
              <>
                <Skeleton height={18}/>
                <Skeleton height={18}/>
                <Skeleton height={18} width="80%"/>
                <Divider sx={{my:1}}/>
                <Skeleton height={18}/>
                <Skeleton height={18}/>
              </>
            ) : (
              <Stack spacing={1}>
                <Typography variant="caption" sx={{color:'#94A3B8'}}>Total opinions analyzed: {youth.trends?.total_opinions_analyzed ?? 0}</Typography>
                {youth.trends?.overall_sentiment && (
                  <Stack direction="row" spacing={1} sx={{flexWrap:'wrap'}}>
                    {Object.entries(youth.trends.overall_sentiment).map(([k,v])=> (
                      <Chip key={k} size="small" label={`${k}: ${v}%`} />
                    ))}
                  </Stack>
                )}
                {youth.trends?.platform_activity && (
                  <>
                    <Divider sx={{my:1}}/>
                    <Typography variant="caption" sx={{color:'#94A3B8'}}>Platform activity</Typography>
                    <Stack direction="row" spacing={1} sx={{flexWrap:'wrap'}}>
                      {Object.entries(youth.trends.platform_activity).map(([p,c])=> (
                        <Chip key={p} size="small" label={`${p}: ${c}`} />
                      ))}
                    </Stack>
                  </>
                )}
                {youth.trends?.top_concerns && youth.trends.top_concerns.length>0 && (
                  <>
                    <Divider sx={{my:1}}/>
                    <Typography variant="caption" sx={{color:'#94A3B8'}}>Top concerns</Typography>
                    <Stack direction="row" spacing={1} sx={{flexWrap:'wrap'}}>
                      {youth.trends.top_concerns.slice(0,8).map((t)=> (
                        <Chip key={t} size="small" label={t} />
                      ))}
                    </Stack>
                  </>
                )}
                {youth.posts && youth.posts.length>0 && (
                  <>
                    <Divider sx={{my:1}}/>
                    <Typography variant="caption" sx={{color:'#94A3B8'}}>Recent posts</Typography>
                    <Stack spacing={1}>
                      {youth.posts.slice(0,3).map((p,i)=> (
                        <Box key={i} sx={{border:'1px solid rgba(148,163,184,0.2)', p:1, borderRadius:1}}>
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Chip size="small" label={p.platform} />
                            <Chip size="small" label={p.sentiment} />
                            <Typography variant="caption" sx={{color:'#94A3B8'}}>{new Date(p.timestamp).toLocaleString()}</Typography>
                          </Stack>
                          <Typography variant="body2" sx={{mt:0.5}}>{p.content}</Typography>
                        </Box>
                      ))}
                    </Stack>
                  </>
                )}
              </Stack>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Full topic list below the graph */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{mb:1}}>All Topics</Typography>
        {loading ? (
          <>
            <Skeleton height={28}/>
            <Skeleton height={28} width="90%"/>
            <Skeleton height={28} width="80%"/>
          </>
        ) : (
          <Stack spacing={1}>
            {rows.map((t, idx)=> (
              <Box key={`${t.topic}-${idx}`} sx={{display:'flex', alignItems:'center', justifyContent:'space-between', border:'1px solid rgba(148,163,184,0.2)', p:1, borderRadius:1}}>
                <Typography variant="body2" sx={{mr:2, flex:1}}>{t.topic}</Typography>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Chip size="small" label={`Youth: ${t.youth_mentions}`} />
                  <Chip size="small" label={`Politicians: ${t.politician_mentions}`} />
                  <Chip size="small" color={t.gap_score>0? 'error' : t.gap_score<0? 'info' : 'default'} label={`Gap: ${t.gap_score>0? '+' : ''}${t.gap_score}`} />
                </Stack>
              </Box>
            ))}
          </Stack>
        )}
      </Paper>
    </Stack>
  )
}
