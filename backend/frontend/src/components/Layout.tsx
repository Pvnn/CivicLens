import { AppBar, Toolbar, Typography, Box, Container, Button, Stack } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

export default function Layout({ children }: { children: React.ReactNode }){
  return (
    <Box>
      <AppBar position="sticky" color="transparent" elevation={0} sx={{ borderBottom: '1px solid rgba(148,163,184,0.15)'}}>
        <Toolbar sx={{ display:'flex', justifyContent:'space-between' }}>
          <Typography variant="h6" color="primary">CivicLens</Typography>
          <Stack direction="row" spacing={1}>
            <Button component={RouterLink} to="/" color="inherit">Dashboard</Button>
            <Button component={RouterLink} to="/policies" color="inherit">Policies</Button>
            <Button component={RouterLink} to="/rti" color="inherit">RTI</Button>
            <Button component={RouterLink} to="/missing-topics" color="inherit">Missing Topics</Button>
          </Stack>
        </Toolbar>
      </AppBar>
      <Container sx={{ py: 3 }}>
        {children}
      </Container>
    </Box>
  )
}
