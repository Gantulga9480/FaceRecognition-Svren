import anim from '../assets/animations/tail-spin.svg'
import '../assets/styles/loading.css'

export default function Loading() {
    return (
        <div className='loading'>
            <img src={anim} width={50} alt='loading' title='loading' ></img>
        </div>
    )
}