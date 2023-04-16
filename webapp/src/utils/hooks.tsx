import { NavigateFunction, NavigateOptions } from "react-router-dom"

export function useNavTransition(navigate: NavigateFunction) {
    const transition = (path: string, options?: NavigateOptions) => {
    // @ts-ignore
        if (!document.startViewTransition) return navigate(path, options)
    // @ts-ignore
        else return document.startViewTransition(() => navigate(path, options))
    };
    return transition
}