import { IResponse, IError } from "../api_endpoints.interface";

export async function POST(url: string, data: any) {
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
    } catch (error) {
        return Promise.reject('CONNECTION_REFUSED');
    }
}

export function AutoPOST(url: string, data: any, onSuccess: (data: any) => void, onError: (error: IError) => void) {
    POST(url, data).then((res: IResponse) => {
        if (res.code === 200) onSuccess(res.data)
        else onError({reason: res.code.toString(), message: res.status})
    }).catch((reason) => onError({reason: reason, message: 'Server Down'}))
}

export async function GET(url: string) {
    try {
        const response = await fetch(url);
        return response.json();
    } catch (error) {
        return Promise.reject('CONNECTION_REFUSED');
    }
}

export function AutoGET(url: string, onSuccess: (data: any) => void, onError: (error: IError) => void) {
    GET(url).then((res: IResponse) => {
        if (res.code === 200) onSuccess(res.data)
        else onError({reason: res.code.toString(), message: res.status})
    }).catch((reason) => {onError({reason: reason.toString(), message: 'Server Down'})})
}