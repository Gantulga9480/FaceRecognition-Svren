import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import Loading from "../components/Loading"
import { useNavTransition } from "../utils/hooks"
import { AutoPOST, AutoGET } from "../utils/requests"
import { toTime } from "../utils/tools"
import { InputButton, InputFile } from "../components/Input"
import { ModalNotify } from "../components/Modal"
import { SimplePopup } from "../components/Popup"
import { SERVER_FIND_PERSON_STOP, SERVER_FIND_PERSON_START, SERVER_FIND_PERSON_FORWARD } from "../api_endpoints"
import '../assets/styles/Video.css'

export default function Video() {

  const transition = useNavTransition(useNavigate())

  const [video, setVideo] = useState(null)
  const [imageList, setImageList] = useState<any>([])
  const [loading, setLoading] = useState(false)
  const [toggle, setToggle] = useState(false)
  const [image, setImage] = useState(null)
  const [percent, setPercent] = useState(null)
  const [resList, setResList] = useState([])
  const [modalText, setModalText] = useState('')
  const [modalState, setModalState] = useState(false)

  const [videoPopup, setVideoPopup] = useState(true)
  const [imagePopup, setImagePopup] = useState(true)


  function onImageInput(event: any) {
    event.preventDefault()
    if (event.target.files.length > 0) {
      setLoading(true)
      let tmp_list: any = []
      let load_list = []
      for (let i = 0; i < event.target.files.length; i++) {
        load_list.push(new FileReader())
        load_list[i].readAsDataURL(event.target.files[i])
        load_list[i].onloadend = (res: any) => {
          tmp_list.push(res.target.result)
          if (tmp_list.length == event.target.files.length) {
            event.target.value = "";
            setImageList(tmp_list)
            setLoading(false)
            setImagePopup(false)
            setTimeout(() => {
              setImagePopup(true)
            }, 3000);
          }
        }
      }
    }
  }

  function onVideoInput(event: any) {
    event.preventDefault()
    if (event.target.files[0]) {
      setLoading(true)
      let reader = new FileReader()
      reader.readAsDataURL(event.target.files[0])
      reader.onloadend = (res: any) => {
        event.target.value = "";
        setVideo(res.target.result)
        setLoading(false)
        setVideoPopup(false)
        setTimeout(() => {
          setVideoPopup(true)
        }, 3000);
      }
    }
  }

  function process() {
    if (video) {
      setLoading(true)
      setResList([])
      AutoPOST(SERVER_FIND_PERSON_START, {
        video: video,
        imgs: imageList
      }, (data, _) => {
        if (data === '1') {
          setToggle(old => !old)
        }
      }, (error) => {
        transition('/error', { state: error, replace: true })
      })
    } else {
      setModalText('No video provided')
      setModalState(true)
    }
  }

  useEffect(() => {
    if (video) {
      AutoGET(SERVER_FIND_PERSON_FORWARD, (data, status) => {
        if (data.percent === 100) {
          setPercent(data.percent)
          AutoGET(SERVER_FIND_PERSON_STOP, (data, status) => {
            setLoading(false)
            setImage(null)
            setPercent(null)
            setVideo(null)
            setImageList([])
            if (data.length > 0) {
              setResList(data)
            } else {
              setModalText('Found nothing from this video')
              setModalState(true)
            }
          }, (error) => {
            transition('/error', { state: error, replace: true })
          })
        } else {
          setPercent(data.percent)
          setImage(data.frame)
          setToggle(old => !old)
        }
      }, (error) => {
        transition('/error', { state: error, replace: true })
      })
    }
  }, [toggle])

  return (
    <>
      <div className="Video">
        {loading && <Loading />}
        {percent && <span style={{ position: 'absolute', top: "33px", left: "30px" }}>{percent}%</span>}
        <div className="submit-section">
          <InputFile label="Select video" onChange={onVideoInput} accept="video/mp4" disabled={loading} width={150} height={50} />
          <span style={{ marginRight: "20px" }}></span>
          <InputFile label="Select image" onChange={onImageInput} accept="image/png,image/jpeg" multiple disabled={loading} width={150} height={50} />
          <span style={{ marginRight: "20px" }}></span>
          <InputButton label="Process" onClick={process} disabled={loading} width={150} height={50} />
        </div>
        {image &&
          <div className="image-container">
            <div className="image">
              <img src={image}></img>
            </div>
          </div>}
        <div className="result-container">
          {Array.from(resList, (item: { image: string, timestamp: number }, i) => {
            return (
              <div className="result">
                <img src={item.image} alt="result" />
                <span>{toTime(item.timestamp)}</span>
              </div>
            )
          })}
        </div>
      </div>
      {modalState && <ModalNotify title={modalText} onOk={() => { setModalState(false) }} />}
      <SimplePopup message="Video selected" disable={videoPopup} />
      <SimplePopup message="Image selected" disable={imagePopup} />
    </>
  );
}