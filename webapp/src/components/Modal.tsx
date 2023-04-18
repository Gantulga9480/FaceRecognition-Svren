import "../assets/styles/modal.css"
import Button from "./Button"

export interface IModalProps {
    title: string,
    onYes: () => void,
    onNo: () => void
}

export default function Modal(props: IModalProps) {

    function yesCallback() {
        props.onYes()
    }

    function noCallback() {
        props.onNo()
    }

    return (
        <div className="modal-back">
            <div className="overlay" onClick={(e) => {e.preventDefault(); props.onNo()}}></div>
            <div className="modal">
                <div className="modal-title prevent-select">
                    {props.title}
                </div>
                <div className="modal-btn">
                    <span>
                        <Button text="Yes" onClick={yesCallback} seleced />
                    </span>
                    <span>
                        <Button text="No" onClick={noCallback} seleced />
                    </span>
                </div>
            </div>
        </div>
    )
}