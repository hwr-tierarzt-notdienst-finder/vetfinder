<script lang="ts">
	import '../app.css';
	import { themeChange } from 'theme-change';
	import { onMount } from 'svelte';
	import { sendVetRegistrationEmail } from '../api';
	import { goto } from '$app/navigation';

	onMount(() => {
		themeChange(false);
	});

	let registrationEmail: string = '';

	function regsiter() {
		if (registrationEmail) {
			sendVetRegistrationEmail(registrationEmail);
			registrationEmail = '';
		}
	}

	function goToHome() {
		goto('/');
	}
</script>

<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
<!-- svelte-ignore a11y-label-has-associated-control -->
<!-- svelte-ignore a11y-missing-attribute -->
<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="w-full h-screen table m-0">
	<!-- Register modal -->
	<input type="checkbox" id="email-registration" class="modal-toggle" />
	<div class="modal modal-bottom sm:modal-middle">
		<div class="modal-box">
			<h3 class="font-bold text-lg">Registrierung</h3>
			<p class="py-4">
				Bitte geben Sie Ihre E-Mail an und drücken Sie auf "Registrieren". Sie bekommen anschließend
				eine E-Mail, die es Ihnen ermöglicht, sich in unser System einzutragen.
			</p>
			<div class="form-control w-full max-w-xs">
				<!-- svelte-ignore a11y-label-has-associated-control -->
				<label class="label">
					<span class="label-text">E-Mail</span>
				</label>
				<input
					placeholder="Hier eingeben"
					type="email"
					bind:value={registrationEmail}
					class="input input-bordered w-full max-w-xs"
				/>
			</div>
			<div class="modal-action">
				<label for="email-registration" class="btn btn-ghost">Schließen</label>
				<label for="email-registration" class="btn" on:click={regsiter}>Registrieren</label>
			</div>
		</div>
	</div>
	<!-- Register modal -->
	<!-- Success modal -->
	<input type="checkbox" id="change-success-modal" class="modal-toggle" />
	<div class="modal modal-bottom sm:modal-middle">
		<div class="modal-box">
			<h3 class="font-bold text-lg">Änderung erfolgreich</h3>
			<p class="py-4">Ihre Änderung an Ihren Daten war erfolgreich.</p>
			<div class="modal-action">
				<label for="change-success-modal" class="btn btn-success" on:click={goToHome}
					>Schließen</label
				>
			</div>
		</div>
	</div>
	<!-- Success modal -->
	<div class="navbar bg-base-100">
		<div class="navbar-start" />
		<div class="navbar-center">
			<a class="btn btn-ghost normal-case text-xl" href="/">VetFinder</a>
		</div>
		<div class="navbar-end">
			<label class="swap swap-rotate">
				<!-- this hidden checkbox controls the state -->
				<input data-toggle-theme="light,dark" type="checkbox" />

				<!-- moon icon -->
				<svg
					class="swap-off fill-current w-8 h-8"
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					><path
						d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z"
					/></svg
				>

				<!-- sun icon -->
				<svg
					class="swap-on fill-current w-8 h-8"
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					><path
						d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z"
					/></svg
				>
			</label>
		</div>
	</div>

	<slot />

	<div class="table-row h-0">
		<footer class="footer footer-center mt-5 p-5 bg-base-200 text-base-content rounded">
			<div class="grid grid-flow-col gap-4">
				<a class="link link-hover">Über uns</a>
				<a class="link link-hover">Kontakt</a>
				<a class="link link-hover">Datenschutz</a>
			</div>
			<div>
				<p>
					Copyright © 2022 - All right reserved by <a
						href="https://www.hwr-berlin.de/"
						class="link link-hover ">HWR</a
					>
				</p>
			</div>
		</footer>
	</div>
</div>

<style lang="postcss">
</style>
