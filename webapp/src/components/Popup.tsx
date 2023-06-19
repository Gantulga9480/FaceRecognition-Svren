import '../assets/styles/popup.css'

function PopupWrapper(props: {children: JSX.Element, disable?: boolean}) {
    return (
        <div className={"popup-wrapper" + (props.disable ? " popup-disabled" : "")}>
            {props.children}
        </div>
    )
}

export function SimplePopup(props: {message: string, disable?: boolean}) {
    return (
        <PopupWrapper disable={props.disable} >
            <div className="simple-popup">
                <span>{props.message}</span>
            </div>
        </PopupWrapper>
    )
}

