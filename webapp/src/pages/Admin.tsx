import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AutoGET } from "../utils/requests";
import { useNavTransition } from "../utils/hooks";
import { SERVER_ADMIN } from "../api_endpoints";
import UserList from "../components/UserList";
import Loading from "../components/Loading";
import Button from "../components/Button";
import '../assets/styles/Admin.css'

export default function Admin() {

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)
    const [loading, setLoading] = useState(true)

    function addPersonCallback(id: number) {
        transition("/create")
    }

    useEffect(() => {
        let token = sessionStorage.getItem('token')
        AutoGET(`${SERVER_ADMIN}?token=${token}`, (_, status: string) => {
            if (status === 'ok') setLoading(false)
            else transition('/login',)
        }, (error) => {
            if (error.code === "401") transition('/login',)
            else transition('/error', {state: error, replace: true})
        })
    }, [])

    let page = loading ? (
        <Loading />
    ) : (
        <>
            <div className="Admin-top">
                <div>
                    <span><Button id={0} text="Add person" onClick={addPersonCallback} seleced /></span>
                </div>
            </div>
            <UserList />
        </>
    )

    return <div className='main-container'><div className='main-page Admin'>{page}</div></div>
}

