import { v4 as uuidv4 } from 'uuid';

export type LabelObject<T extends string> = {
    [index in T]: string;
}

export function convertVetToFormDataRequest(vet: Vet): FormDataRequest {
    return {
        clinicName: vet.contact.clinicName,
        nameInformation: vet.name,
        contacts: [
            {
                type: "tel:landline",
                value: vet.contact.telephone
            },
            {
                type: "email",
                value: vet.contact.email
            },
        ],
        location: {
            address: vet.address
        },
        treatments: vet.treatments.treatments,
        openingHours: vet.openingHours,
        emergencyTimes: vet.emergencyTimes,
        timezone: vet.timezone
    }
}

export function convertFormDataRequestToVet(request: FormDataRequest): Vet {
    return {
        contact: {
            clinicName: request.clinicName,
            telephone: request.contacts.find(entry => entry.type === "tel:landline")?.value || '',
            email: request.contacts.find(entry => entry.type === "email")?.value || '',
        },
        name: request.nameInformation,
        address: request.location.address,
        treatments: {
            treatments: request.treatments,
        },
        openingHours: request.openingHours,
        emergencyTimes: request.emergencyTimes,
        timezone: request.timezone
    }
}

export type FormDataRequest = {
    clinicName: string,
    nameInformation: NameInformation,
    contacts: ContactRequestEntry[],
    location: {
        address: Address
    },
    treatments: string[],
    openingHours: OpeningHoursOverview,
    emergencyTimes?: EmergencyTimeRequest[],
    timezone: string
}

export type ContactRequestEntry = {
    type: string,
    value: string
}

export type Vet = {
    contact: Contact,
    name: NameInformation,
    address: Address,
    treatments: TreatmentInformation,
    openingHours: OpeningHoursOverview,
    emergencyTimes?: EmergencyTimeRequest[],
    timezone: string
}

export type Contact = {
    clinicName: string,
    email: string,
    telephone: string
}

export type NameInformation = {
    formOfAddress?: FormOfAddress,
    title?: Title,
    firstName: string,
    lastName: string
}

export type Address = {
    street: string,
    number: string,
    city: string,
    zipCode: string,
}

export type TreatmentInformation = {
    treatments: string[],
    other?: string,
    note?: string,
}

export type EmergencyTimeRequest = {
    startDate: string;
    endDate: string;
    fromTime: string;
    toTime: string;
    days: string[]
}

export function convertEmergencyTimeToRequest(emergencyTime: EmergencyTime): EmergencyTimeRequest {
    return {
        startDate: emergencyTime.startDate.toLocaleDateString(undefined, {
            dateStyle: 'medium'
        }),
        endDate: emergencyTime.endDate.toLocaleDateString(undefined, {
            dateStyle: 'medium'
        }),
        fromTime: emergencyTime.fromTime.toLocaleTimeString(undefined, {
            timeStyle: 'short'
        }),
        toTime: emergencyTime.toTime.toLocaleTimeString(undefined, {
            timeStyle: 'short'
        }),
        days: emergencyTime.days
    }
}

export const TreatmentLabels: LabelObject<string> = {
    dogs: 'Hund',
    cats: 'Katze',
    horses: 'Pferd',
    small_animals: 'Kleintiere',
    misc: 'Sonstige'
};

export type TreatmentState = {
    [index: string]: boolean;
};

export type Day = 'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri' | 'Sat' | 'Sun';
export const Days: Day[] = [
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'Sun'
];

export const DayLabels: LabelObject<Day> = {
    Mon: 'Montag',
    Tue: 'Dienstag',
    Wed: 'Mittwoch',
    Thu: 'Donnerstag',
    Fri: 'Freitag',
    Sat: 'Samstag',
    Sun: 'Sonntag'
};

export type OpeningHoursInformation = {
    from: string;
    to: string;
};

export type OpeningHoursOverview = {
    [index in Day]: OpeningHoursInformation | undefined;
};

export type OpeningHours = {
    [index in Day]: string | undefined;
};
export type DaySelectionInformation = {
    [index in Day]: boolean;
};

export type FormOfAddress = 'mr' | 'ms' | 'divers' | 'not_specified';
export const FormOfAddresses: FormOfAddress[] = ['mr', 'ms', 'divers', 'not_specified'];

export const FormOfAddressLabels: LabelObject<FormOfAddress> = {
    mr: 'Herr',
    ms: 'Frau',
    divers: 'Divers',
    not_specified: 'Keine Angabe'
}

export type Title = 'not_specified' | 'dr_med' | 'dr_med_dent' | 'dr_med_vent' | 'dr_phil' | 'dr_paed' | 'dr_rer_nat' | 'dr_rer_pol' | 'dr_ing';
export const Titles: Title[] = [
    'not_specified',
    'dr_med',
    'dr_med_dent',
    'dr_med_vent',
    'dr_phil',
    'dr_paed',
    'dr_rer_nat',
    'dr_rer_pol',
    'dr_ing'
];

