import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from 'next-themes';
import { Toaster } from 'sonner';

// Simple dashboard without authentication
import DashboardPageSimple from './pages/dashboard/DashboardPageSimple';

function AppSimple() {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <Router>
        <div className="min-h-screen bg-background font-sans antialiased">
          <Routes>
            {/* Simple dashboard route */}
            <Route path="/" element={<DashboardPageSimple />} />
            <Route path="/dashboard" element={<DashboardPageSimple />} />
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        <Toaster 
          position="top-right" 
          expand={true}
          richColors
          closeButton
        />
      </Router>
    </ThemeProvider>
  );
}

export default AppSimple;