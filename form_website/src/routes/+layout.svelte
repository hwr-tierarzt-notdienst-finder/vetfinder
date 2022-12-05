<script lang="ts">
	import '../app.css';
</script>

<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
<!-- svelte-ignore a11y-label-has-associated-control -->
<!-- svelte-ignore a11y-missing-attribute -->
<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="w-full h-screen table m-0">
	<div class="navbar bg-base-100">
		<div class="navbar-start">
			<div class="dropdown">
				<label tabindex="0" class="btn btn-ghost btn-circle">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-5 w-5"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 6h16M4 12h16M4 18h7"
						/></svg
					>
				</label>
				<ul
					tabindex="0"
					class="menu menu-compact dropdown-content mt-3 p-2 shadow bg-base-100 rounded-box w-52"
				>
					<li><a href="/">Startseite</a></li>
					<li><a href="/form">Eintragen</a></li>
					<li><a href="/about_us">Über uns</a></li>
				</ul>
			</div>
		</div>
		<div class="navbar-center">
			<a class="btn btn-ghost normal-case text-xl" href="/">VetFinder</a>
		</div>
		<div class="navbar-end" />
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
