import { useEffect, useState } from 'react'
import { api } from '@/api/client'
import { Grid, Card, CardContent, Typography, Chip, Stack, Button, TextField } from '@mui/material'

type Policy = {
  id: number
  title: string
  ministry: string
  publication_date?: string
  effective_date?: string
  source_url?: string
  status: string
  details?: { what_changed?: string; who_affected?: string; what_to_do?: string }
  summary?: { english?: string; nepali?: string }
  operational_gaps?: { missing_dates?: boolean; missing_officer_info?: boolean; missing_urls?: boolean }
}

export default function Policies(){
  const [policies, setPolicies] = useState<Policy[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string|undefined>()
  const [days, setDays] = useState(7)

  useEffect(()=>{ load() },[])

  async function load(){
    setLoading(true); setError(undefined)
    try {
      const res = await api<{policies: Policy[]}>(`/api/policies/recent?days=${days}`)
      setPolicies(res.policies || [])
    } catch(e:any){ setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" spacing={1}>
        <TextField type="number" size="small" label="Days" value={days} onChange={e=>setDays(parseInt(e.target.value)||7)} />
        <Button variant="contained" onClick={load}>Load Recent</Button>
      </Stack>
      {loading && <div>Loading…</div>}
      {error && <div style={{color:'#f87171'}}>Error: {error}</div>}
      <Grid container spacing={2}>
        {policies.map(p=> (
          <Grid item xs={12} md={6} key={p.id}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">{p.title}</Typography>
                  <Chip size="small" label={p.status} color={p.status==='Action Required'?'warning':'default'} />
                </Stack>
                <Typography variant="body2" color="text.secondary">{p.ministry}</Typography>
                <Typography variant="body2" sx={{mt:1}}><strong>What changed:</strong> {p.details?.what_changed || '—'}</Typography>
                <Typography variant="body2"><strong>Who it affects:</strong> {p.details?.who_affected || '—'}</Typography>
                <Typography variant="body2"><strong>What to do:</strong> {p.details?.what_to_do || '—'}</Typography>
                <Typography variant="body2" sx={{mt:1}}><strong>EN:</strong> {p.summary?.english || '—'}</Typography>
                <Typography variant="body2"><strong>NE:</strong> {p.summary?.nepali || '—'}</Typography>
                {p.source_url && <Button href={p.source_url} target="_blank" size="small" sx={{mt:1}}>Source</Button>}
                <Stack direction="row" spacing={1} sx={{mt:1}}>
                  <Chip size="small" label={`Missing dates: ${p.operational_gaps?.missing_dates?'Yes':'No'}`} />
                  <Chip size="small" label={`Officer info: ${p.operational_gaps?.missing_officer_info?'Missing':'Present'}`} />
                  <Chip size="small" label={`URLs: ${p.operational_gaps?.missing_urls?'Missing':'Present'}`} />
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  )
}
