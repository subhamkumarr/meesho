# Frontend Setup Instructions

## Prerequisites
Make sure you have Node.js (version 18 or higher) and npm installed on your system.

## Installation Steps

1. **Install dependencies:**
   ```bash
   cd catalogai/frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Troubleshooting

If you encounter TypeScript errors:
1. Make sure all dependencies are installed: `npm install`
2. Clear Next.js cache: `rm -rf .next`
3. Restart the development server

## Dependencies Overview

The project uses:
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - API client
- **Radix UI** - Accessible components

## Environment Variables

Create a `.env.local` file with:
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```