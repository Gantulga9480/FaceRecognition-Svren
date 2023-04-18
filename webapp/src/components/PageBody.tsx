export default function PageBody(props: {className?: string, children?: JSX.Element}) {

    let main_page_class = 'main-page '
    main_page_class += props.className ? props.className : ''

    return (
        <div className='main-container'>
            <div className={main_page_class}>
                {props.children}
            </div>
        </div>
    )
}