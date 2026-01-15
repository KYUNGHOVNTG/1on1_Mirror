import React from 'react';
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { Zap } from 'lucide-react';
import { jwtDecode } from 'jwt-decode';
import { useAuthStore } from '../../../core/store/useAuthStore';

export const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const { login } = useAuthStore();

    // .env에서 Client ID 가져오기 (없으면 빈 문자열)
    const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

    const handleSuccess = (credentialResponse: any) => {
        try {
            if (credentialResponse.credential) {
                const decoded: any = jwtDecode(credentialResponse.credential);
                console.log('Login Success:', decoded);

                // 간단한 유저 정보 저장 (실제로는 백엔드 검증 필요)
                login(
                    {
                        id: decoded.sub,
                        email: decoded.email,
                        name: decoded.name,
                        picture: decoded.picture
                    },
                    credentialResponse.credential
                );

                navigate('/dashboard');
            }
        } catch (error) {
            console.error('Login Failed', error);
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
                        <div className="w-full flex justify-center">
                            <GoogleLogin
                                onSuccess={handleSuccess}
                                onError={() => {
                                    console.log('Login Failed');
                                }}
                                useOneTap
                            />
                        </div>
                    )}

                    <p className="mt-8 text-xs text-slate-400">
                        © 2026 1on1 Mirror. All rights reserved.
                    </p>
                </div>
            </div>
        </GoogleOAuthProvider>
    );
};
