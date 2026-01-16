import React, { useState } from 'react';
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { Zap } from 'lucide-react';
import { useAuthStore } from '../../../core/store/useAuthStore';
import { apiClient } from '../../../core/api/client';

export const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const { login } = useAuthStore();
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // .env에서 Client ID 가져오기 (없으면 빈 문자열)
    const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

    const handleSuccess = async (credentialResponse: any) => {
        try {
            setError(null);
            setIsLoading(true);

            if (credentialResponse.credential) {
                // 서버에 Google ID Token 전송
                const response = await apiClient.post('/v1/auth/google/login', {
                    id_token: credentialResponse.credential
                });

                const { user, tokens } = response.data;

                // AuthStore에 사용자 정보 및 토큰 저장
                login(user, tokens);

                console.log('Login Success:', user);

                navigate('/dashboard');
            }
        } catch (error: any) {
            console.error('Login Failed', error);
            setError(error.message || '로그인에 실패했습니다. 다시 시도해주세요.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
                <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-xl border border-slate-100 flex flex-col items-center text-center">

                    <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-6">
                        <Zap className="w-8 h-8 text-primary" fill="currentColor" />
                    </div>

                    <h1 className="text-3xl font-bold text-slate-900 mb-2">1on1 Mirror</h1>
                    <p className="text-slate-500 mb-8">AI 기반 원온원 미러링 서비스</p>

                    {!GOOGLE_CLIENT_ID ? (
                        <div className="p-4 bg-red-50 text-red-600 rounded-lg text-sm mb-4">
                            VITE_GOOGLE_CLIENT_ID가 설정되지 않았습니다.
                        </div>
                    ) : (
                        <>
                            {error && (
                                <div className="w-full p-4 bg-red-50 text-red-600 rounded-lg text-sm mb-4">
                                    {error}
                                </div>
                            )}
                            {isLoading ? (
                                <div className="w-full flex justify-center items-center py-4">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                                    <span className="ml-3 text-slate-600">로그인 중...</span>
                                </div>
                            ) : (
                                <div className="w-full flex justify-center">
                                    <GoogleLogin
                                        onSuccess={handleSuccess}
                                        onError={() => {
                                            console.log('Google Login Failed');
                                            setError('Google 로그인에 실패했습니다.');
                                        }}
                                        useOneTap
                                    />
                                </div>
                            )}
                        </>
                    )}

                    <p className="mt-8 text-xs text-slate-400">
                        © 2026 1on1 Mirror. All rights reserved.
                    </p>
                </div>
            </div>
        </GoogleOAuthProvider>
    );
};
