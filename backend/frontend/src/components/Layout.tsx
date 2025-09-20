import { AppBar, Toolbar, Typography, Box, Container, Button, Stack } from '@mui/material'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'

export default function Layout({ children }: { children: React.ReactNode }){
  const navigate = useNavigate()
  const [authed, setAuthed] = useState(false)
  useEffect(()=>{
    setAuthed(!!localStorage.getItem('auth_token'))
  }, [])
  const logout = ()=>{
    localStorage.removeItem('auth_token')
    setAuthed(false)
    navigate('/')
  }
  return (
    <Box>
      <AppBar position="sticky" color="transparent" elevation={0} sx={{ borderBottom: '1px solid rgba(148,163,184,0.15)'}}>
        <Toolbar sx={{ display:'flex', justifyContent:'space-between' }}>
          <Typography variant="h6" color="primary">CivicLens</Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            <Button component={RouterLink} to="/" color="inherit">Dashboard</Button>
            <Button component={RouterLink} to="/policies" color="inherit">Policies</Button>
            <Button component={RouterLink} to="/rti" color="inherit">RTI</Button>
            <Button component={RouterLink} to="/missing-topics" color="inherit">Missing Topics</Button>
            <Button component={RouterLink} to="/forum" variant="contained" color="primary">Forum</Button>
            {!authed ? (
              <>
                <Button component={RouterLink} to="/login" color="inherit">Login</Button>
                <Button component={RouterLink} to="/register" color="inherit">Register</Button>
              </>
            ) : (
              <Button onClick={logout} color="inherit">Logout</Button>
            )}
          </Stack>
        </Toolbar>
      </AppBar>
      <Container sx={{ py: 3 }}>
        {children}
      </Container>
    </Box>
  )
}
