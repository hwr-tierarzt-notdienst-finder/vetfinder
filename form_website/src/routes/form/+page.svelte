<script lang="ts">
	import { onMount } from 'svelte';
	import { fetchPostFormData } from '../../api';
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
		type FormDataRequest,
		type TreatmentState,
		Treatments,
		TreatmentLabels,
		treatmentStateToArray,
		type EmergencyTimeRequest,
		convertEmergencyTimeToRequest,
		type FormOfAddress,
		FormOfAddressLabels,
		type Title,
		TitleLabels
	} from '../../types';

	import { page } from '$app/stores';
	import Input from '../../components/Input.svelte';

	let vetToken: string | null = null;

	onMount(() => {
		vetToken = $page.url.searchParams.get('vetToken');
	});

	let clinicName: string = '';
	let email: string = '';
	let telephone: string = '';

	let selectedFormOfAddress: FormOfAddress = 'not_specified';
	let selectedTitle: Title = 'not_specified';
	let firstName: string = '';
	let lastName: string = '';

	let street: string = '';
	let houseNumber: string = '';
	let city: string = '';
	let postCode: string = '';

	let selectedTreatments: TreatmentState = {
		dog: false,
		cat: false,
		horse: false,
		small_animals: false,
		other: false
	};

	let otherTreatmentInformation: string = '';
	let treatmentNote: string = '';

	const openingHoursFrom: OpeningHours = {
		monday: undefined,
		tuesday: undefined,
		wednesday: undefined,
		thursday: undefined,
		friday: undefined,
		saturday: undefined,
		sunday: undefined
	};
	const openingHoursTo: OpeningHours = {
		monday: undefined,
		tuesday: undefined,
		wednesday: undefined,
		thursday: undefined,
		friday: undefined,
		saturday: undefined,
		sunday: undefined
	};
	const dayClosed: DaySelectionInformation = {
		monday: true,
		tuesday: true,
		wednesday: true,
		thursday: true,
		friday: true,
		saturday: true,
		sunday: true
	};

	function getOpeningHoursOfDay(day: Day): OpeningHoursInformation | undefined {
		if (openingHoursFrom[day] == undefined || openingHoursTo[day] == undefined) {
			return undefined;
		}

		return {
			from: openingHoursFrom[day]!,
			to: openingHoursTo[day]!
		};
	}

	function getOpeningHoursOverview(): OpeningHoursOverview {
		let overview: OpeningHoursOverview = {
			monday: undefined,
			tuesday: undefined,
			wednesday: undefined,
			thursday: undefined,
			friday: undefined,
			saturday: undefined,
			sunday: undefined
		};

		for (const day of Days) {
			overview[day] = getOpeningHoursOfDay(day);
		}

		return overview;
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
		emergencyTimes.push(emergencyTime);
		emergencyTimes = emergencyTimes;
		newEmergencyTimeTemplate = createDefaultEmergencyTimeTemplate();
	}

	function sendFormData() {
		const treatments = treatmentStateToArray(selectedTreatments);
		const emergencyTimeRequests: EmergencyTimeRequest[] = emergencyTimes.map((emergencyTime) =>
			convertEmergencyTimeToRequest(emergencyTime)
		);

		const request: FormDataRequest = {
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
				postCode: postCode
			},
			treatments: {
				treatments: treatments,
				other: otherTreatmentInformation,
				note: treatmentNote
			},
			openingHours: getOpeningHoursOverview(),
			emergencyTimes: emergencyTimeRequests
		};

		fetchPostFormData(request);
	}
</script>

<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
<!-- svelte-ignore a11y-label-has-associated-control -->
<!-- svelte-ignore a11y-missing-attribute -->
<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="mt-10 flex min-w-full justify-center">
	<div class="flex flex-col gap-10 justify-center items-center">
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
		<!-- Contact -->
		<div class="section">
			<h1 class="text-2xl font-bold">Kontaktdaten</h1>
			<div class="flex gap-4">
				<Input label="Klinikname" bind:value={clinicName} type="text" placeholder="Hier eingeben" />
				<Input label="E-Mail" bind:value={email} type="email" placeholder="Hier eingeben" />
				<Input
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
				<Input label="Vorname" bind:value={firstName} type="text" placeholder="Hier eingeben" />
				<Input label="Nachname" bind:value={lastName} type="text" placeholder="Hier eingeben" />
			</div>
		</div>
		<div class="divider" />
		<!-- Adress -->
		<div class="section">
			<h1 class="text-2xl font-bold">Adresse</h1>
			<div class="flex gap-4">
				<Input label="Straße" bind:value={street} type="text" placeholder="Hier eingeben" />
				<Input
					label="Hausnummer"
					bind:value={houseNumber}
					type="text"
					placeholder="Hier eingeben"
				/>
				<Input label="Stadt" bind:value={city} type="text" placeholder="Hier eingeben" />
				<Input label="Postleitzahl" bind:value={postCode} type="text" placeholder="Hier eingeben" />
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
						{#each Treatments as treatment}
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
					{#if selectedTreatments['other']}
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
		<button class="btn btn-primary btn-lg" on:click={sendFormData}>Eintragen</button>
	</div>
</div>

<style>
	.section {
		@apply w-3/4 flex flex-col gap-4 justify-center items-center;
	}
</style>
