# VetFinder Form Website

## Project Structure

`bin`: contains script to build and deploy the website

`src`: main content
- `api`: communication with backend via REST
- `components`: components that are used multiple times
- `routes`:
  - `/`: start page with statistics and information about the project 
  - `/form`: form page for data collection
- `types`: collection of types and conversion functions used throughout the project

`static`: contains images

`.env.sample`: template for `.env` file (variables are explained in the `Setup` section)

## Setup
1. copy `.env.sample` file and rename it to `.env`
2. fill in the following variables:
   1. `VITE_API_URL` - URL on which the backend is running and API is available
   2. `VITE_JWT_TOKEN` - it is the created JWT token from the backend

## Developing

1. Install dependencies with `npm install` (or `pnpm install` or `yarn`)
2. Start the development server:

```bash
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of the website:

```bash
npm run build
```

You can preview the production build with `npm run preview`.