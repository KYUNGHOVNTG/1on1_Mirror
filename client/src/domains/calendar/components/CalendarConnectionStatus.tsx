/**
 * Calendar Connection Status Component
 *
 * 캘린더 연동 상태를 표시하는 컴포넌트
 */

import React, { useEffect } from 'react';
import { useCalendarStore } from '../store';
import { CalendarConnectButton } from './CalendarConnectButton';
import { useNavigate } from 'react-router-dom';

interface CalendarConnectionStatusProps {
    /** 추가 CSS 클래스 */
    className?: string;
    /** 연동 해제 버튼 표시 여부 (기본값: true) */
    showDisconnectButton?: boolean;
}

/**
 * 캘린더 연동 상태 컴포넌트
 *
 * 연동 여부에 따라 다른 UI를 표시합니다.
 * - 연동 안됨: 연동 버튼 표시
 * - 연동됨: 연동 정보 및 해제 버튼 표시
 */
export const CalendarConnectionStatus: React.FC<CalendarConnectionStatusProps> = ({
    className = '',
    showDisconnectButton = true,
}) => {
    const { connection, loading, fetchConnection, disconnectCalendar } = useCalendarStore();
    const navigate = useNavigate();

    // 컴포넌트 마운트 시 연동 상태 조회
    useEffect(() => {
        fetchConnection();
    }, [fetchConnection]);

    const handleDisconnect = async () => {
        if (!confirm('캘린더 연동을 해제하시겠습니까?')) {
            return;
        }

        try {
            await disconnectCalendar();
            alert('캘린더 연동이 해제되었습니다.');
        } catch (error) {
            console.error('캘린더 연동 해제 실패:', error);
            alert('캘린더 연동 해제에 실패했습니다. 다시 시도해주세요.');
        }
    };

    // 로딩 중
    if (loading && !connection) {
        return (
            <div className={`flex items-center justify-center p-6 ${className}`}>
                <div className="flex items-center gap-3">
                    <div className="w-6 h-6 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
                    <p className="text-gray-600">연동 상태를 확인하는 중...</p>
                </div>
            </div>
        );
    }

    // 연동 안됨
    if (!connection) {
        return (
            <div className={`p-6 bg-white rounded-lg border border-gray-200 ${className}`}>
                <div className="flex items-start gap-4">
                    {/* 아이콘 */}
                    <div className="flex-shrink-0 w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                        <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    </div>

                    {/* 내용 */}
                    <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                            캘린더 연동 안됨
                        </h3>
                        <p className="text-sm text-gray-600 mb-4">
                            구글 캘린더를 연동하여 1:1 미팅 일정을 불러오세요.
                        </p>
                        <CalendarConnectButton />
                    </div>
                </div>
            </div>
        );
    }

    // 연동됨

    return (
        <div className={`p-6 bg-white rounded-lg border border-green-200 ${className}`}>
            <div className="flex items-start gap-4">
                {/* 성공 아이콘 */}
                <div className="flex-shrink-0 w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>

                {/* 내용 */}
                <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        캘린더 연동됨 ✅
                    </h3>
                    <div className="text-sm text-gray-600 space-y-1 mb-4">
                        <p>
                            <span className="font-medium">캘린더 ID:</span>{' '}
                            <span className="font-mono text-xs">{connection.google_calendar_id}</span>
                        </p>
                        <p>
                            <span className="font-medium">연동 일시:</span>{' '}
                            {new Date(connection.created_at).toLocaleString('ko-KR')}
                        </p>
                        {connection.webhook_expires_at && (
                            <p>
                                <span className="font-medium">Webhook 만료:</span>{' '}
                                {new Date(connection.webhook_expires_at).toLocaleString('ko-KR')}
                            </p>
                        )}
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={() => navigate('/calendar/events')}
                            className="
                                px-4 py-2
                                bg-indigo-600 hover:bg-indigo-700
                                text-white font-medium text-sm rounded-lg
                                transition-colors duration-200
                            "
                        >
                            이벤트 목록 보기
                        </button>

                        {/* 연동 해제 버튼 */}
                        {showDisconnectButton && (
                            <button
                                onClick={handleDisconnect}
                                disabled={loading}
                                className="
                                    px-4 py-2
                                    bg-white border border-red-300
                                    hover:bg-red-50
                                    text-red-600 font-medium text-sm rounded-lg
                                    transition-colors duration-200
                                    disabled:opacity-50 disabled:cursor-not-allowed
                                "
                            >
                                {loading ? '해제 중...' : '연동 해제'}
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
