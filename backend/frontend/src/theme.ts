import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#5EEAD4' },
    secondary: { main: '#A78BFA' },
    background: { default: '#0B1220', paper: '#0F172A' },
    text: { primary: '#E2E8F0', secondary: '#94A3B8' }
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif',
    h4: { fontWeight: 700 },
    h6: { fontWeight: 600 }
  },
})

export default theme
