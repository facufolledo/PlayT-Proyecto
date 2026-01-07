import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export default function DebugAuth() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [debugInfo, setDebugInfo] = useState<any>({});

  useEffect(() => {
    const info = {
      currentUrl: window.location.href,
      origin: window.location.origin,
      pathname: window.location.pathname,
      search: window.location.search,
      baseUrl: import.meta.env.BASE_URL,
      mode: import.meta.env.MODE,
      prod: import.meta.env.PROD,
      searchParams: Object.fromEntries(searchParams.entries()),
      expectedLoginUrl: `${window.location.origin}${import.meta.env.BASE_URL}login`,
    };
    
    setDebugInfo(info);
    console.log('🔍 Debug Auth Info:', info);
  }, [searchParams]);

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-textPrimary mb-6">Debug Auth - Drive+</h1>
        
        <div className="bg-cardBg rounded-lg p-6 border border-cardBorder">
          <h2 className="text-lg font-semibold text-textPrimary mb-4">Información de Debug</h2>
          
          <pre className="bg-gray-900 text-green-400 p-4 rounded text-sm overflow-auto">
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
          
          <div className="mt-6 space-y-2">
            <button
              onClick={() => navigate('/login')}
              className="bg-primary text-white px-4 py-2 rounded mr-4"
            >
              Ir a Login
            </button>
            
            <button
              onClick={() => navigate('/login?verified=true')}
              className="bg-green-600 text-white px-4 py-2 rounded mr-4"
            >
              Ir a Login (Verified)
            </button>
            
            <button
              onClick={() => navigate('/')}
              className="bg-gray-600 text-white px-4 py-2 rounded"
            >
              Ir a Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}