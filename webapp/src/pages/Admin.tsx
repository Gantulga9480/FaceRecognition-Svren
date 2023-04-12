import { useEffect, useState } from "react";
import { NavigateOptions, useNavigate } from "react-router-dom";
import { AutoGET } from "../utils/requests";
import { SERVER_ADMIN as URL } from "../api_endpoints";
import Loading from "../components/Loading";
import '../assets/styles/Admin.css'

export default function Admin() {

    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)

    const viewNavigate = (path: string, options?: NavigateOptions) => {
// @ts-ignore
        if (!document.startViewTransition) return navigate(path, options)
// @ts-ignore
        else return document.startViewTransition(() => navigate(path, options))
    };

    useEffect(() => {
        let token = sessionStorage.getItem('token')
        AutoGET(`${URL}?token=${token}`, (data: string) => {
            if (data !== 'ok') viewNavigate('/login')
            else setLoading(false)
        }, (error) => viewNavigate('/error', {state: error, replace: true}))
        , []})

    if (loading) {
        return (
            <div className='main-container'>
                <div className='main-page Admin'>
                    <Loading />
                </div>
            </div>
        )
    } 

    return (
        <div className='main-container'>
            <div className='main-page Admin'>
                Admin
            </div>
        </div>
    );
}

