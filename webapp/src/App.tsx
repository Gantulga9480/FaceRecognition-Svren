import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Video from './pages/Video'
import ImagePage from './pages/Image'
import Admin from './pages/Admin'
import About from './pages/About'
import Login from './pages/Login'
import Loading from './pages/LoadingPage'
import Error from './pages/Error'
import CreateUser from './pages/CreateUser'
import Sidebar from './components/Sidebar'
import './assets/styles/App.css'
import PageBody from './components/PageBody'

export default function App() {
  return (
    <div className='App'>
      <BrowserRouter>
        <Sidebar />
        <PageBody>
          <Routes>
            <Route index element={<Home />} />
            <Route path='video' element={<Video />} />
            <Route path='image' element={<ImagePage />} />
            <Route path='admin' element={<Admin />} />
            <Route path='about' element={<About />} />
            <Route path='create' element={<CreateUser />} />
            <Route path='login' element={<Login />} />
            <Route path='loading' element={<Loading />} />
            <Route path='error' element={<Error />} />
            <Route path='*' element={<Error code='404' status='Page Not Found' />} />
          </Routes>
        </PageBody>
      </BrowserRouter>
    </div>
  )
}