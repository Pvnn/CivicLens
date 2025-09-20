import { Grid, Card, CardContent, Typography, Button, Stack } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

export default function Dashboard(){
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">PolicyPulse</Typography>
            <Typography variant="body2" sx={{mb:2}}>Browse recent policies, summaries, and gaps.</Typography>
            <Stack direction="row" spacing={1}>
              <Button component={RouterLink} to="/policies" variant="contained">Open</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">RTI Generator</Typography>
            <Typography variant="body2" sx={{mb:2}}>Validate and generate RTI drafts instantly.</Typography>
            <Button component={RouterLink} to="/rti" variant="contained">Open</Button>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Missing Topics</Typography>
            <Typography variant="body2" sx={{mb:2}}>Compare youth vs political focus and gaps.</Typography>
            <Button component={RouterLink} to="/missing-topics" variant="contained">Open</Button>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )
}
