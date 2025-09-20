import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Policies from './pages/Policies'
import RTI from './pages/RTI'
import MissingTopics from './pages/MissingTopics'

export default function App(){
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard/>} />
        <Route path="/policies" element={<Policies/>} />
        <Route path="/rti" element={<RTI/>} />
        <Route path="/missing-topics" element={<MissingTopics/>} />
        <Route path="*" element={<div>Not Found</div>} />
      </Routes>
    </Layout>
  )
}
