import type { FormDataRequest } from "../types";

export async function createOrOverwriteVet(request: FormDataRequest) {
    return new Promise<string[]>((resolve, reject) => {
        fetch(`${import.meta.env['VITE_API_URL']}/form/create-or-overwrite-vet`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${import.meta.env['VITE_JWT_TOKEN']}`
            },
            body: JSON.stringify(request)
        })
            .catch(error => {
                console.error(error);
            })
    });
}

export async function sendVetRegistrationEmail(email: string) {
    return new Promise<string[]>((resolve, reject) => {
        fetch(`${import.meta.env['VITE_API_URL']}/form/send-vet-registration-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${import.meta.env['VITE_JWT_TOKEN']}`
            },
            body: JSON.stringify({
                emailAddress: email
            })
        })
            .then(response => response.json())
            .then((token) => {
                console.log(token);
            })
            .catch(error => {
                console.error(error);
            })
    });
}

export async function getVetWithToken(vetToken: string): Promise<FormDataRequest | null> {
    return new Promise<FormDataRequest | null>((resolve, reject) => {
        fetch(`${import.meta.env['VITE_API_URL']}/form/vet`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${vetToken}`,
            },
        })
            .then(response => {

                if (response.status === 404) {
                    resolve(null);
                } else {
                    return response.json();
                }
            })
            .then((vet: FormDataRequest) => {
                resolve(vet);
            })
            .catch(error => {
                console.error(error);
                resolve(null);
            })
    });
}

export async function getTreatments(): Promise<string[]> {
    return new Promise<string[]>((resolve, _) => {
        fetch(`${import.meta.env['VITE_API_URL']}/treatments`, {
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then((treatments: string[]) => {
                resolve(treatments);
            })
            .catch(error => {
                console.error(error);
                resolve([]);
            })
    });
}