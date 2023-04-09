import { SyntheticEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AutoGET } from "../utils/requests";
import { SERVER_TEST } from "../api_endpoints";
import '../assets/styles/Login.css'


export default function Login() {

    const navigate = useNavigate()

    const [name, setName] = useState('')
    const [pass, setPass] = useState('')

    function handleSubmit(e: SyntheticEvent) {
        e.preventDefault()
    }

    // useEffect(() => AutoGET(SERVER_TEST, (data: any) => {}, (error) => navigate('/error', {state: error, replace: true})), [])

    return (
        <div className='main-container'>
            <div className='main-page Login'>
                <div className="Login-header">Log into admin dashboard</div>
                <form onSubmit={handleSubmit}>
                    <div>
                    <input className="form-field" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="User Name" required />
                    </div>
                    <div>
                    <input className="form-field" type="password" value={pass} onChange={(e) => setPass(e.target.value)} placeholder="Password" required />
                    </div>
                    <div>
                    <input className="form-button" type="submit" value="Log in"/>
                    </div>
                </form>
            </div>
        </div>
    );
}