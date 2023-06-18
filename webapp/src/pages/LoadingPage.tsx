import anim from '../assets/animations/tail-spin.svg'
import '../assets/styles/LoadingPage.css'

export default function LoadingPage() {
    return (
        <div className='Loading'>
            <img src={anim} width={150} alt='loading' title='loading' ></img>
        </div>
    )
}