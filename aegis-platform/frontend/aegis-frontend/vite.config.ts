import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 58533, // Random port to avoid conflicts
    host: '127.0.0.1'
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor libraries
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'react-vendor';
            }
            if (id.includes('lucide-react') || id.includes('@radix-ui')) {
              return 'ui-vendor';
            }
            if (id.includes('react-hook-form') || id.includes('@hookform') || id.includes('zod')) {
              return 'form-vendor';
            }
            if (id.includes('axios') || id.includes('class-variance-authority') || id.includes('clsx') || id.includes('tailwind-merge')) {
              return 'utils-vendor';
            }
            return 'vendor';
          }
          
          // Application chunks by feature
          if (id.includes('/pages/dashboard/') || id.includes('/components/ui/chart')) {
            return 'dashboard';
          }
          if (id.includes('/pages/assets/') || id.includes('/dialogs/NewAssetDialog')) {
            return 'assets';
          }
          if (id.includes('/pages/risks/') || id.includes('/dialogs/NewRiskDialog')) {
            return 'risks';
          }
          if (id.includes('/pages/assessments/') || id.includes('/dialogs/NewAssessmentDialog')) {
            return 'assessments';
          }
          if (id.includes('/pages/tasks/') || id.includes('/dialogs/NewTaskDialog')) {
            return 'tasks';
          }
          if (id.includes('/pages/users/') || id.includes('/dialogs/AddUserDialog') || id.includes('/dialogs/InviteUsersDialog')) {
            return 'users';
          }
          if (id.includes('/pages/reports/')) {
            return 'reports';
          }
          if (id.includes('/pages/integrations/')) {
            return 'integrations';
          }
        }
      }
    },
    chunkSizeWarningLimit: 600,
    minify: 'esbuild',
  },
})

