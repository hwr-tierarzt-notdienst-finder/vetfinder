<script lang="ts">
	import { set_input_type } from 'svelte/internal';

	export let label: string;

	type InputType =
		| 'text'
		| 'email'
		| 'url'
		| 'tel'
		| 'number'
		| 'range'
		| 'radio'
		| 'color'
		| 'date'
		| 'month'
		| 'week'
		| 'time'
		| 'datetime-local'
		| 'password'
		| 'submit'
		| 'reset';
	export let type: InputType = 'text';
	export let placeholder: string = '';
	export let value: string = '';

	function typeAction(node: HTMLInputElement) {
		node.type = type;
	} // workaround, because two-way binding of type does not work in Svelte
</script>

<div class="form-control w-full max-w-xs">
	<!-- svelte-ignore a11y-label-has-associated-control -->
	<label class="label">
		<span class="label-text">{label}</span>
	</label>
	<input bind:value use:typeAction {placeholder} class="input input-bordered w-full max-w-xs" />
</div>
