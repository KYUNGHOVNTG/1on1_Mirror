/**
 * Calendar Connect Button Component
 *
 * 구글 캘린더 연동 버튼 컴포넌트
 * OAuth 인증 URL로 리다이렉트합니다.
 */

import React from 'react';
import { useCalendarStore } from '../store';

interface CalendarConnectButtonProps {
    /** 버튼 텍스트 (기본값: "구글 캘린더 연동하기") */
    label?: string;
    /** 추가 CSS 클래스 */
    className?: string;
    /** 연동 완료 후 콜백 */
    onConnected?: () => void;
}

/**
 * 구글 캘린더 연동 버튼
 *
 * 클릭 시 구글 OAuth 인증 페이지로 리다이렉트됩니다.
 */
export const CalendarConnectButton: React.FC<CalendarConnectButtonProps> = ({
    label = '구글 캘린더 연동하기',
    className = '',
}) => {
    const { loading } = useCalendarStore();

    const handleConnect = () => {
        // 환경변수에서 Google Client ID 가져오기
        const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
        const redirectUri = `${window.location.origin}/calendar/callback`;

        if (!clientId) {
            console.error('VITE_GOOGLE_CLIENT_ID가 설정되지 않았습니다.');
            alert('구글 클라이언트 ID가 설정되지 않았습니다. 관리자에게 문의하세요.');
            return;
        }

        // Google OAuth URL 생성
        const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
        authUrl.searchParams.append('client_id', clientId);
        authUrl.searchParams.append('redirect_uri', redirectUri);
        authUrl.searchParams.append('response_type', 'code');
        authUrl.searchParams.append('scope', 'https://www.googleapis.com/auth/calendar.readonly');
        authUrl.searchParams.append('access_type', 'offline');
        authUrl.searchParams.append('prompt', 'consent');

        // OAuth 인증 페이지로 리다이렉트
        window.location.href = authUrl.toString();
    };

    return (
        <button
            onClick={handleConnect}
            disabled={loading}
            className={`
        inline-flex items-center justify-center gap-2
        px-6 py-3 
        bg-gradient-to-r from-blue-600 to-blue-700 
        hover:from-blue-700 hover:to-blue-800
        text-white font-semibold rounded-lg
        shadow-md hover:shadow-lg
        transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        disabled:hover:from-blue-600 disabled:hover:to-blue-700
        ${className}
      `}
        >
            {/* Google 아이콘 */}
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>

            {loading ? '연동 중...' : label}
        </button>
    );
};
