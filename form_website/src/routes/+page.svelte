<script lang="ts">
	import { goto } from '$app/navigation';

	function redirectForm() {
		goto('/form');
	}
</script>

<div class="h-full flex flex-col items-center justify-center">
	<div class="hero bg-base-100">
		<div class="hero-content">
			<div class="max-w-xl flex flex-col justify-center items-center">
				<h1 class="mb-2 text-5xl font-bold text-center">Hallo!</h1>
				<h1 class="text-2xl text-center">
					VetFinder ist ein Projekt zur Anzeige von den aktuell geöffneten Tiernotdiensten
				</h1>
				<div class="mt-4 stats stats-vertical lg:stats-horizontal shadow bg-primary">
					<div class="stat">
						<div class="stat-title">Tierärzte insgesamt</div>
						<div class="stat-value">1.433</div>
						<div class="stat-desc">seit November 2022</div>
					</div>

					<div class="stat">
						<div class="stat-title">Neue Tierärzte</div>
						<div class="stat-value">265</div>
					</div>

					<div class="stat">
						<div class="stat-title">Nutzer monatlich</div>
						<div class="stat-value">20.569</div>
						<div class="stat-desc">↗︎ 1.112 (5%)</div>
					</div>
				</div>
				<h1 class="mt-10 text-xl text-center">
					Du bist ein Tierarzt? Dann <button class="btn btn-primary btn-sm" on:click={redirectForm}
						>klicke hier</button
					>
				</h1>
			</div>
		</div>
	</div>
</div>
