import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from './Button'
import { getMask, getArray } from '../utils/tools';
import homeIcon from '../assets/icons/house-line.svg'
import adminIcon from '../assets/icons/lock-open-outline.svg'
import videoIcon from '../assets/icons/media-library.svg'
import aboutIcon from '../assets/icons/community.svg'
import '../assets/styles/sidebar.css'

const navName = ['Home', 'Video', 'Adminstration', 'About us']
const navPath = ['/', '/video', '/admin', '/about']
const navIcon = [homeIcon, videoIcon, adminIcon, aboutIcon]

let new_selected: boolean[] = getMask(navPath, location.pathname)

export default function Sidebar() {
    const navigate = useNavigate();
    const [selected, setSelected] = useState(new_selected);
    const viewNavigate = (newRoute: string) => {
// @ts-ignore
        if (!document.startViewTransition) return navigate(newRoute)
// @ts-ignore
        else return document.startViewTransition(() => navigate(newRoute))
      };

    function switchNavBtn(id: number) {
        new_selected = getArray(false, navName.length);
        new_selected[id] = true
        setSelected(new_selected)
    }

    function onClick(id: number) {
        viewNavigate(navPath[id]);
        switchNavBtn(id);
    }

    return (
        <div className="side-bar-container">
            <div className='side-bar'>
                {Array.from(navName, (elem: string, i) => {
                    return <Button key={i} id={i} text={elem} icon={navIcon[i]} seleced={selected[i]} onClick={onClick}/>
                })}
            </div>
        </div>
    )
}