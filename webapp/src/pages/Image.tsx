import { useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import Loading from "../components/Loading"
import { InputButton, InputFile } from "../components/Input"
import { ModalTextInput, ModalNotify } from "../components/Modal"
import { useNavTransition } from "../utils/hooks"
import { AutoPOST } from "../utils/requests"
import { SERVER_DETECT, SERVER_USER_ADD } from "../api_endpoints"
import { IDetectResponseData } from "../api_endpoints.interface"
import '../assets/styles/ImagePage.css'


export default function ImagePage() {

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)

    const [modalTextInput, setModalTextInput] = useState(false)
    const [modal, setModal] = useState(false)
    const [image, setImage] = useState('')
    const [loading, setLoading] = useState(false)
    const [names, setNames] = useState<string[]|null>([])
    const [styles, setStyles] = useState<any[]|null>([])
    const imgRef = useRef()

    function onSelect(event: any) {
        let reader = new FileReader()
        reader.onload = (res: any) => {
            event.target.value = "";
            setImage(res.target.result)
            let img = new Image()
            img.onload = () => {
                AutoPOST(SERVER_DETECT, {img_uri: res.target.result}, (data: IDetectResponseData, status) => {
                    setLoading(false)
                    if (data.preds.length > 0) {
                        let nms = []
                        let stls = []
                        for (let i = 0; i < data.preds.length; i++) {
                            nms.push(data.preds[i].name)
                            let x_scale = 1
                            let y_scale = 1
                            if (img.width > 1280 || img.height > 720) {
                                x_scale = img.width / imgRef.current.width
                                y_scale = img.height / imgRef.current.height
                            }
                            stls.push({top: data.preds[i].box[1] / y_scale,
                                       left: data.preds[i].box[0] / x_scale,
                                       width: data.preds[i].box[2] / x_scale,
                                       height: data.preds[i].box[3] / y_scale
                                    })
                        }
                        setNames(nms);
                        setStyles(stls);
                        if (loading) setLoading(false)
                    } else {
                        setNames(null);
                        setLoading(false)
                    }
                }, (error) => {
                    transition('/error', {state: error, replace: true})
                })
            }
            img.src = res.target.result
        }
        if (event.target.files[0]) {
            setLoading(true)
            setNames(null)
            setStyles(null)
            reader.readAsDataURL(event.target.files[0])
        }
    }

    function onAdd() {
        setModalTextInput(true)
    }

    function onConfirm(text: string) {
        setModalTextInput(false)
        setLoading(true)
        let token = sessionStorage.getItem('token')
        AutoPOST(SERVER_USER_ADD,
            {name: text.toUpperCase(), img_uri: image, token: token},
            (data, status) => { setLoading(false); setModal(true) },
            (error) => transition("/error", {state: error, replace: true})
        )
    }

    return (
        <>
            {loading && <Loading />}
            <div className='ImagePage'>
                <div className="submit-section">
                    <InputFile label="Upload image" accept="image/png, image/jpeg" onChange={onSelect} disabled={loading} width={150} height={50} />
                </div>
                <div className="image-container">
                    <div className="image">
                        {(styles && names) && Array.from(names, (name: string, i) => {
                            return (
                                <div key={i} className={'image-overlay ' + ((name === 'Unknown') ? 'unknown' : 'known')} style={styles[i]}>
                                    { (name === 'Unknown') &&
                                        <div className="add-icon">
                                            <InputButton label="Add" onClick={ onAdd }  width={50} height={50} />
                                        </div> }
                                    <p className="prevent-select" style={{top: styles[i].height + 1, left: -2, border: (name === 'Unknown')  ? "1px solid #ff0000" : "1px solid #00ff00"}}>{name}</p>
                                </div>
                            )
                        })}
                        <img className="prevent-select" src={image} ref={imgRef} ></img>
                    </div>
                </div>
            </div>
            { modalTextInput && <ModalTextInput title="Enter name" onConfirm={ onConfirm } onBack={ () => setModalTextInput(false) } /> }
            { modal && <ModalNotify title="Successfully added. Load image again to see result" onOk={() => setModal(false)} /> }
        </>
    )
}