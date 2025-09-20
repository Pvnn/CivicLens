import { useEffect, useMemo, useState } from 'react'
import { api } from '@/api/client'
import {
  Box,
  Paper,
  Stack,
  Typography,
  TextField,
  Button,
  Grid,
  Chip,
  Divider,
  IconButton,
  Collapse,
  Alert,
} from '@mui/material'
import ThumbUpAltOutlinedIcon from '@mui/icons-material/ThumbUpAltOutlined'
import ThumbDownAltOutlinedIcon from '@mui/icons-material/ThumbDownAltOutlined'


type User = { id:number; email:string; name?:string|null }
type Idea = { id:number; content:string; user:User; created_at:string; score:number; comments_count:number }
type Comment = { id:number; content:string; user:User; created_at:string }

export default function Forum(){
  const [authed, setAuthed] = useState(false)
  const [top, setTop] = useState<Idea[]>([])
  const [ideas, setIdeas] = useState<Idea[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string|undefined>()

  const [newIdea, setNewIdea] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(()=>{
    setAuthed(!!localStorage.getItem('auth_token'))
  },[])

  const loadAll = async ()=>{
    setLoading(true)
    setError(undefined)
    try{
      const [t, l] = await Promise.all([
        api<{success:boolean; data: Idea[]}>('/api/forum/ideas/top'),
        api<{success:boolean; data: Idea[]}>('/api/forum/ideas'),
      ])
      setTop(t.data || [])
      setIdeas(l.data || [])
    }catch(e:any){ setError(e.message) } finally { setLoading(false) }
  }

  useEffect(()=>{ loadAll() }, [])

  const onSubmitIdea = async (e: React.FormEvent)=>{
    e.preventDefault()
    if (!newIdea.trim()) return
    setSubmitting(true)
    try{
      await api('/api/forum/ideas', { method:'POST', body: JSON.stringify({ content: newIdea.trim() }) })
      setNewIdea('')
      await loadAll()
    }catch(e:any){ setError(e.message) } finally { setSubmitting(false) }
  }

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Youth Engagement Forum</Typography>
      {error && <Alert severity="error">{error}</Alert>}

      {/* Top 3 ideas */}
      <Paper sx={{ p:2 }}>
        <Typography variant="subtitle1" sx={{mb:1}}>Top Ideas</Typography>
        <Grid container spacing={2}>
          {(loading ? Array.from({length:3}) : top).map((it:any, idx)=> (
            <Grid key={idx} item xs={12} md={4}>
              <Paper sx={{ p:2, height:'100%' }}>
                {loading ? (
                  <>
                    <Box sx={{ bgcolor:'rgba(148,163,184,0.15)', height:18, mb:1 }} />
                    <Box sx={{ bgcolor:'rgba(148,163,184,0.15)', height:18, width:'80%' }} />
                  </>
                ) : (
                  <>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{mb:1}}>
                      <Chip size="small" color="success" label={`Score: ${it.score}`}/>
                      <Typography variant="caption" sx={{ color:'#94A3B8' }}>{new Date(it.created_at).toLocaleString()}</Typography>
                    </Stack>
                    <Typography variant="body1" sx={{ mb:1 }}>{it.content}</Typography>
                    <Typography variant="caption" sx={{ color:'#94A3B8' }}>by {it.user?.name || it.user?.email}</Typography>
                  </>
                )}
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Submit idea */}
      <Paper sx={{ p:2 }}>
        <Typography variant="subtitle1" sx={{mb:1}}>Submit a new idea</Typography>
        {!authed && (
          <Alert severity="info" sx={{mb:2}}>Login or Register to submit, vote, and comment.</Alert>
        )}
        <form onSubmit={onSubmitIdea}>
          <Stack spacing={1}>
            <TextField
              placeholder="Share your policy idea or issue..."
              value={newIdea}
              onChange={e=>setNewIdea(e.target.value)}
              multiline minRows={3}
              disabled={!authed}
            />
            <Stack direction="row" spacing={1}>
              <Button type="submit" variant="contained" disabled={!authed || submitting}>{submitting? 'Submitting…':'Submit'}</Button>
            </Stack>
          </Stack>
        </form>
      </Paper>

      {/* Ideas list */}
      <Paper sx={{ p:2 }}>
        <Typography variant="subtitle1" sx={{mb:1}}>All Ideas</Typography>
        <Stack spacing={1}>
          {ideas.map((it)=> (
            <IdeaRow key={it.id} idea={it} onVoted={(score)=>{
              setIdeas(prev => prev.map(p=> p.id===it.id? {...p, score}: p))
              setTop(prev => prev.map(p=> p.id===it.id? {...p, score}: p))
            }} />
          ))}
        </Stack>
      </Paper>
    </Stack>
  )
}

function IdeaRow({ idea, onVoted }:{ idea: Idea; onVoted: (score:number)=>void }){
  const [score, setScore] = useState(idea.score)
  const [commentsOpen, setCommentsOpen] = useState(false)
  const [comments, setComments] = useState<Comment[]|null>(null)
  const [newComment, setNewComment] = useState('')
  const authed = useMemo(()=> !!localStorage.getItem('auth_token'), [])

  const vote = async (value: 1 | -1)=>{
    try{
      const res = await api<{success:boolean; data:{idea_id:number; score:number}}>(`/api/forum/ideas/${idea.id}/vote`, { method:'POST', body: JSON.stringify({ value }) })
      if(res.success){ setScore(res.data.score); onVoted(res.data.score) }
    }catch{}
  }

  const toggleComments = async ()=>{
    const next = !commentsOpen
    setCommentsOpen(next)
    if (next && comments===null){
      try{
        const res = await api<{success:boolean; data: Comment[]}>(`/api/forum/ideas/${idea.id}/comments`)
        setComments(res.data || [])
      }catch{ setComments([]) }
    }
  }

  const addComment = async ()=>{
    if (!newComment.trim()) return
    try{
      const res = await api<{success:boolean; data:{id:number; content:string; created_at:string}}>(`/api/forum/ideas/${idea.id}/comments`, { method:'POST', body: JSON.stringify({ content: newComment.trim() }) })
      setNewComment('')
      const me = await api<{success:boolean; user:User}>(`/api/auth/me`)
      setComments(prev => ([...(prev||[]), { id: res.data.id, content: res.data.content, created_at: res.data.created_at, user: me.user }]))
    }catch{}
  }

  return (
    <Paper sx={{ p:1.5 }}>
      <Stack direction="row" spacing={1} alignItems="flex-start" justifyContent="space-between">
        <Stack spacing={0.5} sx={{flex:1}}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip size="small" label={`Score: ${score}`}/>
            <Typography variant="caption" sx={{ color:'#94A3B8' }}>{new Date(idea.created_at).toLocaleString()}</Typography>
          </Stack>
          <Typography variant="body1">{idea.content}</Typography>
          <Typography variant="caption" sx={{ color:'#94A3B8' }}>by {idea.user?.name || idea.user?.email}</Typography>
        </Stack>
        <Stack direction="row" spacing={1} alignItems="center">
          <IconButton size="small" onClick={()=>vote(1)} disabled={!authed} aria-label="upvote"><ThumbUpAltOutlinedIcon/></IconButton>
          <IconButton size="small" onClick={()=>vote(-1)} disabled={!authed} aria-label="downvote"><ThumbDownAltOutlinedIcon/></IconButton>
        </Stack>
      </Stack>
      <Divider sx={{my:1}}/>
      <Stack spacing={1}>
        <Button size="small" onClick={toggleComments}>
          {commentsOpen? 'Hide comments' : `Show comments${idea.comments_count? ` (${idea.comments_count})` : ''}`}
        </Button>
        <Collapse in={commentsOpen} timeout="auto" unmountOnExit>
          <Stack spacing={1} sx={{mt:1}}>
            {(comments||[]).map(c => (
              <Box key={c.id} sx={{border:'1px solid rgba(148,163,184,0.2)', p:1, borderRadius:1}}>
                <Typography variant="body2" sx={{mb:0.5}}>{c.content}</Typography>
                <Typography variant="caption" sx={{ color:'#94A3B8' }}>by {c.user?.name || c.user?.email} • {new Date(c.created_at).toLocaleString()}</Typography>
              </Box>
            ))}
            <Stack direction="row" spacing={1}>
              <TextField size="small" placeholder="Add a comment" value={newComment} onChange={e=>setNewComment(e.target.value)} fullWidth disabled={!authed}/>
              <Button onClick={addComment} variant="contained" disabled={!authed || !newComment.trim()}>Post</Button>
            </Stack>
          </Stack>
        </Collapse>
      </Stack>
    </Paper>
  )
}
