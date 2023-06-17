import { useState } from "react"
import '../assets/styles/input.css'

export function InputWrapper(props: {children: any}) {
    return (
        <div className="input-wrapper prevent-select">
            {props.children}
        </div>
    )
}

export function InputButton(props: {label: string, onClick: Function}) {
    return (
        <InputWrapper>
            <div className="input-button" onClick={(e) => {e.preventDefault(); props.onClick()} }>
                <div>{props.label}</div>
            </div>
        </InputWrapper>
    )
}

export function InputText(props: {label: string, value: string, onChange: Function}) {
    return (
        <InputWrapper>
            <div className="input-text">
                <label>{props.label}</label>
                <input type="text" value={props.value} onChange={(e) => props.onChange(e.target.value)} />
            </div>
        </InputWrapper>
    )
}

