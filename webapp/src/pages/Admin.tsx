import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AutoGET } from "../utils/requests";
import { SERVER_ADMIN as URL } from "../api_endpoints";
import '../assets/styles/Admin.css'

export default function Admin() {

    const navigate = useNavigate()

    useEffect(() => AutoGET(`${URL}?token=1234`, (data: string) => {
        if (data !== 'ok') navigate('/login')
    }, (error) => navigate('/error', {state: error, replace: true})), [])

    return (
        <div className='main-container'>
            <div className='main-page Admin'>
                Admin
            </div>
        </div>
    );
}