export const TitleLabels: LabelObject<Title> = {
    'not_specified': 'Keine Angabe',
    'dr_med': 'Dr. med.',
    'dr_med_dent': 'Dr. med. dent.',
    'dr_med_vent': 'Dr. med. vet.',
    'dr_phil': 'Dr. phil',
    'dr_paed': 'Dr. paed.',
    'dr_rer_nat': 'Dr. rer. nat.',
    'dr_rer_pol': 'Dr. rer. pol.',
    'dr_ing': 'Dr. ing.'
}

export type EmergencyTime = {
    id: string;
    startDate: Date;
    endDate: Date;
    fromTime: Date;
    toTime: Date;
    days: Day[]
};

export type EmergencyTimeTemplate = {
    startDate: string;
    endDate: string;
    fromTime: string;
    toTime: string;
    days: DaySelectionInformation
}

export function createDefaultEmergencyTimeTemplate(): EmergencyTimeTemplate {

    const now = new Date();

    const offsetNextMonday = 8 - now.getDay();
    let fromDate = new Date(now.getTime() + 3600000 * 24 * offsetNextMonday);

    const offsetNextFriday = offsetNextMonday + 4;
    let toDate = new Date(now.getTime() + 3600000 * 24 * offsetNextFriday);

    let fromTime = new Date(now);
    fromTime.setMinutes(0);
    fromTime.setSeconds(0);
    fromTime.setMilliseconds(0);

    fromTime = new Date(fromTime.getTime() + 3600000 * 1); // add one hour

    let toTime = new Date(now);
    toTime.setMinutes(0);
    toTime.setSeconds(0);
    toTime.setMilliseconds(0);

    toTime = new Date(toTime.getTime() + 3600000 * 2);

    return {
        startDate: formatDate(fromDate),
        endDate: formatDate(toDate),
        fromTime: formatTime(fromTime),
        toTime: formatTime(toTime),
        days: {
            Mon: false,
            Tue: false,
            Wed: false,
            Thu: false,
            Fri: false,
            Sat: false,
            Sun: false
        }
    };

}

export function convertEmergencyTimeRequestToEmergencyTime(request: EmergencyTimeRequest): EmergencyTime {
    return {
        id: uuidv4(),
        startDate: convertDateStringToDateObject(request.startDate),
        endDate: convertDateStringToDateObject(request.endDate),
        fromTime: convertTimeStringToDateObject(request.fromTime),
        toTime: convertTimeStringToDateObject(request.toTime),
        days: request.days.map(dayString => dayString as Day)
    }
}

function formatDate(date: Date): string {
    return `${date.getFullYear()}-${String(date.getMonth()).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function formatTime(time: Date): string {
    return `${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}`
}

export function compareTime(time1: string, time2: string): number {

    const spit1 = time1.split(":");
    const hour1 = Number(spit1[0]);
    const minute1 = Number(spit1[1]);

    const spit2 = time2.split(":");
    const hour2 = Number(spit2[0]);
    const minute2 = Number(spit2[1]);

    if (hour1 < hour2) {
        return -1;
    } else if (hour1 > hour2) {
        return 1;
    } else {
        if (minute1 < minute2) {
            return -1;
        } else if (minute1 > minute2) {
            return 1;
        }
    }

    return 0;

}

export function createEmergencyTimeFromTemplate(template: EmergencyTimeTemplate): EmergencyTime {

    return {
        id: uuidv4(),
        startDate: new Date(template.startDate),
        endDate: new Date(template.endDate),
        fromTime: convertTimeStringToDateObject(template.fromTime),
        toTime: convertTimeStringToDateObject(template.toTime),
        days: convertDaySelectionMapToArray(template.days)
    }
}

export function convertDaySelectionMapToArray(selection: DaySelectionInformation): Day[] {

    let days: Day[] = []

    for (const key of Object.keys(selection)) {

        const day: Day = key as Day;
        if (selection[day]) {
            days.push(day);
        }

    }

    return days;

}

export function convertArrayToDaySelectionMap(days: string[]): DaySelectionInformation {

    let selection: DaySelectionInformation = {
        Mon: false,
        Tue: false,
        Wed: false,
        Thu: false,
        Fri: false,
        Sat: false,
        Sun: false
    }

    for (const dayString of days) {
        const day = dayString as Day;
        selection[day] = true;
    }

    return selection;

}

export function convertTreatmentStateToArray(state: TreatmentState): string[] {

    let treatments: string[] = []

    for (const treatment of Object.keys(state)) {

        if (state[treatment]) {
            treatments.push(treatment);
        }

    }

    return treatments;

}

export function convertArrayToTreatmentState(array: string[]): TreatmentState {

    const state: TreatmentState = {}

    for (const treatment of array) {
        state[treatment] = true;
    }

    return state;

}

function convertTimeStringToDateObject(time: string): Date {

    const split = time.split(":");
    const hours = split[0];
    const minutes = split[1];

    const date = new Date(0);
    date.setHours(Number(hours)),
        date.setMinutes(Number(minutes));

    return date;

}

function convertDateStringToDateObject(time: string): Date {

    const split = time.split(".");
    const days = Number(split[0]);
    const month = Number(split[1]);
    const year = Number(split[2]);

    const date = new Date(0);
    date.setFullYear(year, month - 1, days);

    return date;

}