import '../assets/styles/button.css'

interface IButton {
    onClick: (id: number) => void,
    id: number,
    text?: string
    icon?: any,
    seleced?: boolean,
}

export default function Button(props: IButton) {

    function ButtonCallback(e: React.SyntheticEvent) {
        e.preventDefault();
        props.onClick(props.id);
    }

    let classname = 'button prevent-select';
    classname += props.seleced ? ' button-selected' : '';

    return (
        <div className={classname} onClick={ButtonCallback}>
            {props.icon &&
                <div className='button-icon'>
                    <img src={props.icon} alt='icon'></img>
                </div>
            }
            {props.text &&
                <div className='button-text hidden-half'>
                    {props.text}
                </div>
            }
        </div>
    )
}