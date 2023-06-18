import ari from '../assets/images/Ariana_Grande_-_Positions.png'
import taylor from '../assets/images/Taylor_Swift_-Red.png'
import '../assets/styles/About.css'

export default function About() {
    return (
        <div className='About'>
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
        </div>
    );
}