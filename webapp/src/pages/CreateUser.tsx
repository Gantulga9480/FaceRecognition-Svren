import { useEffect, useState } from "react"
import { useNavigate } from 'react-router-dom';
import { useNavTransition } from '../utils/hooks';
import Button from "../components/Button";
import Loading from "../components/Loading";
import Camera from "../components/Camera";
import { ModalConfirm } from "../components/Modal";
import { AutoGET, AutoPOST } from "../utils/requests";
import { SERVER_USERS_INFO, SERVER_USER_ADD, SERVER_USER_ADD_IMG } from "../api_endpoints";
import { IError } from "../api_endpoints.interface";
import "../assets/styles/CreateUser.css"

interface IUserInfo {
    id: string
    name: string
}

export default function CreateUser() {

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)

    const [loading, setLoading] = useState(false)
    const [nameError, setNameError] = useState(false)
    const [btnDisabled, setBtnDisabled] = useState(false)
    const [name, setName] = useState('')
    const [id, setId] = useState('')
    const [image, setImage] = useState(null)
    const [usersInfo, setUsersInfo] = useState<IUserInfo[]>([])
    const [refresh, setRefresh] = useState(true)
    const [showmodal, setShowModal] = useState(false)
    const [camDisabled, setCamDisabled] = useState(false)

    function modalYesCallback() {
        setShowModal(false)
        let token = sessionStorage.getItem('token')
        AutoPOST(SERVER_USER_ADD_IMG, {
            token: token,
            id: id,
            name: name,
            img_uri: image},
            (data, status) => {
                setTimeout(() => {
                    setLoading(false)
                    setBtnDisabled(false)
                    setRefresh(!refresh)
                }, 500)
            },
            (error) => transition("/error", {state: error, replace: true})
        )
    }

    function modalNoCallback() {
        setShowModal(false)
        setLoading(false)
        setBtnDisabled(false)
        setCamDisabled(false)
    }

    function onSubmit() {
        setCamDisabled(true)
        if (image) {
            if (name) {
                setLoading(true)
                setBtnDisabled(true)
                for (let i = 0; i < usersInfo.length; i++) {
                    if (name.toUpperCase() === usersInfo[i].name) {
                        setId(usersInfo[i].id)
                        setShowModal(true)
                        return
                    }
                }
                let token = sessionStorage.getItem('token')
                AutoPOST(SERVER_USER_ADD,
                    {name: name.toUpperCase(), img_uri: image, token: token},
                    (data, status) => {
                        setTimeout(() => {
                            setLoading(false)
                            setBtnDisabled(false)
                            setCamDisabled(false)
                            setRefresh(!refresh)
                        }, 500)
                    },
                    (error) => transition("/error", {state: error, replace: true})
                )
            } else {
                setNameError(true)
            }
        } else {
            let state: IError = {
                code: 'CAMERA_NOT_FOUND',
                status: "Camera Not Found",
            }
            transition('/error', {state: state, replace: true})
        }
    }

    useEffect(() => {
        setLoading(true)
        let token = sessionStorage.getItem('token')
        AutoGET(`${SERVER_USERS_INFO}?token=${token}`, (data: IUserInfo[], status: string) => {
            if (status === 'ok') {
                setUsersInfo(data)
                setTimeout(() => {
                    setLoading(false)
                }, 500)
            }
            else transition('/error', {state: {status: 'Failed to load users', code: 500}, replace: true})
        }, (error) => {
            if (error.code === "401") transition('/login',)
            else transition('/error', {state: error, replace: true})
        })
    }, [refresh])

    return (
        <>
            {loading && <Loading />}
            <div className="Create">
                {showmodal && <ModalConfirm title={`User ${name} aleady exists. Add new image to ${name}?`}
                                            onNo={modalNoCallback}
                                            onYes={modalYesCallback} />}
                <Camera getImg={setImage} disabled={camDisabled}/>
                <div className="Create-name">
                    <input type="text" value={name} placeholder="Enter user name" onChange={(e) => { setName(e.target.value); setNameError(false) }} required />
                    {nameError && <p style={{color: "red"}}>Please provide user name</p>}
                </div>
                <span><Button id={0} text="Submit" onClick={onSubmit} seleced disabled={btnDisabled}/></span>
            </div>
        </>
    )
}