import { useState } from 'react'
import { api } from '@/api/client'
import { Stack, TextField, Button, Typography, Paper } from '@mui/material'

export default function RTI(){
  const [url, setUrl] = useState('')
  const [complaint, setComplaint] = useState('')
  const [complaintId, setComplaintId] = useState<number|undefined>()
  const [rtiId, setRtiId] = useState<number|undefined>()
  const [output, setOutput] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(){
    setBusy(true); setOutput('')
    try { const res = await api<any>('/api/rti/submit-complaint', {method:'POST', body: JSON.stringify({url, complaint})}); setComplaintId(res.id); setOutput(JSON.stringify(res, null, 2)) } catch(e:any){ setOutput(e.message) } finally { setBusy(false) }
  }
  async function validate(){
    if (!complaintId) return
    setBusy(true); setOutput('')
    try { const res = await api<any>(`/api/rti/validate/${complaintId}`); setOutput(JSON.stringify(res, null, 2)) } catch(e:any){ setOutput(e.message) } finally { setBusy(false) }
  }
  async function generate(){
    if (!complaintId) return
    setBusy(true); setOutput('')
    try { const res = await api<any>(`/api/rti/generate/${complaintId}`, {method:'POST'}); setRtiId(res.rti_id); setOutput(JSON.stringify(res, null, 2)) } catch(e:any){ setOutput(e.message) } finally { setBusy(false) }
  }
  function download(){ if (rtiId) window.location.href = `/api/rti/download/${rtiId}` }

  return (
    <Stack spacing={2}>
      <Typography variant="h5">RTI Generator</Typography>
      <TextField label="Government Policy URL" value={url} onChange={e=>setUrl(e.target.value)} fullWidth />
      <TextField label="Your Complaint / Missing Info" value={complaint} onChange={e=>setComplaint(e.target.value)} multiline minRows={4} fullWidth />
      <Stack direction="row" spacing={1}>
        <Button variant="contained" onClick={submit} disabled={busy}>1) Submit</Button>
        <Button variant="contained" onClick={validate} disabled={busy || !complaintId}>2) Validate</Button>
        <Button variant="contained" onClick={generate} disabled={busy || !complaintId}>3) Generate</Button>
        <Button variant="outlined" onClick={download} disabled={!rtiId}>4) Download PDF</Button>
      </Stack>
      <Paper sx={{p:2, bgcolor:'#0b1220', border:'1px solid rgba(148,163,184,0.15)'}}>
        <pre style={{whiteSpace:'pre-wrap', margin:0}}>{output}</pre>
      </Paper>
    </Stack>
  )
}
