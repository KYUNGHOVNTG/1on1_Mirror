/**
 * Calendar OAuth Callback Page
 *
 * 구글 OAuth 인증 후 리다이렉트되는 페이지
 * 인증 코드를 받아서 백엔드로 전송하고 연동을 완료합니다.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useCalendarStore } from '../store';

/**
 * 캘린더 OAuth 콜백 페이지
 *
 * URL 파라미터에서 인증 코드를 추출하고 백엔드로 전송합니다.
 */
export const CalendarCallbackPage: React.FC = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const { connectCalendar } = useCalendarStore();

    const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
    const [errorMessage, setErrorMessage] = useState<string>('');

    useEffect(() => {
        const handleCallback = async () => {
            // URL에서 인증 코드 추출
            const code = searchParams.get('code');
            const error = searchParams.get('error');

            // 에러가 있는 경우
            if (error) {
                setStatus('error');
                setErrorMessage(`인증이 취소되었습니다: ${error}`);
                return;
            }

            // 인증 코드가 없는 경우
            if (!code) {
                setStatus('error');
                setErrorMessage('인증 코드를 받지 못했습니다.');
                return;
            }

            try {
                // 백엔드로 인증 코드 전송
                const redirectUri = `${window.location.origin}/calendar/callback`;
                await connectCalendar(code, redirectUri);

                setStatus('success');

                // 2초 후 대시보드로 이동
                setTimeout(() => {
                    navigate('/dashboard', { replace: true });
                }, 2000);
            } catch (error: any) {
                console.error('캘린더 연동 실패:', error);
                setStatus('error');
                setErrorMessage(
                    error.message || '캘린더 연동에 실패했습니다. 다시 시도해주세요.'
                );
            }
        };

        handleCallback();
    }, [searchParams, connectCalendar, navigate]);

    // 처리 중
    if (status === 'processing') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
                <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
                    <div className="text-center">
                        {/* 로딩 스피너 */}
                        <div className="w-16 h-16 mx-auto mb-6">
                            <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                        </div>

                        <h1 className="text-2xl font-bold text-gray-900 mb-2">
                            캘린더 연동 중...
                        </h1>
                        <p className="text-gray-600">
                            구글 캘린더를 연동하고 있습니다.
                            <br />
                            잠시만 기다려주세요.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    // 성공
    if (status === 'success') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50 flex items-center justify-center p-4">
                <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
                    <div className="text-center">
                        {/* 성공 아이콘 */}
                        <div className="w-16 h-16 mx-auto mb-6 bg-green-100 rounded-full flex items-center justify-center">
                            <svg
                                className="w-10 h-10 text-green-600"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                />
                            </svg>
                        </div>

                        <h1 className="text-2xl font-bold text-gray-900 mb-2">
                            연동 완료! 🎉
                        </h1>
                        <p className="text-gray-600 mb-6">
                            구글 캘린더가 성공적으로 연동되었습니다.
                            <br />
                            대시보드로 이동합니다...
                        </p>

                        {/* 진행 바 */}
                        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                            <div className="bg-green-600 h-full rounded-full animate-progress-bar" />
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // 에러
    return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
                <div className="text-center">
                    {/* 에러 아이콘 */}
                    <div className="w-16 h-16 mx-auto mb-6 bg-red-100 rounded-full flex items-center justify-center">
                        <svg
                            className="w-10 h-10 text-red-600"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                    </div>

                    <h1 className="text-2xl font-bold text-gray-900 mb-2">연동 실패</h1>
                    <p className="text-gray-600 mb-6">{errorMessage}</p>

                    {/* 버튼 */}
                    <div className="flex gap-3">
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="
                flex-1 px-4 py-2
                bg-gray-100 hover:bg-gray-200
                text-gray-700 font-medium rounded-lg
                transition-colors duration-200
              "
                        >
                            대시보드로
                        </button>
                        <button
                            onClick={() => window.location.reload()}
                            className="
                flex-1 px-4 py-2
                bg-blue-600 hover:bg-blue-700
                text-white font-medium rounded-lg
                transition-colors duration-200
              "
                        >
                            다시 시도
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
