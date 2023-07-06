import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom";
import { useNavTransition } from "../utils/hooks";
import { AutoGET, AutoDELETE } from "../utils/requests"
import { SERVER_USER, SERVER_USERS } from "../api_endpoints"
import { IUser } from "../api_endpoints.interface"
import Loading from "../components/Loading";
import Button from "./Button";
import { ModalConfirm } from "./Modal";
import deleteIcon from "../assets/icons/delete.svg"
import "../assets/styles/userlist.css"

interface IUserProp {
    btnid: number,
    user: IUser,
    state: Function,
    modal: Function,
    onClick: (id?: number) => void,
}

function DeleteBtn(props: {onClick: () => void}) {
    return (
        <span className="user-delete-btn">
            <span onClick={props.onClick}>
                <img src={deleteIcon} ></img>
            </span>
        </span>
    )
}

function UserImage(props: {image: string, id: string, name: string, img_id: string, state: Function, modal: Function}) {

    function onClick() {
        props.state({id: props.id, name: props.name, count: props.img_id})
        props.modal(true)
    }

    return (
        <div className="user-image">
            <img src={props.image} alt="user_img" />
            <DeleteBtn onClick={onClick} />
        </div>
    )
}

export function User(props: IUserProp) {
    return (
        <div className="user">
            <div className="user-detail">
                <div style={{marginRight: '20px', width: '20px'}}>{props.btnid+1}.</div>
                <div className="user-name">{props.user.name}</div>
                <div className="user-id">{props.user.id}</div>
                {Array.from(props.user.image_info.images, (e: string, i) => {
                    return <UserImage key={i} image={e} id={props.user.id} name={props.user.name} img_id={props.user.image_info.image_ids[i]} state={props.state} modal={props.modal}/>
                })}
            </div>
            <div className="user-btn">
                <span>
                    <Button id={props.btnid} icon={deleteIcon} onClick={props.onClick} seleced />
                </span>
            </div>
        </div>
    )
}

export default function UserList() {

    const [users, setUsers] = useState<IUser[]>([])
    const [showmodal, setShowModal] = useState(false)
    const [currentIdName, setCurrentIdName] = useState({id: '', name: '', count: ''})
    const [loading, setLoading] = useState(true)
    const [refresh, setRefresh] = useState(true)

    const navigate = useNavigate()
    const transition = useNavTransition(navigate)

    function modalYesCallback() {
        setShowModal(false)
        setLoading(true)
        if (currentIdName.count === '') {
            AutoDELETE(`${SERVER_USER}/${currentIdName.id}`,
                (status) => {
                    setRefresh(!refresh)
                    setLoading(false)
                    setCurrentIdName({id: '', name: '', count: ''})
                }, (error) => transition('/error', {state: error, replace: true}))
        } else {
            AutoDELETE(`${SERVER_USER}/${currentIdName.id}/${currentIdName.count}`,
                (status) => {
                    setRefresh(!refresh)
                    setLoading(false)
                    setCurrentIdName({id: '', name: '', count: ''})
                }, (error) => transition('/error', {state: error, replace: true}))
        }
    }

    function buttonCb(id?: number) {
        if (typeof id === 'number') {
            setCurrentIdName({id: users[id].id, name: users[id].name, count: ''})
            setShowModal(true)
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
                {showmodal && <ModalConfirm title={`Та ${currentIdName.name} нэртэй хэрэглэгчийг устгамаар байна уу?`}
                                            onNo={() => setShowModal(false)}
                                            onYes={modalYesCallback} />}
                <div className="users-list">
                    {Array.from(users, (user: IUser, i) => {
                        return <User key={i} btnid={i} user={user} onClick={buttonCb}
                                     state={setCurrentIdName} modal={setShowModal}/>
                    })}
                </div>
            </div>
        </>
    )
}