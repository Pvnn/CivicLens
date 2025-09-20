import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Policies from './pages/Policies'
import RTI from './pages/RTI'
import MissingTopics from './pages/MissingTopics'
import Forum from './pages/Forum'
import Login from './pages/Login'
import Register from './pages/Register'

export default function App(){
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard/>} />
        <Route path="/policies" element={<Policies/>} />
        <Route path="/rti" element={<RTI/>} />
        <Route path="/missing-topics" element={<MissingTopics/>} />
        <Route path="/forum" element={<Forum/>} />
        <Route path="/login" element={<Login/>} />
        <Route path="/register" element={<Register/>} />
        <Route path="*" element={<div>Not Found</div>} />
      </Routes>
    </Layout>
  )
}
