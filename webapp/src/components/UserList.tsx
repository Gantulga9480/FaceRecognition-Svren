import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom";
import { useNavTransition } from "../utils/hooks";
import { AutoGET, AutoDELETE } from "../utils/requests"
import { SERVER_USER, SERVER_USERS } from "../api_endpoints"
import { IUser } from "../api_endpoints.interface"
import "../assets/styles/userlist.css"
import Loading from "../components/Loading";
import Button from "./Button";
import Modal from "./Modal";
import deleteIcon from "../assets/icons/delete.svg"

interface IUserProp {
    user: IUser
    onClick: (id: number) => void
}

export function User(props: IUserProp) {
    return (
        <div className="user">
            <div className="user-detail">
                <div className="user-id">{props.user.id}.</div>
                <div className="user-name">{props.user.name}</div>
                <img className="user-image" src={props.user.img_uri} alt="user_img" title={props.user.name}></img>
            </div>
            <div className="user-btn">
                <span>
                    <Button id={parseInt(props.user.id)} icon={deleteIcon} onClick={props.onClick} seleced />
                </span>
            </div>
        </div>
    )
}

export default function UserList() {

    const [users, setUsers] = useState<IUser[]>([])
    const [showmodal, setShowModal] = useState(false)
    const [nameid, setNameid] = useState({id: '', name: ''})
    const [loading, setLoading] = useState(true)
    const [refresh, setRefresh] = useState(true)

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)

    function modalYesCallback() {
        setShowModal(false);
        setLoading(true)
        AutoDELETE(`${SERVER_USER}/${nameid.id}`,
            (status) => {
                setRefresh(!refresh)
                setLoading(false)
                setNameid({id: '', name: ''})
            }, (error) => transition('/error', {state: error, replace: true}))
    }

    function buttonCb(id: number) {
        for (let i = 0; i < users.length; i++) {
            if (users[i].id === id.toString()) {
                setNameid({id: users[i].id, name: users[i].name})
                setShowModal(true)
                break
            }
        }
    }

    useEffect(() => {
        let token = sessionStorage.getItem('token')
        AutoGET(`${SERVER_USERS}?token=${token}`,
            (data: IUser[], status: string) => {
                if (status === "ok") {
                    setUsers(data)
                    setLoading(false)
                }
            },
            (error) => transition('/error', {state: error, replace: true}))
    }, [refresh])

    return (
        <>
            {loading && <Loading />}
            <div className="users">
                {showmodal && <Modal title={`Are you sure you want to delete ${nameid.name}?`}
                                    onNo={() => setShowModal(false)}
                                    onYes={modalYesCallback} />}
                <div className="users-list">
                    {Array.from(users, (user: IUser, i) => {
                        return <User key={i} user={user} onClick={buttonCb} />
                    })}
                </div>
            </div>
        </>
    )
}