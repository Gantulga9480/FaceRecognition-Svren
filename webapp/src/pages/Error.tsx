import { useLocation } from "react-router-dom"
import errorIcon from '../assets/icons/error_icon.svg'
import { IError } from "../api_endpoints.interface"
import '../assets/styles/Error.css'

export default function Error(props: IError) {

    const location = useLocation()

    let page = props.code ? (
        <>
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
        </>
    ) : (
        <>
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
        </>
    )

    return (
        <div className="Error">
            {page}
        </div>
    )
}