import "../assets/styles/CreateUser.css"
import { SERVER_USER_ADD } from "../api_endpoints"
import { AutoPOST } from "../utils/requests"
import { useRef, useState } from "react"
import { useNavigate } from 'react-router-dom';
import { useNavTransition } from '../utils/hooks';
import Button from "../components/Button";
import Loading from "../components/Loading";
import { IError } from "../api_endpoints.interface";
import PageBody from "../components/PageBody";
import Camera from "../components/Camera";


export default function CreateUser() {

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)

    const [loading, setLoading] = useState(false)
    const [nameError, setNameError] = useState(false)
    const [btnDisabled, setBtnDisabled] = useState(false)
    const [name, setName] = useState('')
    const [image, setImage] = useState(null)

    function onSubmit() {
        if (image) {
            if (name) {
                setLoading(true)
                setBtnDisabled(true)
                AutoPOST(SERVER_USER_ADD, {name: name, img_uri: image},
                    (data, status) => { setLoading(false); setBtnDisabled(false) },
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

    return (
        <PageBody className="Create">
            <>
                {loading && <Loading />}
                <Camera getImg={setImage}/>
                <div className="Create-name">
                    <input type="text" value={name} onChange={(e) => { setName(e.target.value); setNameError(false) }} required/>
                    {nameError && <p style={{color: "red"}}>Please provide user name</p>}
                </div>
                <span><Button id={0} text="Submit" onClick={onSubmit} seleced disabled={btnDisabled}/></span>
            </>
        </PageBody>
    )
}