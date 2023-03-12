import { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import '../assets/styles/Home.css';

const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: "user"
};
let timer_id = 0;

async function postData(url = '', data = {}) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            body: data
        });
        return response.json();
    } catch (error) {
        return false;
    }
}

function Home() {

    const [name, setName] = useState(null);
    const [style, setStyle] = useState(null);
    const webcamRef = useRef(null);

    function take_snapshot() {
        const data_uri = webcamRef.current.getScreenshot();
        postData('http://127.0.0.1:8080', data_uri).then((res) => {
            if (res) {
                setName(res["name"]);
                setStyle({top: res["box"][1]+30,
                          left: res["box"][0]+window.innerWidth/2 - 320,
                          width: res["box"][2],
                          height: res["box"][3],
                          border: res["name"] == "Unknown" ? "3px solid #ff0000" : "3px solid #00ff00"});
            } else {
                setName("Server down");
                setStyle({display: "None"});
            }
        });
    }
    useEffect(() => {
        timer_id = setInterval(take_snapshot, 1000);
    }, [])

    return (
        <div className="Home">
            <div className='webcam-container'>
                <Webcam screenshotFormat='image/jpeg' ref={webcamRef} videoConstraints={videoConstraints} />
                <div className='webcam-overlay' style={style}></div>
            </div>
            <div className='name-container'>{name}</div>
        </div>
    )
}

export default Home;
