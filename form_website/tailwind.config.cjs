/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {}
	},
	plugins: [require('daisyui')],
	daisyui: {
		themes: [
			{
				light: {
					...require('daisyui/src/colors/themes')['[data-theme=light]'],
					primary: '#dc2626'
				},
				dark: {
					...require('daisyui/src/colors/themes')['[data-theme=dark]'],
					primary: '#7f1d1d'
				}
			}
		]
	}
};
