<script lang="ts">
	import { onMount } from 'svelte';
	import { createOrOverwriteVet, getTreatments, getVetWithToken } from '../../api';
	import {
		type DaySelectionInformation,
		type EmergencyTime,
		type Day,
		type OpeningHours,
		type OpeningHoursInformation,
		type OpeningHoursOverview,
		Days,
		DayLabels,
		FormOfAddresses,
		Titles,
		type EmergencyTimeTemplate,
		createDefaultEmergencyTimeTemplate,
		createEmergencyTimeFromTemplate,
		type Vet,
		type TreatmentState,
		TreatmentLabels,
		type EmergencyTimeRequest,
		convertEmergencyTimeToRequest,
		type FormOfAddress,
		FormOfAddressLabels,
		type Title,
		TitleLabels,
		compareTime,
		convertTreatmentStateToArray,
		convertArrayToTreatmentState,
		convertEmergencyTimeRequestToEmergencyTime
	} from '../../types';

	import { page } from '$app/stores';
	import Input from '../../components/Input.svelte';
	import { goto } from '$app/navigation';

	let loading: boolean = true;
	let vetToken: string | null = null;

	let availableTreatments: string[] = [];

	let clinicName: string = '';
	let email: string = '';
	let telephone: string = '';

	onMount(() => {
		email = $page.url.searchParams.get('email') || '';
		vetToken = $page.url.searchParams.get('access-token');

		(async () => {
			if (vetToken) {
				const vet = await getVetWithToken(vetToken);

				if (vet === null) {
					goto('/');
				} else {
					console.log(vet);
					// TODO: mapping

					clinicName = vet.contact.clinicName;
					email = vet.contact.email;
					telephone = vet.contact.telephone;

					selectedFormOfAddress = vet.name.formOfAddress || 'not_specified';
					selectedTitle = vet.name.title || 'not_specified';
					firstName = vet.name.firstName;
					lastName = vet.name.lastName;

					street = vet.address.street;
					houseNumber = vet.address.number;
					city = vet.address.city;
					zipCode = vet.address.zipCode;

					selectedTreatments = convertArrayToTreatmentState(vet.treatments.treatments);
					otherTreatmentInformation = '';
					treatmentNote = '';

					for (const day of Days) {
						if (vet.openingHours[day] === undefined) {
							dayClosed[day] = true;
						} else {
							openingHoursFrom[day] = vet.openingHours[day]!.from;
							openingHoursTo[day] = vet.openingHours[day]!.to;
							dayClosed[day] = false;
						}
					}

					if (vet.emergencyTimes) {
						emergencyTimes = vet.emergencyTimes.map((request) =>
							convertEmergencyTimeRequestToEmergencyTime(request)
						);
					} else {
						emergencyTimes = [];
					}
				}
			}

			availableTreatments = await getTreatments();

			for (const treatment of availableTreatments) {
				selectedTreatments[treatment] = false;
			}

			loading = false;
		})();
	});

	let selectedFormOfAddress: FormOfAddress = 'not_specified';
	let selectedTitle: Title = 'not_specified';
	let firstName: string = '';
	let lastName: string = '';

	let street: string = '';
	let houseNumber: string = '';
	let city: string = '';
	let zipCode: string = '';

	let selectedTreatments: TreatmentState = {};

	let otherTreatmentInformation: string = ''; // currently not supported by the backend
	let treatmentNote: string = ''; // currently not supported by the backend

	let openingHoursFrom: OpeningHours = {
		Mon: undefined,
		Tue: undefined,
		Wed: undefined,
		Thu: undefined,
		Fri: undefined,
		Sat: undefined,
		Sun: undefined
	};
	let openingHoursTo: OpeningHours = {
		Mon: undefined,
		Tue: undefined,
		Wed: undefined,
		Thu: undefined,
		Fri: undefined,
		Sat: undefined,
		Sun: undefined
	};
	let dayClosed: DaySelectionInformation = {
		Mon: true,
		Tue: true,
		Wed: true,
		Thu: true,
		Fri: true,
		Sat: true,
		Sun: true
	};

	function getOpeningHoursOfDay(day: Day): OpeningHoursInformation | undefined {
		if (openingHoursFrom[day] === undefined || openingHoursTo[day] === undefined) {
			return undefined;
		}

		return {
			from: openingHoursFrom[day]!,
			to: openingHoursTo[day]!
		};
	}

	function getOpeningHoursOverview(): OpeningHoursOverview {
		let overview: OpeningHoursOverview = {
			Mon: undefined,
			Tue: undefined,
			Wed: undefined,
			Thu: undefined,
			Fri: undefined,
			Sat: undefined,
			Sun: undefined
		};

		for (const day of Days) {
			overview[day] = getOpeningHoursOfDay(day);
		}

		return overview;
	}

	function checkInputError(): string | null {
		if (clinicName.length === 0) {
			return 'Klinikname fehlt!';
		} else if (email.length === 0) {
			return 'E-Mail fehlt!';
		} else if (telephone.length === 0) {
			return 'Telefonnummer fehlt!';
		} else if (firstName.length === 0) {
			return 'Vorname fehlt!';
		} else if (lastName.length === 0) {
			return 'Nachname fehlt!';
		} else if (street.length === 0) {
			return 'Straße fehlt!';
		} else if (houseNumber.length === 0) {
			return 'Hausnummer fehlt!';
		} else if (city.length === 0) {
			return 'Stadt fehlt!';
		} else if (zipCode.length === 0) {
			return 'Postleitzahl fehlt!';
		}

		return null;
	}

	function checkTreatmentsError(treatments: string[]): string | null {
		if (treatments.length === 0) {
			return 'Wählen Sie bitte mindestens eine Tierart, die Sie behandeln, aus!';
		} else if (treatments.indexOf('misc') !== -1 && otherTreatmentInformation.length === 0) {
			return 'Spezifizieren Sie "Sonstige" bei Ihren Behandlungen!';
		}
		return null;
	}

	function checkOpeningHourError(): string | null {
		for (const day of Days) {
			if (dayClosed[day]) continue;

			if (openingHoursFrom[day] === undefined && openingHoursTo[day] === undefined) {
				return `Öffnungszeiten am ${DayLabels[day]} fehlen!`;
			} else if (openingHoursFrom[day] === undefined && openingHoursTo[day] !== undefined) {
				return `Öffnungszeit am ${DayLabels[day]} fehlt!`;
			} else if (openingHoursFrom[day] !== undefined && openingHoursTo[day] === undefined) {
				return `Schließzeit am ${DayLabels[day]} fehlt!`;
			} else if (openingHoursFrom[day] !== undefined && openingHoursTo[day] !== undefined) {
				const compare = compareTime(openingHoursFrom[day]!, openingHoursTo[day]!);
				if (compare === 1) {
					return `Die Öffnungszeit am ${DayLabels[day]} muss vor der Schließzeit liegen!`;
				} else if (compare === 0) {
					return `Die Öffnungszeit und Schließzeit am ${DayLabels[day]} müssen sich unterscheiden!`;
				}
			}
		}

		return null;
	}

	let newEmergencyTimeTemplate: EmergencyTimeTemplate = createDefaultEmergencyTimeTemplate();

	let emergencyTimes: EmergencyTime[] = [];

	function deleteEmergencyTime(id: string) {
		emergencyTimes = emergencyTimes.filter((time) => {
			return time.id !== id;
		});
	}

	function addEmergencyTime() {
		const emergencyTime = createEmergencyTimeFromTemplate(newEmergencyTimeTemplate);

		if (emergencyTime.days.length === 0) {
			showError('Wähle Sie bitte mindestens einen Wochentag aus!');
			return;
		}

		if (emergencyTime.startDate.getTime() > emergencyTime.endDate.getTime()) {
			showError('Das Startdatum muss vor der Enddatum liegen!');
			return;
		}

		if (emergencyTime.fromTime.getTime() > emergencyTime.toTime.getTime()) {
			showError('Die Startöffnungszeit muss vor der Endöffnungszeit liegen!');
			return;
		}

		emergencyTimes.push(emergencyTime);
		emergencyTimes = emergencyTimes;
		newEmergencyTimeTemplate = createDefaultEmergencyTimeTemplate();
	}

	function sendVet() {
		const inputErrors = checkInputError();

		if (inputErrors !== null) {
			showError(inputErrors);
			return;
		}

		const treatments = convertTreatmentStateToArray(selectedTreatments);
		const treatmentsError = checkTreatmentsError(treatments);

		if (treatmentsError !== null) {
			showError(treatmentsError);
			return;
		}

		const openingHoursError = checkOpeningHourError();

		if (openingHoursError !== null) {
			showError(openingHoursError);
			return;
		}

		const emergencyTimeRequests: EmergencyTimeRequest[] = emergencyTimes.map((emergencyTime) =>
			convertEmergencyTimeToRequest(emergencyTime)
		);

		const vet: Vet = {
			contact: {
				clinicName: clinicName,
				email: email,
				telephone: telephone
			},
			name: {
				formOfAddress:
					selectedFormOfAddress === 'not_specified' ? undefined : selectedFormOfAddress,
				title: selectedTitle === 'not_specified' ? undefined : selectedTitle,
				firstName: firstName,
				lastName: lastName
			},
			address: {
				street: street,
				number: houseNumber,
				city: city,
				zipCode: zipCode
			},
			treatments: {
				treatments: treatments,
				other: otherTreatmentInformation,
				note: treatmentNote
			},
			openingHours: getOpeningHoursOverview(),
			emergencyTimes: emergencyTimeRequests,
			timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
		};

		console.log(vet);

		createOrOverwriteVet(vet);
	}

	let timer: NodeJS.Timer | null = null;
	let error: string = '';
	const ErrorTime: number = 5000;

	function showError(message: string) {
		if (timer !== null) {
			clearTimeout(timer);
		}

		error = message;
		timer = setTimeout(() => {
			error = '';
		}, ErrorTime);
	}
