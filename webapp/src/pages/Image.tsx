import { useState } from "react"
import { useNavigate } from "react-router-dom"
import PageBody from "../components/PageBody"
import Loading from "./LoadingPage"
import { useNavTransition } from "../utils/hooks"
import { AutoPOST } from "../utils/requests"
import { SERVER_DETECT, SERVER_DETECT_ANNOT } from "../api_endpoints"
import { IDetectResponseData } from "../api_endpoints.interface"
import '../assets/styles/ImagePage.css'


export default function ImagePage(props: any) {

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)

    const [image, setImage] = useState('')
    const [loading, setLoading] = useState(false)
    const [names, setNames] = useState<string[]|null>([])
    const [styles, setStyles] = useState<any[]>([])

    function onSelect(event: any) {
        setLoading(true)
        let reader = new FileReader()
        reader.readAsDataURL(event.target.files[0])
        reader.onload = (res: any) => {
            AutoPOST(SERVER_DETECT_ANNOT, {img_uri: res.target.result}, (data: any) => {
                // setImage(res.target.result)
                setImage(data.img_uri)
                setLoading(false)
                // if (data.preds.length > 0) {
                //     let nms = []
                //     let stls = []
                //     for (let i = 0; i < data.preds.length; i++) {
                //         nms.push(data.preds[i].name)
                //         stls.push({top: data.preds[i].box[1],
                //                    left: data.preds[i].box[0],
                //                    width: data.preds[i].box[2],
                //                    height: data.preds[i].box[3],
                //                    border: data.preds[i].name == "Unknown" ? "2px solid #ff0000" : "2px solid #00ff00"})
                //     }
                //     setNames(nms);
                //     setStyles(stls);
                //     if (loading) setLoading(false)
                // } else {
                //     setNames(null);
                //     setLoading(false)
                // }
            }, (error) => {
                transition('/error', {state: error, replace: true})
            })

        }
    }

    return (
        <PageBody className='ImagePage'>
            <>
                <div className="image-submit-form">
                    {loading && <Loading />}
                    <span>
                        <label className="file-input button button-selected prevent-select">
                            Upload image
                            <input type="file" accept="image/png, image/jpeg" onChange={onSelect} />
                        </label>
                    </span>
                </div>
                <div className="image-container">
                    <img src={image}></img>
                    <div className="image">
                        {/* {names && Array.from(styles, (style: object, i) => {
                            return <div key={i} className='image-overlay' style={style}></div>
                        })}
                        {names && Array.from(names, (name: string, i) => {
                            return <p key={i} style={{top: styles[i].top+styles[i].height+2, left: styles[i].left}}>{name}</p>
                        })} */}
                    </div>
                </div>
            </>
        </PageBody>
    )
}