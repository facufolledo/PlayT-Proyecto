import React, { useState } from 'react';
import { api } from '../services/api';

interface TestResult {
  endpoint: string;
  method: string;
  success: boolean;
  status?: number;
  error?: string;
  data?: any;
  headers?: Record<string, string>;
}

export const CorsDebug: React.FC = () => {
  const [results, setResults] = useState<TestResult[]>([]);
  const [testing, setTesting] = useState(false);

  const testEndpoint = async (endpoint: string, method: 'GET' | 'POST' = 'GET'): Promise<TestResult> => {
    try {
      let response;
      
      if (method === 'GET') {
        response = await api.get(endpoint);
      } else {
        response = await api.post(endpoint, { test: true });
      }

      return {
        endpoint,
        method,
        success: true,
        status: response.status,
        data: response.data,
        headers: Object.fromEntries(
          Object.entries(response.headers).filter(([key]) => 
            key.toLowerCase().includes('access-control') || 
            key.toLowerCase().includes('cors')
          )
        )
      };
    } catch (error: any) {
      return {
        endpoint,
        method,
        success: false,
        error: error.message,
        status: error.response?.status
      };
    }
  };

  const runTests = async () => {
    setTesting(true);
    setResults([]);

    const tests = [
      { endpoint: '/health', method: 'GET' as const },
      { endpoint: '/debug/cors', method: 'GET' as const },
      { endpoint: '/api/test-cors', method: 'GET' as const },
      { endpoint: '/api/test-cors', method: 'POST' as const },
      { endpoint: '/', method: 'GET' as const }
    ];

    const testResults: TestResult[] = [];

    for (const test of tests) {
      console.log(`🔍 Probando ${test.method} ${test.endpoint}`);
      const result = await testEndpoint(test.endpoint, test.method);
      testResults.push(result);
      setResults([...testResults]);
      
      // Pequeña pausa entre tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setTesting(false);
  };

  const getStatusColor = (result: TestResult) => {
    if (result.success) return 'text-green-600';
    if (result.status === 0 || result.error?.includes('CORS')) return 'text-red-600';
    return 'text-yellow-600';
  };

  const getStatusIcon = (result: TestResult) => {
    if (result.success) return '✅';
    if (result.status === 0 || result.error?.includes('CORS')) return '❌';
    return '⚠️';
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">🔧 Diagnóstico CORS</h2>
      
      <div className="mb-4">
        <p className="text-gray-600 mb-2">
          <strong>Frontend:</strong> {window.location.origin}
        </p>
        <p className="text-gray-600 mb-4">
          <strong>Backend:</strong> {import.meta.env.VITE_API_URL}
        </p>
        
        <button
          onClick={runTests}
          disabled={testing}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          {testing ? '🔄 Probando...' : '🚀 Ejecutar Pruebas CORS'}
        </button>
      </div>

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Resultados:</h3>
          
          {results.map((result, index) => (
            <div key={index} className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-sm">
                  {getStatusIcon(result)} {result.method} {result.endpoint}
                </span>
                <span className={`font-semibold ${getStatusColor(result)}`}>
                  {result.success ? `${result.status} OK` : `${result.status || 'CORS'} Error`}
                </span>
              </div>
              
              {result.error && (
                <div className="text-red-600 text-sm mb-2">
                  <strong>Error:</strong> {result.error}
                </div>
              )}
              
              {result.data && (
                <div className="text-sm mb-2">
                  <strong>Response:</strong>
                  <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </div>
              )}
              
              {result.headers && Object.keys(result.headers).length > 0 && (
                <div className="text-sm">
                  <strong>CORS Headers:</strong>
                  <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                    {JSON.stringify(result.headers, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
          
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">💡 Interpretación:</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>✅ <strong>Verde:</strong> Endpoint funcionando correctamente</li>
              <li>❌ <strong>Rojo:</strong> Error CORS - Backend no responde o headers incorrectos</li>
              <li>⚠️ <strong>Amarillo:</strong> Endpoint responde pero con errores (404, 500, etc.)</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};