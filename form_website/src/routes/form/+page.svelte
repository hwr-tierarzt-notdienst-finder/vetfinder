<script lang="ts">
	type CategoryState = {
		[index in Category]: boolean;
	};
	let selectedCategories: CategoryState = {
		dog: false,
		cat: false,
		horse: false,
		small_animals: false,
		other: false
	};

	type Category = 'dog' | 'cat' | 'horse' | 'small_animals' | 'other';
	const categories: Category[] = ['dog', 'cat', 'horse', 'small_animals', 'other'];

	type CategoryLabel = {
		[index in Category]: string;
	};
	const categoryLabels: CategoryLabel = {
		dog: 'Hund',
		cat: 'Katze',
		horse: 'Pferd',
		small_animals: 'Kleintiere',
		other: 'Sonstige'
	};

	let selectedFormOfAddress: string = '';
	const formOfAddresses: string[] = ['Herr', 'Frau'];

	let selectedTitle: string = '';
	const titles: string[] = [
		'Kein Titel',
		'Dr. med.',
		'Dr. med. dent.',
		'Dr. med. vet.',
		'Dr. phil',
		'Dr. paed.',
		'Dr. rer. nat.',
		'Dr. rer. pol.',
		'Dr. ing.'
	];

	type Day = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';
	const days: Day[] = [
		'monday',
		'tuesday',
		'wednesday',
		'thursday',
		'friday',
		'saturday',
		'sunday'
	];

	type DayLabel = {
		[index in Day]: string;
	};
	const dayLabels: DayLabel = {
		monday: 'Montag',
		tuesday: 'Dienstag',
		wednesday: 'Mittwoch',
		thursday: 'Donnerstag',
		friday: 'Freitag',
		saturday: 'Samstag',
		sunday: 'Sonntag'
	};

	type OpeningHoursInformation = {
		from: string | undefined;
		to: string | undefined;
	};

	type OpeningHoursOverview = {
		[index in Day]:
			| {
					from: string | undefined;
					to: string | undefined;
			  }
			| undefined;
	};

	type OpeningHours = {
		[index in Day]: string | undefined;
	};
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

	function getOpeningHoursOfDay(day: Day): OpeningHoursInformation {
		return {
			from: openingHoursFrom[day],
			to: openingHoursTo[day]
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

		for (const day of days) {
			overview[day] = getOpeningHoursOfDay(day);
		}

		return overview;
	}

	$: {
		if (openingHoursFrom || openingHoursTo) {
			console.log(getOpeningHoursOverview());
		}
	}
</script>

<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
<!-- svelte-ignore a11y-label-has-associated-control -->
<!-- svelte-ignore a11y-missing-attribute -->
<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="flex min-w-full justify-center">
	<div class="flex flex-col gap-10 justify-center items-center">
		<div class="w-full flex flex-col gap-2">
			<h1 class="text-2xl font-bold">Kontaktdaten</h1>
			<div class="flex gap-4">
				<div class="form-control w-full max-w-xs">
					<label class="label">
						<span class="label-text label-">E-Mail</span>
					</label>
					<input
						type="email"
						placeholder="Hier eingeben"
						class="input input-bordered w-full max-w-xs"
					/>
				</div>
				<div class="form-control w-full max-w-xs">
					<label class="label">
						<span class="label-text">Telefonnummer</span>
					</label>
					<input
						type="tel"
						placeholder="Hier eingeben"
						class="input input-bordered w-full max-w-xs"
					/>
				</div>
			</div>
		</div>
		<div class="divider" />
		<div class="w-full flex flex-col gap-2">
			<h1 class="text-2xl font-bold">Vollständiger Name</h1>
			<div class="flex gap-4">
				<div class="form-control w-full max-w-xs">
					<label class="label">
						<span class="label-text">Titel</span>
					</label>
					<div class="flex">
						<div class="dropdown dropdown-bottom">
							<label tabindex="0" class="btn m-1"
								>{selectedFormOfAddress ? selectedFormOfAddress : 'Hier eingeben'}</label
							>
							<ul
								tabindex="0"
								class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52"
							>
								{#each formOfAddresses as formOfAddress}
									<li>
										<a on:click={() => (selectedFormOfAddress = formOfAddress)}>{formOfAddress}</a>
									</li>
								{/each}
							</ul>
						</div>
						<div class="dropdown dropdown-bottom">
							<label tabindex="0" class="btn m-1"
								>{selectedTitle ? selectedTitle : 'Hier eingeben'}</label
							>
							<ul
								tabindex="0"
								class="dropdown-content  menu p-2 shadow bg-base-100 rounded-box w-52"
							>
								{#each titles as title}
									<li>
										<a on:click={() => (selectedTitle = title)}>{title}</a>
									</li>
								{/each}
							</ul>
						</div>
					</div>
				</div>
				<div class="form-control w-full max-w-xs">
					<label class="label">
						<span class="label-text">Dein Vorname</span>
					</label>
					<input
						type="text"
						placeholder="Hier eingeben"
						class="input input-bordered w-full max-w-xs"
					/>
				</div>
				<div class="form-control w-full max-w-xs">
					<label class="label">
						<span class="label-text">Dein Nachname</span>
					</label>
					<input
						type="text"
						placeholder="Hier eingeben"
						class="input input-bordered w-full max-w-xs"
					/>
				</div>
			</div>
		</div>
		<div class="divider" />
		<div class="w-full flex flex-col gap-2">
			<h1 class="text-2xl font-bold">Adresse</h1>
			<div class="flex gap-4">
				<div class="form-control w-full max-w-xs">
					<label class="label">
						<span class="label-text">Straße</span>
					</label>
					<input
						type="text"
						placeholder="Hier eingeben"
						class="input input-bordered w-full max-w-xs"
					/>
				</div>
				<div class="form-control w-full max-w-xs">
					<label class="label">
						<span class="label-text">Hausnummer</span>
					</label>
					<input
						type="text"
						placeholder="Hier eingeben"
						class="input input-bordered w-full max-w-xs"
					/>
				</div>
				<div class="form-control w-full max-w-xs">
					<label class="label">
						<span class="label-text">Postleitzahl</span>
					</label>
					<input
						type="text"
						placeholder="Hier eingeben"
						class="input input-bordered w-full max-w-xs"
					/>
				</div>
			</div>
		</div>
		<div class="divider" />
		<div class="w-full flex flex-col gap-2">
			<h1 class="text-2xl font-bold">Behandlungen</h1>
			<div class="flex gap-4">
				<div class="form-control flex-col w-full max-w-xs">
					<label class="label">
						<span class="label-text">Tierarten</span>
					</label>
					<div class="form-control flex-row flex-wrap gap-4">
						{#each categories as category}
							<label class="label justify-start gap-2 cursor-pointer">
								<input
									type="checkbox"
									bind:checked={selectedCategories[category]}
									class="checkbox"
								/>
								<span class="label-text">{categoryLabels[category]}</span>
							</label>
						{/each}
					</div>
					{#if selectedCategories['other']}
						<div class="mt-2 form-control w-full">
							<input
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
							type="text"
							placeholder="Anmerkungen..."
							class="input input-bordered w-full max-w-xs"
						/>
					</div>
				</div>
			</div>
		</div>
		<div class="divider" />
		<div class="w-full flex flex-col gap-2">
			<h1 class="text-2xl font-bold">Öffnungszeiten</h1>
			{#each days as day}
				<div class="flex gap-4">
					<div class="form-control w-full max-w-xs">
						<label class="label">
							<span class="label-text">{dayLabels[day]}</span>
						</label>
						<div class="flex gap-2 justify-center items-center">
							<label class="label">
								<span class="label-text">von</span>
							</label>
							<input
								bind:value={openingHoursFrom[day]}
								type="time"
								class="input input-bordered w-full max-w-xs"
							/>
							<label class="label">
								<span class="label-text">bis</span>
							</label>
							<input
								bind:value={openingHoursTo[day]}
								type="time"
								class="input input-bordered w-full max-w-xs"
							/>
						</div>
					</div>
				</div>
			{/each}
		</div>
		<button class="btn btn-primary btn-lg">Eintragen</button>
	</div>
</div>
