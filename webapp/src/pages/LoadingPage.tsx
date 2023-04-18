import PageBody from '../components/PageBody'
import anim from '../assets/animations/tail-spin.svg'
import '../assets/styles/LoadingPage.css'

export default function Loading() {
    return (
        <PageBody className='Loading'>
            <img src={anim} width={150} alt='loading' title='loading' ></img>
        </PageBody>
    )
}