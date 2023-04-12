import '../assets/styles/camera.css';
import { useState, useRef, useEffect } from 'react';
import { NavigateOptions, useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import { AutoPOST } from '../utils/requests';
import { FACE_RECOGNITION_URL } from '../api_endpoints';
import { IDetectResponseData, IError } from '../api_endpoints.interface';
import Loading from './Loading';

export default function Camera() {

    const navigate = useNavigate();
    const viewNavigate = (path: string, options?: NavigateOptions) => {
// @ts-ignore
        if (!document.startViewTransition) return navigate(path, options)
// @ts-ignore
        else return document.startViewTransition(() => navigate(path, options))
    };

    const [names, setNames] = useState<string[]|null>([]);
    const [styles, setStyles] = useState<any[]>([]);
    const [count, setCount] = useState(0);
    const [timer, setTimer] = useState(0);
    const [loading, setLoading] = useState(true)
    const webcamRef: any = useRef(null);

    function predict() {
        if (webcamRef.current) {
            const data_uri = webcamRef.current.getScreenshot();
            if (data_uri) {
                clearInterval(timer);
                AutoPOST(FACE_RECOGNITION_URL, {img_uri: data_uri}, (data: IDetectResponseData) => {
                    if (data.preds.length > 0) {
                        let nms = []
                        let stls = []
                        for (let i = 0; i < data.preds.length; i++) {
                            nms.push(data.preds[i].name)
                            stls.push({top: data.preds[i].box[1],
                                       left: data.preds[i].box[0],
                                       width: data.preds[i].box[2],
                                       height: data.preds[i].box[3],
                                       border: data.preds[i].name == "Unknown" ? "2px solid #ff0000" : "2px solid #00ff00"})
                        }
                        setNames(nms);
                        setStyles(stls);
                        if (loading) setLoading(false)
                    } else {
                        setNames(null);
                    }
                    setTimer(0)
                }, (error) => {
                    viewNavigate('/error', {state: error, replace: true})
                })
            } else {
                setCount(count + 1)
            }
        }
    }

    useEffect(() => {
        if (count === 2) {
            let state: IError = {
                reason: 'CAMERA_NOT_FOUND',
                message: "Camera Not Found",
            }
            viewNavigate('/error', {state: state, replace: true})
        }
    }, [count])

    useEffect(() => {
        clearInterval(timer);
        setTimer(setInterval(predict, 300))
    }, [])

    return (
        <div>
            {loading && <Loading />}
            <div className="web-camera">
                <Webcam screenshotFormat='image/jpeg' ref={webcamRef} videoConstraints={{width: 640, height: 480, facingMode: "user"}} />
                {names && Array.from(styles, (style: object, i) => {
                    return <div key={i} className='webcam-overlay' style={style}></div>
                })}
                {names && Array.from(names, (name: string, i) => {
                    return <p key={i} style={{top: styles[i].top+styles[i].height+2, left: styles[i].left}}>{name}</p>
                })}
            </div>
        </div>
    )
}
