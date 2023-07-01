import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from './Button'
import { getMask, getArray } from '../utils/tools';
import { useNavTransition } from '../utils/hooks';
import adminIcon from '../assets/icons/lock-open-outline.svg'
import videoIcon from '../assets/icons/media-library.svg'
import aboutIcon from '../assets/icons/community.svg'
import camereIcon from '../assets/icons/Camera.svg'
import folderIcon from '../assets/icons/Folder.svg'
import '../assets/styles/sidebar.css'

const navName = ['Камер', 'Видео', 'Зураг','Админ', 'Бидний тухай']
const navPath = ['/', '/video', '/image','/admin', '/about']
const navIcon = [camereIcon, videoIcon, folderIcon, adminIcon, aboutIcon]

let new_selected: boolean[] = getMask(navPath, location.pathname)

export default function Sidebar() {
    const navigate = useNavigate();
    const transition = useNavTransition(navigate)
    const [selected, setSelected] = useState(new_selected);

    function switchNavBtn(id: number) {
        new_selected = getArray(false, navName.length);
        new_selected[id] = true
        setSelected(new_selected)
    }

    function onClick(id?: number) {
        if (id !== undefined)
        {
            transition(navPath[id]);
            switchNavBtn(id);
        }
    }

    return (
        <nav>
            <div className="side-bar-container">
                <div className='side-bar'>
                    {Array.from(navName, (elem: string, i) => {
                        return <span key={i}><Button id={i} text={elem} icon={navIcon[i]} seleced={selected[i]} onClick={onClick} textAlign='left' resizable /></span>
                    })}
                </div>
            </div>
        </nav>
    )
}