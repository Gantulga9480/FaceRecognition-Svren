import '../assets/styles/input.css'

export function InputWrapper(props: {children: any, width?: number, height?: number}) {
    return (
        <div className="input-wrapper prevent-select" style={{width: props.width, height: props.height}}>
            {props.children}
        </div>
    )
}

export function InputButton(props: {label: string, onClick: Function, disabled?: boolean, width?: number, height?: number}) {
    return (
        <InputWrapper width={props.width} height={props.height} >
            <div className={"input-button" + (props.disabled ? " input-disabled": "")}
                 onClick={(e) => {e.preventDefault(); if (!props.disabled) props.onClick()} }>
                <label>{props.label}</label>
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

export function InputFile(props: {label: string, onChange: (event: any) => void, accept?: string, multiple?: boolean, disabled?: boolean, width?: number, height?: number}) {
    return (
        <InputWrapper width={props.width} height={props.height} >
            <div className={"input-button input-file" + (props.disabled ? " input-disabled": "")}>
                <label>
                    {props.label}
                    <input
                        type="file"
                        accept={props.accept}
                        onChange={props.onChange}
                        multiple={props.multiple}
                        disabled={props.disabled} />
                </label>
            </div>
        </InputWrapper>
    )
}
