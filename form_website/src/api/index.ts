import type { FormDataRequest } from "../types";

export async function fetchPostFormData(request: FormDataRequest) {

    fetch(import.meta.env['VITE_API_URL'], {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
    })

}

export async function fetchGetFormData(vetToken: string) {
    fetch(`${import.meta.env['VITE_API_URL']}/form?vetToken=${vetToken}`, {
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then((vet: any) => {
        console.log(vet);
    })
}

export async function fetchGetJWTToken(): Promise<string> {
    return new Promise<string>((resolve, reject) => {

    });
}