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
				<div class="my-5 flex flex-col gap-2">
					<p class="text-2xl text-center">
						VetFinder ist ein Projekt zur Anzeige von Tierärzten in deiner Nähe.
					</p>
					<p class="text-2xl text-center">
						Die Idee ist denkbar <span class="font-bold">einfach</span>: Tierärzte tragen sich bei
						uns ein, werden geprüft und können anschließend von den Nutzern gesucht werden.
					</p>
					<p class="text-2xl text-center">
						Tierärzte sind somit leichter von den Nutzern auffindbar und Tierbesitzer finden im
						Notfall schnell einen passenden Tierarzt.
					</p>
				</div>
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
					Du bist Tierarzt? Dann <label for="email-registration" class="btn btn-primary btn-sm"
						>klicke hier</label
					>
				</h1>

				<div class="mt-16 flex flex-col gap-5 justify-center items-center">
					<div class="mockup-phone">
						<div class="camera" />
						<div class="display">
							<div class="artboard artboard-demo phone-1">
								<img src="app.png" alt="VetFinder App" />
							</div>
						</div>
					</div>
					<h1 class="text-xl text-center">Hol dir jetzt unsere App!</h1>
					<div class="rating rating-lg rating-half pointer-events-none">
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-1 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-2 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-1 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-2 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-1 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-2 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-1 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-2 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-1 bg-yellow-300"
						/>
						<input
							disabled
							type="radio"
							name="rating-4"
							class="mask mask-star-2 mask-half-2 bg-yellow-50"
						/>
					</div>
					<div class="flex gap-2">
						<img src="google-play-badge.png" alt="Google Playstore" width="200px" />
						<img src="apple-badge.svg" alt="Apple Store" width="180px" />
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
