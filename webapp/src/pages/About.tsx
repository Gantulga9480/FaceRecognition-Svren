import PageBody from '../components/PageBody';
import '../assets/styles/About.css'
import ari from '../assets/images/Ariana_Grande_-_Positions.png'
import taylor from '../assets/images/Taylor_Swift_-Red.png'

export default function About() {
    return (
        <PageBody className='About'>
            <>
                <div className='About-image'>
                    <img src={ari} alt='ariana' title='Ariana Grande'></img>
                    <p>Ariana Grande</p>
                </div>
                <div className='About-image'>
                    <img src={taylor} alt='taylor' title='Taylor Swift'></img>
                    <p>Taylor Swift</p>
                </div>
            </>
        </PageBody>
    );
}