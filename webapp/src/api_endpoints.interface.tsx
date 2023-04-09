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
    reason: string,
    message: string
}