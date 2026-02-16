# RAG Knowledge Base Frontend

This is the frontend part of the RAG Knowledge Base system, built with React, TypeScript, and Tailwind CSS.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Copy the environment example file:
```bash
cp .env.example .env
```

Adjust the API URL if necessary:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Run Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### 4. Build for Production
```bash
npm run build
```

The built files will be in the `dist` directory.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn/UI** - Component library
- **Vite** - Build tool
- **Axios** - HTTP client
- **Radix UI** - Accessible components

## Project Structure

```
src/
├── components/
│   ├── ui/              # Base UI components
│   ├── ChatArea.tsx     # Chat interface
│   ├── DocumentUpload.tsx  # File upload
│   ├── KnowledgePanel.tsx  # Document management
│   └── ConfigPanel.tsx  # Configuration panel
├── lib/
│   ├── api.ts           # API client
│   ├── types.ts         # TypeScript types
│   └── utils.ts         # Utility functions
├── App.tsx              # Main app component
└── main.tsx             # Entry point
```

## Features

- 📄 Multi-format document upload (PDF, DOCX, XLSX, TXT, CSV)
- 💬 Intelligent Q&A with RAG
- 🔍 Vector similarity search
- 📊 Knowledge base management
- ⚙️ Real-time configuration
- 📱 Responsive design

## API Integration

The frontend connects to the backend API at `/api/v1`. Make sure the backend server is running before starting the frontend.

## License

MIT
