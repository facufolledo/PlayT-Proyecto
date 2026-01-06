// Script para probar CORS desde la consola del navegador
// Ejecuta esto en la consola de kioskito.click

console.log('🚀 Iniciando pruebas CORS...');

const API_URL = 'https://drive-plus-production.up.railway.app';

// Función para probar un endpoint
async function testEndpoint(url, method = 'GET', body = null) {
    try {
        console.log(`🔍 Probando ${method} ${url}`);
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Origin': window.location.origin
            },
            credentials: 'include' // Importante para CORS con credentials
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(url, options);
        const data = await response.json();
        
        console.log(`✅ ${method} ${url} - Status: ${response.status}`);
        console.log('Response:', data);
        console.log('Headers:', Object.fromEntries(response.headers.entries()));
        
        return { success: true, status: response.status, data };
    } catch (error) {
        console.error(`❌ ${method} ${url} - Error:`, error);
        return { success: false, error: error.message };
    }
}

// Ejecutar pruebas
async function runCorsTests() {
    console.log('🌐 Origin:', window.location.origin);
    console.log('🎯 API URL:', API_URL);
    
    // Prueba 1: Health check
    await testEndpoint(`${API_URL}/health`);
    
    // Prueba 2: CORS test endpoint
    await testEndpoint(`${API_URL}/api/test-cors`);
    
    // Prueba 3: Debug CORS
    await testEndpoint(`${API_URL}/debug/cors`);
    
    // Prueba 4: Root endpoint
    await testEndpoint(`${API_URL}/`);
    
    // Prueba 5: POST request (más complejo para CORS)
    await testEndpoint(`${API_URL}/api/test-cors`, 'POST', { test: true });
    
    console.log('🏁 Pruebas CORS completadas');
}

// Ejecutar las pruebas
runCorsTests();

// También exportar función para uso manual
window.testCors = runCorsTests;
window.testEndpoint = testEndpoint;

console.log('💡 Puedes ejecutar testCors() o testEndpoint(url) manualmente');