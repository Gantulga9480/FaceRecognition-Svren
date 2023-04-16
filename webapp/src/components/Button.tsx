import '../assets/styles/button.css'

interface IButton {
    onClick: (id: number) => void,
    id: number,
    text?: string
    icon?: any,
    seleced?: boolean,
    textAlign?: string,
    resizable?: boolean
}

export default function Button(props: IButton) {

    function ButtonCallback(e: React.SyntheticEvent) {
        e.preventDefault();
        props.onClick(props.id);
    }

    let classname = 'button prevent-select';
    classname += props.seleced ? ' button-selected' : '';
    let textAlign: any = props.textAlign ? props.textAlign : 'center'
    let margin = (props.icon && props.text) ? "10px" : "0px"
    let textClass = props.resizable ? 'button-text hidden-half' : 'button-text'

    return (
        <div className={classname} onClick={ButtonCallback}>
            {props.icon &&
                <div className='button-icon'>
                    <img src={props.icon} alt='icon'></img>
                </div>
            }
            {props.text &&
                <div className={textClass} style={{textAlign: textAlign, marginLeft: margin}}>
                    {props.text}
                </div>
            }
        </div>
    )
}