import anim from '../assets/animations/tail-spin.svg'
import '../assets/styles/Loading.css'

export default function Loading() {
    return (
        <div className='main-container'>
            <div className='main-page Loading'>
                <img src={anim} width={150} alt='loading' title='loading' ></img>
            </div>
        </div>
    )
}