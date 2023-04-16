import "../assets/styles/CreateUser.css"
import { SERVER_USER_ADD } from "../api_endpoints"
import { AutoPOST } from "../utils/requests"
import { useRef, useState } from "react"
import { useNavigate } from 'react-router-dom';
import { useNavTransition } from '../utils/hooks';
import Webcam from 'react-webcam';
import Button from "../components/Button";
import Loading from "../components/Loading";


export default function CreateUser() {

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)

    const [loading, setLoading] = useState(false)
    const [name, setName] = useState('')
    const webcamRef: any = useRef(null);

    function onSubmit(id: number) {
        if (webcamRef.current) {
            const img_uri = webcamRef.current.getScreenshot();
            if (img_uri) {
                if (name) {
                    setLoading(true)
                    AutoPOST(SERVER_USER_ADD, {name: name, img_uri: img_uri},
                        (data, status) => setLoading(false),
                        (error) => transition("/error", {state: error, replace: true})
                    )
                } else {

                }
            }
        }
    }

    return (
        <div className='main-container'>
            <div className='main-page Create'>
                {loading && <Loading />}
                <Webcam screenshotFormat='image/jpeg' ref={webcamRef} videoConstraints={{width: 640, height: 480, facingMode: "user"}}/>
                <div>
                    <input type="text" value={name} onChange={(e) => setName(e.target.value)} required/>
                </div>
                <span><Button id={0} text="Submit" onClick={onSubmit} seleced/></span>
            </div>
        </div>
    )
}