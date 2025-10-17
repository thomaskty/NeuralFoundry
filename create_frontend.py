#!/usr/bin/env python3
"""
Frontend Generator Script
Creates complete React + Vite frontend structure with all files
Run: python create_frontend.py
"""
import os
import json


def create_file(path, content):
    """Create file with content"""
    dir_path = os.path.dirname(path)
    if dir_path:  # Only create dir if path has a directory component
        os.makedirs(dir_path, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Created: {path}")


def create_frontend():
    """Generate complete frontend structure"""

    print("🚀 Creating frontend structure...\n")

    # Create base directory and change to it
    os.makedirs("frontend", exist_ok=True)

    # Save original directory
    original_dir = os.getcwd()

    try:
        os.chdir("frontend")
    except Exception as e:
        print('exception :',e)

    # ============================================================================
    # package.json
    # ============================================================================
    package_json = {
        "name": "neural-foundry-ui",
        "private": True,
        "version": "0.0.1",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "axios": "^1.6.0",
            "react-markdown": "^9.0.1",
            "react-syntax-highlighter": "^15.5.0",
            "lucide-react": "^0.263.1"
        },
        "devDependencies": {
            "@types/react": "^18.3.3",
            "@types/react-dom": "^18.3.0",
            "@vitejs/plugin-react": "^4.3.1",
            "autoprefixer": "^10.4.16",
            "postcss": "^8.4.32",
            "tailwindcss": "^3.3.6",
            "vite": "^5.3.4"
        }
    }

    create_file("package.json", json.dumps(package_json, indent=2))

    # ============================================================================
    # vite.config.js
    # ============================================================================
    vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
"""
    create_file("vite.config.js", vite_config)

    # ============================================================================
    # tailwind.config.js
    # ============================================================================
    tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#6366F1',
      }
    },
  },
  plugins: [],
}
"""
    create_file("tailwind.config.js", tailwind_config)

    # ============================================================================
    # postcss.config.js
    # ============================================================================
    postcss_config = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
    create_file("postcss.config.js", postcss_config)

    # ============================================================================
    # index.html
    # ============================================================================
    index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Neural::Foundry</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
    create_file("index.html", index_html)

    # ============================================================================
    # src/main.jsx
    # ============================================================================
    main_jsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    create_file("src/main.jsx", main_jsx)

    # ============================================================================
    # src/index.css
    # ============================================================================
    index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
"""
    create_file("src/index.css", index_css)

    print("\n" + "=" * 70)
    print("✅ Frontend structure created successfully!")
    print("=" * 70)
    print("\n📋 Next steps:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("\n🌐 Frontend will run on: http://localhost:3000")
    print("🔌 Backend proxy configured for: http://localhost:8000")
    print("\n💡 I'll provide the React components in the next message!")

    os.chdir(original_dir)


if __name__ == "__main__":
    create_frontend()