# Mosaiq Frontend

This is the frontend for the Mosaiq app, built with Next.js.

## Prerequisites

Before running the app, make sure you have:

- Node.js 20+ installed
- npm installed
- a terminal open in this project folder

## Install dependencies

From the project root:

```bash
cd "frontend 10.56.22 PM"
npm install
```

## Run the app locally

Start the development server:

```bash
npm run dev
```

Then open:

```text
http://localhost:3000

```

## Production build

To create a production build:

```bash
npm run build
```

To run the production build locally:

```bash
npm run start
```

## Linting

```bash
npm run lint
```

## Project structure

```text
src/
  app/
  components/
  lib/
  types/
public/
```

## Main routes

These are the main pages currently available in the frontend:

- `/` — landing page
- `/onboarding` — onboarding flow
- `/signup` — signup page
- `/login` — login page
- `/brand-setup` — create a new brand profile
- `/dashboard` — main dashboard
- `/reviews` — approvals / review queue page

## Notes

- This app uses the Next.js App Router.
- The project is configured for TypeScript and uses custom app routes under `src/app`.
- If you change UI code, the dev server will hot reload automatically.

## Troubleshooting

If `npm install` fails, make sure you are inside the frontend folder and not the parent project directory.

Example:

```bash
cd "/Users/your-name/Downloads/Multi-Platform_AI_Content/frontend 10.56.22 PM"
```

Then run:

```bash
npm install
npm run dev
```
