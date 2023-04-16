import { useLocation } from "react-router-dom"
import errorIcon from '../assets/icons/error_icon.svg'
import '../assets/styles/Error.css'
import { IError } from "../api_endpoints.interface"

export default function Error(props: IError) {
    if (props.code) {
        return (
            <div className='main-container'>
                <div className='main-page Error'>
                    <div className="Error-image">
                        <img src={errorIcon} width={100}></img>
                    </div>
                    <div>
                        <div className="Error-message">
                            {props.status}
                        </div>
                        <div className="Error-reason">
                            <span>reason:</span>
                            {props.code}
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    const location = useLocation()

    return (
        <div className='main-container'>
            <div className='main-page Error'>
                <div className="Error-image">
                    <img src={errorIcon} width={100}></img>
                </div>
                <div>
                    <div className="Error-message">
                        {location.state.status}
                    </div>
                    <div className="Error-reason">
                        <span>reason:</span>
                        {location.state.code}
                    </div>
                </div>
            </div>
        </div>
    )
}