import { useState } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import { api } from '@/api/client'
import { Box, Paper, Stack, TextField, Button, Typography, Alert, Link } from '@mui/material'

export default function Login(){
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string|undefined>()

  const onSubmit = async (e: React.FormEvent)=>{
    e.preventDefault()
    setError(undefined)
    setLoading(true)
    try{
      const res = await api<{success:boolean; token:string; user:{id:number; email:string; name?:string}}>('/api/auth/login', {
        method:'POST',
        body: JSON.stringify({ email, password })
      })
      if(res.success && res.token){
        localStorage.setItem('auth_token', res.token)
        navigate('/forum')
      } else {
        setError('Login failed')
      }
    }catch(e:any){ setError(e.message) } finally { setLoading(false) }
  }

  return (
    <Box sx={{ display:'flex', justifyContent:'center' }}>
      <Paper sx={{ p:3, maxWidth:420, width:'100%' }}>
        <Typography variant="h5" sx={{mb:2}}>Login</Typography>
        {error && <Alert severity="error" sx={{mb:2}}>{error}</Alert>}
        <form onSubmit={onSubmit}>
          <Stack spacing={2}>
            <TextField label="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required fullWidth/>
            <TextField label="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required fullWidth/>
            <Button type="submit" variant="contained" disabled={loading}>{loading? 'Logging in…':'Login'}</Button>
            <Typography variant="body2">No account? <Link component={RouterLink} to="/register">Register</Link></Typography>
          </Stack>
        </form>
      </Paper>
    </Box>
  )
}
