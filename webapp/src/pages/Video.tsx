import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import PageBody from "../components/PageBody"
import Loading from "./LoadingPage"
import { useNavTransition } from "../utils/hooks"
import { AutoPOST, AutoGET } from "../utils/requests"
import { InputText, InputButton } from "../components/Input"
import { SERVER_FIND_PERSON_STOP, SERVER_FIND_PERSON_START, SERVER_FIND_PERSON_FORWARD } from "../api_endpoints"
import '../assets/styles/Video.css'

export default function Video() {

    const transition = useNavTransition(useNavigate())

    const [text, setText] = useState('')
    const [loading, setLoading] = useState(false)
    const [imageList, setImageList] = useState<any>([])


    function onSelect(event: any) {
        let tmp_list: any = []
        for (let i = 0; i < event.target.files.length; i++) {
            let reader = new FileReader()
            reader.readAsDataURL(event.target.files[i])
            reader.onloadend = (res: any) => {
                tmp_list.push(res.target.result)
                if (tmp_list.length == event.target.files.length) {
                    setImageList(tmp_list)
                }
            }
        }
    }

    function process() {
        // AutoPOST(SERVER_FIND_PERSON_START, {
        //     path: text,
        //     imgs: imageList
        // }, (data, status) => {
        //     if (data === '1') {
        //         let run = true
        //         while (run) {
        //             let block = true
        //             AutoGET(SERVER_FIND_PERSON_FORWARD, (data, status) => {
        //                 console.log(data['percent'])
        //                 block = false
        //             }, (error) => {
        //                 run = false
        //             })
        //             while (block) {}
        //         }
        //     }
        // }, (error) => {
        //     transition('/error', {state: error, replace: true})
        // })
    }

    useEffect(() => {
        console.log(imageList)
    }, [imageList])

    return (
        <PageBody className='Video'>
            <>
                <div className="image-submit-form">
                    {loading && <Loading />}
                    <span>
                        <label className="file-input button button-selected prevent-select">
                            Upload image
                            <input type="file" accept="image/png, image/jpeg" onChange={onSelect} multiple />
                        </label>
                    </span>
                </div>
                <InputText label="Enter path to video" value={text} onChange={setText}/>
                <div style={{height: "20px"}}></div>
                <InputButton label="Process" onClick={process}/>
            </>
        </PageBody>
    );
}