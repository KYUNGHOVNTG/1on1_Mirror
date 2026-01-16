import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './domains/auth/pages/LoginPage';
import { DashboardPage } from './domains/dashboard/pages/DashboardPage';
import { CalendarCallbackPage, CalendarEventListPage } from './domains/calendar';
import { useAuthStore } from './core/store/useAuthStore';
import { LoadingOverlay } from './core/loading';

// 보호된 라우트 컴포넌트
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <BrowserRouter>
      {/* 전역 로딩 오버레이 */}
      <LoadingOverlay />

      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/calendar/callback"
          element={
            <ProtectedRoute>
              <CalendarCallbackPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/calendar/events"
          element={
            <ProtectedRoute>
              <CalendarEventListPage />
            </ProtectedRoute>
          }
        />
        {/* 없는 페이지는 로그인 화면으로 리다이렉트 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;