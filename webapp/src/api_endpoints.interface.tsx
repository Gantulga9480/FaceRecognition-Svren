export interface IResponse {
    data: any,
    status: string,
    code: number
}

interface IPreds {
    box: number[],
    name: string,
}

export interface IDetectResponseData {
    preds: IPreds[],
}

export interface IError {
    code?: string,
    status?: string
}

export interface IUser {
    id: string,
    name: string,
    img_uri: string,
}
