export function getArray(value: any ,length: number): any[] {
    let array: any[] = []
    for (let i=0; i < length; i++) array.push(value)
    return array
}

export function getMask(array: any[], value: any) {
    let mask: boolean[] = getArray(false, array.length)
    for (let i = 0; i < array.length; i++) {
        if (value === array[i]) mask[i] = true
    }
    return mask
}

export function toTime(S: number) {
    let m = Math.floor(S / 60)
    let s = S - m * 60
    return `${m}:${s}`
}
