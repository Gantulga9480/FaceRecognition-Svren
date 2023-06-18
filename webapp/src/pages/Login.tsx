import { SyntheticEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useNavTransition } from "../utils/hooks";
import { AutoPOST } from "../utils/requests";
import { SERVER_ADMIN_LOGIN } from "../api_endpoints";
import '../assets/styles/Login.css'


export default function Login() {

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)
    const [name, setName] = useState('')
    const [pass, setPass] = useState('')
    const [fieldClass, setfieldClass] = useState("form-field")

    useEffect(() => {
        setfieldClass("form-field")
    }, [name, pass])

    function handleSubmit(e: SyntheticEvent) {
        e.preventDefault()
        let data = { name: name, pass: pass }
        AutoPOST(SERVER_ADMIN_LOGIN, data, (data: {token: string}, status: string) => {
            if (status === 'ok') {
                sessionStorage.setItem('token', data.token)
                transition('/admin')
            }
            else setfieldClass("form-wrong form-field")
        }, (error) => {
            if (error.code === "401") setfieldClass("form-wrong form-field")
            else transition('/error', {state: error, replace: true})
        })
    }

    let error = fieldClass == "form-wrong form-field" ? true : false

    return (
        <div className="Login">
            <div className="Login-header">Log into admin dashboard</div>
            <form onSubmit={handleSubmit}>
                <div>
                <input className={fieldClass} type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="User Name" required />
                </div>
                <div>
                <input className={fieldClass} type="password" value={pass} onChange={(e) => setPass(e.target.value)} placeholder="Password" required />
                </div>
                <div>
                <input className="form-button" type="submit" value="Log in"/>
                </div>
            </form>
            {error &&
                <div className="login-error">
                    Wrong name or password
            </div>}
        </div>
    );
}