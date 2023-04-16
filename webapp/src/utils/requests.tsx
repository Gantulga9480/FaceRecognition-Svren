import { IResponse, IError } from "../api_endpoints.interface";

export async function POST(url: string, data: object) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
              },
            body: JSON.stringify(data)
        });
        return response.json();
    } catch (error) { return Promise.reject('CONNECTION_REFUSED'); }
}

export function AutoPOST(url: string,
                         data: object,
                         onSuccess: (data: any, status: string) => void,
                         onError: (error: IError) => void) {
    POST(url, data).then((res: IResponse) => {
        if (res.code === 200) onSuccess(res.data, res.status)
        else onError({code: res.code.toString(), status: res.status})
    }).catch((reason) => onError({code: reason, status: 'Server Down'}))
}

export async function GET(url: string) {
    try {
        const response = await fetch(url);
        return response.json();
    } catch (error) { return Promise.reject('CONNECTION_REFUSED'); }
}

export function AutoGET(url: string,
                        onSuccess: (data: any, status: string) => void,
                        onError: (error: IError) => void) {
    GET(url).then((res: IResponse) => {
        if (res.code === 200) onSuccess(res.data, res.status)
        else onError({code: res.code.toString(), status: res.status})
    }).catch((reason) => {onError({code: reason.toString(), status: 'Server Down'})})
}

export async function DELETE(url: string) {
    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        return response.json();
    } catch (error) { return Promise.reject('CONNECTION_REFUSED'); }
}

export function AutoDELETE(url: string, onSuccess: (status: string) => void, onError: (error: IError) => void) {
    DELETE(url).then((res: IResponse) => {
        if (res.code === 200) onSuccess(res.status)
        else onError({code: res.code.toString(), status: res.status})
    }).catch((reason) => {onError({code: reason.toString(), status: 'Server Down'})})
}
