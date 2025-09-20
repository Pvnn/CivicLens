import { useEffect, useState } from 'react'
import { api } from '@/api/client'
import { Stack, Typography, List, ListItem, ListItemText, Chip } from '@mui/material'

type Item = { source: string; title: string; url?: string; score?: number; author?: string; created_at?: string; description?: string; language?: string }

export default function CareerFeed(){
  const [items, setItems] = useState<Item[]>([])
  const [error, setError] = useState<string|undefined>()
  useEffect(()=>{ (async()=>{
    try { const res = await api<{success:boolean; data: Item[]}>('/api/career-feed'); setItems(res.data || []) } catch(e:any){ setError(e.message) }
  })() },[])
  return (
    <Stack spacing={2}>
      <Typography variant="h5">Career Feed</Typography>
      {error && <div style={{color:'#f87171'}}>Error: {error}</div>}
      <List>
        {items.map((it, idx)=> (
          <ListItem key={idx} component="a" href={it.url||'#'} target="_blank" sx={{borderBottom:'1px solid rgba(148,163,184,0.15)'}}>
            <ListItemText primary={it.title} secondary={`${it.source}${it.author? ' • '+it.author:''}`} />
            {it.language && <Chip size="small" label={it.language} sx={{ml:1}}/>}
            {typeof it.score==='number' && <Chip size="small" label={`Score ${it.score}`} sx={{ml:1}}/>}
          </ListItem>
        ))}
      </List>
    </Stack>
  )
}
