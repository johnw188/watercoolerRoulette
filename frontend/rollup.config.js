import svelte from 'rollup-plugin-svelte-hot';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';

const watch = process.env.ROLLUP_WATCH;
const production = !watch;
const hot = !production && !!watch;

export default {
	input: 'src/main.js',
	output: {
		sourcemap: true,
		format: 'iife',
		name: 'app',
		file: 'public/build/bundle.js'
	},
	plugins: [
		svelte({
			// enable run-time checks when not in production
			dev: !production,
			// we'll extract any component CSS out into
			// a separate file - better for performance
			css: css => {
				css.write('public/build/bundle.css');
			},
			hot: hot && {
				// Prevent preserving local component state
				noPreserveState: false,
		
				// If this string appears anywhere in your component's code, then local
				// state won't be preserved, even when noPreserveState is false
				noPreserveStateKey: '@!hmr',
		
				// Prevent doing a full reload on next HMR update after fatal error
				noReload: false,
		
				// Try to recover after runtime errors in component init
				optimistic: false,
		
				// --- Advanced ---
		
				// Prevent adding an HMR accept handler to components with
				// accessors option to true, or to components with named exports
				// (from <script context="module">). This have the effect of
				// recreating the consumer of those components, instead of the
				// component themselves, on HMR updates. This might be needed to
				// reflect changes to accessors / named exports in the parents,
				// depending on how you use them.
				acceptAccessors: false,
				acceptNamedExports: false,
		
				// Set true to enable support for Nollup (note: when not specified, this
				// is automatically detected based on the NOLLUP env variable)
				nollup: false,
			  },
		}),

		// If you have external dependencies installed from
		// npm, you'll most likely need these plugins. In
		// some cases you'll need additional configuration -
		// consult the documentation for details:
		// https://github.com/rollup/plugins/tree/master/packages/commonjs
		resolve({
			browser: true,
			dedupe: ['svelte']
		}),
		commonjs(),

		// In dev mode, call `npm run start` once
		// the bundle has been generated
		!production && serve(),

		// Watch the `public` directory and refresh the
		// browser on changes when not in production
		!production && livereload('public'),

		// If we're building for production (npm run build
		// instead of npm run dev), minify
		production && terser()
	],
	watch: {
		clearScreen: false
	}
};

function serve() {
	let started = false;

	return {
		writeBundle() {
			if (!started) {
				started = true;

				require('child_process').spawn('npm', ['run', 'start', '--', '--dev'], {
					stdio: ['ignore', 'inherit', 'inherit'],
					shell: true
				});
			}
		}
	};
}
