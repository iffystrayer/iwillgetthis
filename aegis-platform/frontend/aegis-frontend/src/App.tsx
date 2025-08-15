import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from 'next-themes';
import { Toaster } from 'sonner';
import { Suspense, lazy } from 'react';

import { AuthProvider } from './hooks/useAuth';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { MainLayout } from './components/layout/MainLayout';
import { AuthLayout } from './components/layout/AuthLayout';
import { LoadingSpinner } from './components/ui/loading-spinner';

// Auth pages (keep these eager loaded for better UX)
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Lazy load dashboard pages
const DashboardPage = lazy(() => import('./pages/dashboard/DashboardPage'));
const CisoCockpitPage = lazy(() => import('./pages/dashboard/CisoCockpitPage'));
const AnalystWorkbenchPage = lazy(() => import('./pages/dashboard/AnalystWorkbenchPage'));
const SystemOwnerInboxPage = lazy(() => import('./pages/dashboard/SystemOwnerInboxPage'));

// Lazy load core module pages
const AssetsPage = lazy(() => import('./pages/assets/AssetsPage'));
const AssetDetailsPage = lazy(() => import('./pages/assets/AssetDetailsPage'));
const RisksPage = lazy(() => import('./pages/risks/RisksPage'));
const RiskDetailsPage = lazy(() => import('./pages/risks/RiskDetailsPage'));
const TasksPage = lazy(() => import('./pages/tasks/TasksPage'));
const TaskDetailsPage = lazy(() => import('./pages/tasks/TaskDetailsPage'));
const AssessmentsPage = lazy(() => import('./pages/assessments/AssessmentsPage'));
const AssessmentDetailsPage = lazy(() => import('./pages/assessments/AssessmentDetailsPage'));
const EvidencePage = lazy(() => import('./pages/evidence/EvidencePage'));
const ReportsPage = lazy(() => import('./pages/reports/ReportsPage'));
const IntegrationsPage = lazy(() => import('./pages/integrations/IntegrationsPage'));
const UsersPage = lazy(() => import('./pages/users/UsersPage'));
const SettingsPage = lazy(() => import('./pages/settings/SettingsPage'));
const NotificationSettingsPage = lazy(() => import('./pages/settings/NotificationSettingsPage'));

// Lazy load AI Management pages
const ProvidersPage = lazy(() => import('./pages/ai/ProvidersPage'));
const AIAnalyticsPage = lazy(() => import('./pages/ai/AIAnalyticsPage'));

// Lazy load Workflow Management pages
const WorkflowsPage = lazy(() => import('./pages/workflows/WorkflowsPage'));
const WorkflowInstancesPage = lazy(() => import('./pages/workflows/WorkflowInstancesPage'));

// Loading fallback component
const PageLoadingFallback = () => (
  <div className="flex items-center justify-center min-h-96">
    <LoadingSpinner size="lg" />
  </div>
);

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
                  <Route path="dashboard" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <DashboardPage />
                    </Suspense>
                  } />
                  <Route path="dashboard/ciso" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <CisoCockpitPage />
                    </Suspense>
                  } />
                  <Route path="dashboard/analyst" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <AnalystWorkbenchPage />
                    </Suspense>
                  } />
                  <Route path="dashboard/system-owner" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <SystemOwnerInboxPage />
                    </Suspense>
                  } />
                  
                  {/* Assets */}
                  <Route path="assets" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <AssetsPage />
                    </Suspense>
                  } />
                  <Route path="assets/:id" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <AssetDetailsPage />
                    </Suspense>
                  } />
                  
                  {/* Risks */}
                  <Route path="risks" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <RisksPage />
                    </Suspense>
                  } />
                  <Route path="risks/:id" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <RiskDetailsPage />
                    </Suspense>
                  } />
                  
                  {/* Tasks */}
                  <Route path="tasks" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <TasksPage />
                    </Suspense>
                  } />
                  <Route path="tasks/:id" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <TaskDetailsPage />
                    </Suspense>
                  } />
                  
                  {/* Assessments */}
                  <Route path="assessments" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <AssessmentsPage />
                    </Suspense>
                  } />
                  <Route path="assessments/:id" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <AssessmentDetailsPage />
                    </Suspense>
                  } />
                  
                  {/* Evidence */}
                  <Route path="evidence" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <EvidencePage />
                    </Suspense>
                  } />
                  
                  {/* Reports */}
                  <Route path="reports" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <ReportsPage />
                    </Suspense>
                  } />
                  
                  {/* Integrations */}
                  <Route path="integrations" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <IntegrationsPage />
                    </Suspense>
                  } />
                  
                  {/* AI Management */}
                  <Route path="ai/providers" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <ProvidersPage />
                    </Suspense>
                  } />
                  <Route path="ai/analytics" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <AIAnalyticsPage />
                    </Suspense>
                  } />
                  
                  {/* Workflow Management */}
                  <Route path="workflows" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <WorkflowsPage />
                    </Suspense>
                  } />
                  <Route path="workflows/instances" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <WorkflowInstancesPage />
                    </Suspense>
                  } />
                  
                  {/* Users */}
                  <Route path="users" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <UsersPage />
                    </Suspense>
                  } />
                  
                  {/* Settings */}
                  <Route path="settings" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <SettingsPage />
                    </Suspense>
                  } />
                  <Route path="settings/notifications" element={
                    <Suspense fallback={<PageLoadingFallback />}>
                      <NotificationSettingsPage />
                    </Suspense>
                  } />
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