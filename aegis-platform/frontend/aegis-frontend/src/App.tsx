import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from 'next-themes';
import { Toaster } from 'sonner';

import { AuthProvider } from './hooks/useAuth';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { MainLayout } from './components/layout/MainLayout';
import { AuthLayout } from './components/layout/AuthLayout';

// Auth pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Dashboard pages
import DashboardPage from './pages/dashboard/DashboardPage';
import CisoCockpitPage from './pages/dashboard/CisoCockpitPage';
import AnalystWorkbenchPage from './pages/dashboard/AnalystWorkbenchPage';
import SystemOwnerInboxPage from './pages/dashboard/SystemOwnerInboxPage';

// Core module pages
import AssetsPage from './pages/assets/AssetsPage';
import AssetDetailsPage from './pages/assets/AssetDetailsPage';
import RisksPage from './pages/risks/RisksPage';
import RiskDetailsPage from './pages/risks/RiskDetailsPage';
import TasksPage from './pages/tasks/TasksPage';
import TaskDetailsPage from './pages/tasks/TaskDetailsPage';
import AssessmentsPage from './pages/assessments/AssessmentsPage';
import AssessmentDetailsPage from './pages/assessments/AssessmentDetailsPage';
import EvidencePage from './pages/evidence/EvidencePage';
import ReportsPage from './pages/reports/ReportsPage';
import IntegrationsPage from './pages/integrations/IntegrationsPage';
import UsersPage from './pages/users/UsersPage';
import SettingsPage from './pages/settings/SettingsPage';

// AI Management pages
import ProvidersPage from './pages/ai/ProvidersPage';
import AIAnalyticsPage from './pages/ai/AIAnalyticsPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <AuthProvider>
          <Router>
            <div className="min-h-screen bg-background font-sans antialiased">
              <Routes>
                {/* Auth routes */}
                <Route path="/login" element={
                  <AuthLayout>
                    <LoginPage />
                  </AuthLayout>
                } />
                <Route path="/register" element={
                  <AuthLayout>
                    <RegisterPage />
                  </AuthLayout>
                } />
                
                {/* Protected routes */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <MainLayout />
                  </ProtectedRoute>
                }>
                  {/* Dashboard routes */}
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard" element={<DashboardPage />} />
                  <Route path="dashboard/ciso" element={<CisoCockpitPage />} />
                  <Route path="dashboard/analyst" element={<AnalystWorkbenchPage />} />
                  <Route path="dashboard/system-owner" element={<SystemOwnerInboxPage />} />
                  
                  {/* Assets */}
                  <Route path="assets" element={<AssetsPage />} />
                  <Route path="assets/:id" element={<AssetDetailsPage />} />
                  
                  {/* Risks */}
                  <Route path="risks" element={<RisksPage />} />
                  <Route path="risks/:id" element={<RiskDetailsPage />} />
                  
                  {/* Tasks */}
                  <Route path="tasks" element={<TasksPage />} />
                  <Route path="tasks/:id" element={<TaskDetailsPage />} />
                  
                  {/* Assessments */}
                  <Route path="assessments" element={<AssessmentsPage />} />
                  <Route path="assessments/:id" element={<AssessmentDetailsPage />} />
                  
                  {/* Evidence */}
                  <Route path="evidence" element={<EvidencePage />} />
                  
                  {/* Reports */}
                  <Route path="reports" element={<ReportsPage />} />
                  
                  {/* Integrations */}
                  <Route path="integrations" element={<IntegrationsPage />} />
                  
                  {/* AI Management */}
                  <Route path="ai/providers" element={<ProvidersPage />} />
                  <Route path="ai/analytics" element={<AIAnalyticsPage />} />
                  
                  {/* Users */}
                  <Route path="users" element={<UsersPage />} />
                  
                  {/* Settings */}
                  <Route path="settings" element={<SettingsPage />} />
                </Route>
                
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
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;