</script>

{#if error}
	<div class="alert alert-error shadow-lg w-1/2 fixed top-5 right-5">
		<div>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="stroke-current flex-shrink-0 h-6 w-6"
				fill="none"
				viewBox="0 0 24 24"
				><path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
				/></svg
			>
			<span>{error}</span>
		</div>
	</div>
{/if}

<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
<!-- svelte-ignore a11y-label-has-associated-control -->
<!-- svelte-ignore a11y-missing-attribute -->
<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="mt-10 flex min-w-full justify-center">
	<div class="flex flex-col gap-10 justify-center items-center">
		{#if !loading}
			<div class="p-4 rounded-xl flex flex-col gap-2 justify-center items-center bg-base-200">
				{#if vetToken}
					<h1 class="text-2xl font-bold">Willkommen zurück!</h1>
					<p class="text-xl">Hier kannst du deine Daten abändern.</p>
				{:else}
					<h1 class="text-2xl font-bold">Hallo!</h1>
					<p class="text-xl">Vielen Dank, dass Sie sich in unserem System eintragen wollen.</p>
					<p class="text-xl">Der Schutz Ihrer Daten ist uns sehr wichtig.</p>
					<p class="text-xl">Wir gehen verantwortungsvoll mit Ihren Daten um.</p>
					<p class="text-xl">Unter anderem werden Ihre Daten verschlüsselt an uns gesendet.</p>
				{/if}
			</div>
		{/if}
		<!-- Contact -->
		<div class="section">
			<h1 class="text-2xl font-bold">Kontaktdaten</h1>
			<div class="flex gap-4">
				<Input
					required
					label="Klinikname"
					bind:value={clinicName}
					type="text"
					placeholder="Hier eingeben"
				/>
				<Input
					required
					label="E-Mail"
					bind:value={email}
					type="email"
					placeholder="Hier eingeben"
				/>
				<Input
					required
					label="Telefonnummer"
					bind:value={telephone}
					type="tel"
					placeholder="Hier eingeben"
				/>
			</div>
		</div>
		<div class="divider" />
		<!-- Name -->
		<div class="section">
			<h1 class="text-2xl font-bold">Vollständiger Name</h1>
			<div class="flex gap-4">
				<div class="form-control max-w-xs">
					<label class="label">
						<span class="label-text">Anrede</span>
					</label>
					<div class="flex">
						<div class="dropdown dropdown-bottom">
							<label tabindex="0" class="btn m-1"
								>{selectedFormOfAddress
									? FormOfAddressLabels[selectedFormOfAddress]
									: 'Hier eingeben'}</label
							>
							<ul
								tabindex="0"
								class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52"
							>
								{#each FormOfAddresses as formOfAddress}
									<li>
										<a on:click={() => (selectedFormOfAddress = formOfAddress)}
											>{FormOfAddressLabels[formOfAddress]}</a
										>
									</li>
								{/each}
							</ul>
						</div>
					</div>
				</div>
				<div class="form-control max-w-xs">
					<label class="label">
						<span class="label-text">Titel</span>
					</label>
					<div class="flex">
						<div class="dropdown dropdown-bottom">
							<label tabindex="0" class="btn m-1"
								>{selectedTitle ? TitleLabels[selectedTitle] : 'Hier eingeben'}</label
							>
							<ul
								tabindex="0"
								class="dropdown-content  menu p-2 shadow bg-base-100 rounded-box w-52"
							>
								{#each Titles as title}
									<li>
										<a on:click={() => (selectedTitle = title)}>{TitleLabels[title]}</a>
									</li>
								{/each}
							</ul>
						</div>
					</div>
				</div>
				<Input
					required
					label="Vorname"
					bind:value={firstName}
					type="text"
					placeholder="Hier eingeben"
				/>
				<Input
					required
					label="Nachname"
					bind:value={lastName}
					type="text"
					placeholder="Hier eingeben"
				/>
			</div>
		</div>
		<div class="divider" />
		<!-- Adress -->
		<div class="section">
			<h1 class="text-2xl font-bold">Adresse</h1>
			<div class="flex gap-4">
				<Input
					required
					label="Straße"
					bind:value={street}
					type="text"
					placeholder="Hier eingeben"
				/>
				<Input
					required
					label="Hausnummer"
					bind:value={houseNumber}
					type="text"
					placeholder="Hier eingeben"
				/>
				<Input required label="Stadt" bind:value={city} type="text" placeholder="Hier eingeben" />
				<Input
					required
					label="Postleitzahl"
					bind:value={zipCode}
					type="text"
					placeholder="Hier eingeben"
				/>
			</div>
		</div>
		<div class="divider" />
		<!-- Treatments -->
		<div class="section">
			<h1 class="text-2xl font-bold">Behandlungen</h1>
			<div class="flex gap-4">
				<div class="form-control flex-col w-full max-w-xs">
					<label class="label">
						<span class="label-text">Tierarten</span>
					</label>
					<div class="form-control flex-row flex-wrap gap-4">
						{#each availableTreatments as treatment}
							<label class="label justify-start gap-2 cursor-pointer">
								<input
									type="checkbox"
									bind:checked={selectedTreatments[treatment]}
									class="checkbox"
								/>
								<span class="label-text">{TreatmentLabels[treatment]}</span>
							</label>
						{/each}
					</div>
					{#if selectedTreatments['misc']}
						<div class="mt-2 form-control w-full">
							<input
								bind:value={otherTreatmentInformation}
								type="text"
								placeholder="Hier eingeben"
								class="input input-bordered w-full max-w-xs"
							/>
						</div>
					{/if}
				</div>
				<div class="form-control flex-col w-full max-w-xs">
					<label class="label">
						<span class="label-text">Anmerkungen</span>
					</label>
					<div class="mt-2 form-control w-full">
						<input
							bind:value={treatmentNote}
							type="text"
							placeholder="Anmerkungen..."
							class="input input-bordered w-full max-w-xs"
						/>
					</div>
				</div>
			</div>
		</div>
		<div class="divider" />
		<!-- Opening Hours -->
		<div class="section">
			<h1 class="text-2xl font-bold">Öffnungszeiten</h1>
			<div class="w-full flex flex-col gap-4">
				{#each Days as day}
					<div class="form-control">
						<label class="label">
							<span class="label-text">{DayLabels[day]}</span>
						</label>
						<div class="flex gap-2">
							<label class="label">
								<span class="label-text">von</span>
							</label>
							<input
								disabled={dayClosed[day]}
								bind:value={openingHoursFrom[day]}
								type="time"
								class="input input-bordered w-full max-w-xs"
							/>
							<label class="label">
								<span class="label-text">bis</span>
							</label>
							<input
								disabled={dayClosed[day]}
								bind:value={openingHoursTo[day]}
								type="time"
								class="input input-bordered w-full max-w-xs"
							/>
							<label class="label justify-start gap-2 cursor-pointer">
								<input
									type="checkbox"
									bind:checked={dayClosed[day]}
									class="checkbox"
									on:input={() => {
										openingHoursFrom[day] = undefined;
										openingHoursTo[day] = undefined;
									}}
								/>
								<span class="label-text">geschlossen</span>
							</label>
						</div>
					</div>
				{/each}
			</div>
		</div>
		<div class="divider" />
		<!-- Emergency Times -->
		<div class="w-full flex flex-col gap-2">
			<h1 class="text-2xl font-bold">Notfallzeiten</h1>
			<div class="overflow-x-auto overflow-y-auto">
				<table class="table table-zebra w-full">
					<thead>
						<tr>
							<th />
							<th>Startdatum</th>
							<th>Enddatum</th>
							<th>Wochentage</th>
							<th>Öffnungszeit (Start)</th>
							<th>Öffnungszeit (Ende)</th>
							<th />
						</tr>
					</thead>
					<tbody>
						{#each emergencyTimes as emergencyTime, index}
							<tr>
								<th>{index + 1}</th>
								<td
									>{emergencyTime.startDate.toLocaleDateString(undefined, {
										dateStyle: 'medium'
									})}</td
								>
								<td
									>{emergencyTime.endDate.toLocaleDateString(undefined, {
										dateStyle: 'medium'
									})}</td
								>
								<td>{emergencyTime.days.map((day) => DayLabels[day]).join(', ')}</td>
								<td
									>{emergencyTime.fromTime.toLocaleTimeString(undefined, {
										timeStyle: 'short'
									})}</td
								>
								<td
									>{emergencyTime.toTime.toLocaleTimeString(undefined, {
										timeStyle: 'short'
									})}</td
								>
								<td>
									<button
										class="btn btn-ghost"
										on:click={() => deleteEmergencyTime(emergencyTime.id)}>Löschen</button
									>
								</td>
							</tr>
						{/each}
						<tr>
							<th>{emergencyTimes.length + 1}</th>
							<td>
								<input
									bind:value={newEmergencyTimeTemplate.startDate}
									type="date"
									class="input input-bordered w-full max-w-xs"
								/>
							</td>
							<td>
								<input
									bind:value={newEmergencyTimeTemplate.endDate}
									type="date"
									class="input input-bordered w-full max-w-xs"
								/>
							</td>
							<td>
								<div class="flex flex-wrap max-w-xs">
									{#each Days as day}
										<label class="label justify-start gap-2 cursor-pointer">
											<input
												type="checkbox"
												bind:checked={newEmergencyTimeTemplate.days[day]}
												class="checkbox"
											/>
											<span class="label-text">{DayLabels[day]}</span>
										</label>
									{/each}
								</div>
							</td>
							<td>
								<input
									bind:value={newEmergencyTimeTemplate.fromTime}
									type="time"
									class="input input-bordered w-full max-w-xs"
								/>
							</td>
							<td>
								<input
									bind:value={newEmergencyTimeTemplate.toTime}
									type="time"
									class="input input-bordered w-full max-w-xs"
								/>
							</td>
							<td>
								<button class="btn btn-ghost" on:click={() => addEmergencyTime()}>Hinzufügen</button
								>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
		<button class="btn btn-primary btn-lg" on:click={sendVet}
			>{vetToken ? 'Aktualisieren' : 'Eintragen'}</button
		>
	</div>
</div>

<style>
	.section {
		@apply w-3/4 flex flex-col gap-4 justify-center items-center;
	}
</style>
