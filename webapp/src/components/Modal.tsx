import { useState } from "react"
import "../assets/styles/modal.css"
import Button from "./Button"
import { InputText } from "./Input"

export interface IModalProps {
    title: string,
    onYes: () => void,
    onNo: () => void
}

export interface IModalNotifyProps {
    title: string,
    onOk: () => void,
}

export interface IModalTextInputProps {
    title: string,
    onConfirm: (text: string) => void,
    onBack: () => void
}

export function ModalConfirm(props: IModalProps) {

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
                        <Button text="Тийм" onClick={yesCallback} seleced />
                    </span>
                    <span>
                        <Button text="Үгүй" onClick={noCallback} seleced />
                    </span>
                </div>
            </div>
        </div>
    )
}

export function ModalNotify(props: IModalNotifyProps) {
    return (
        <div className="modal-back">
            <div className="overlay" onClick={(e) => {e.preventDefault(); props.onOk()}}></div>
            <div className="modal">
                <div className="modal-title prevent-select">
                    {props.title}
                </div>
                <div className="modal-btn">
                    <span>
                        <Button text="Хаах" onClick={() => props.onOk()} seleced />
                    </span>
                </div>
            </div>
        </div>
    )
}

export function ModalTextInput(props: IModalTextInputProps) {

    const [text, setText] = useState('')

    function yesCallback() {
        if (text === '') {
            
        } else {
            props.onConfirm(text)
        }
    }

    function noCallback() {
        props.onBack()
    }

    return (
        <div className="modal-back">
            <div className="overlay" onClick={(e) => {e.preventDefault(); props.onBack()}}></div>
            <div className="modal">
                <div className="modal-title prevent-select">
                    {props.title}
                </div>
                <InputText label="" value={text} onChange={setText} />
                <div style={{height: "20px", width: "100%"}}></div>
                <div className="modal-btn">
                    <span style={{width: "100px"}}>
                        <Button text="Хадгалах" onClick={yesCallback} seleced />
                    </span>
                    <span style={{width: "100px"}}>
                        <Button text="Буцах" onClick={noCallback} seleced />
                    </span>
                </div>
            </div>
        </div>
    )
}