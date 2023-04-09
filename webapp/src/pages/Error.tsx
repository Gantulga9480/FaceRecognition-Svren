import { useLocation } from "react-router-dom"
import errorIcon from '../assets/icons/error_icon.svg'
import '../assets/styles/Error.css'

interface IPropsError {
    reason?: string,
    message?: string
}

export default function Error(props: IPropsError) {
    if (props.reason) {
        return (
            <div className='main-container'>
                <div className='main-page Error'>
                    <div className="Error-image">
                        <img src={errorIcon} width={100}></img>
                    </div>
                    <div>
                        <div className="Error-message">
                            {props.message}
                        </div>
                        <div className="Error-reason">
                            <span>reason:</span>
                            {props.reason}
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
                        {location.state.message}
                    </div>
                    <div className="Error-reason">
                        <span>reason:</span>
                        {location.state.reason}
                    </div>
                </div>
            </div>
        </div>
    )
}