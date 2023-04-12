import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Video from './pages/Video'
import Admin from './pages/Admin'
import About from './pages/About'
import Login from './pages/Login'
import Loading from './pages/LoadingPage'
import Error from './pages/Error'
import Sidebar from './components/Sidebar'
import './assets/styles/App.css'

export default function App() {
  return (
    <div className='App'>
      <BrowserRouter>
        <Sidebar />
        <Routes>
          <Route index element={<Home />} />
          <Route path='video' element={<Video />} />
          <Route path='admin' element={<Admin />} />
          <Route path='about' element={<About />} />
          <Route path='login' element={<Login />} />
          <Route path='loading' element={<Loading />} />
          <Route path='error' element={<Error />} />
          <Route path='*' element={<Error reason='404' message='Page Not Found' />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}