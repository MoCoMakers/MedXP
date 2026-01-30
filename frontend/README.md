# MedXP Frontend

A modern clinical handoff platform built with React, TypeScript, Vite, and Tailwind CSS.

## Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)

## Installation

Install the dependencies:

```bash
npm install
```

## Running the Application

Start the development server:

```bash
npm run dev
```

The application will be available at:
- Local: http://localhost:8080/
- Network: http://10.255.250.218:8080/ (or your local IP)

The development server supports hot module replacement, so changes will be reflected automatically.

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run preview` - Preview the production build locally
- `npm run lint` - Run ESLint to check code quality
- `npm test` - Run tests once
- `npm run test:watch` - Run tests in watch mode

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Headless UI components
- **React Router** - Client-side routing
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **Recharts** - Data visualization
- **Vitest** - Testing framework

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Page components
├── hooks/         # Custom React hooks
├── lib/           # Utility functions
├── types/         # TypeScript type definitions
└── data/          # Mock data and constants
```

## Development

The project uses:
- **ESLint** for code linting
- **Tailwind CSS** for styling
- **Shadcn/ui** for pre-built components
- **React Query** for data fetching and caching

## Troubleshooting

If you encounter any issues:

1. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Check Node.js version:
   ```bash
   node --version
   ```

3. Make sure you're in the frontend directory:
   ```bash
   cd /Users/jeevasaravanabhavanandam/Documents/MedXP/frontend
   ```
