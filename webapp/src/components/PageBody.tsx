export default function PageBody(props: {children?: JSX.Element}) {

    return (
        <div className='main-container'>
            <div className='main-page '>
                {props.children}
            </div>
        </div>
    )
}