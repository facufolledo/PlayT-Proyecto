import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Salas from './pages/Salas';
import Torneos from './pages/Torneos';
import TorneoDetalle from './pages/TorneoDetalle';
import Estadisticas from './pages/Estadisticas';
import Rankings from './pages/Rankings';
import Confirmaciones from './pages/Confirmaciones';
import MiPerfil from './pages/MiPerfil';
import Login from './pages/Login';
import Register from './pages/Register';
import PrivateRoute from './components/PrivateRoute';
import { ErrorBoundary } from './components/ErrorBoundary';
import { AuthProvider } from './context/AuthContext';
import { SalasProvider } from './context/SalasContext';
import { TorneosProvider } from './context/TorneosContext';

// La Landing siempre es accesible, incluso si estás autenticado
// El usuario decide cuándo entrar a la app

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <SalasProvider>
            <TorneosProvider>
              <Routes>
              {/* Ruta principal - Landing siempre visible */}
              <Route path="/" element={<Landing />} />

              {/* Rutas públicas */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Rutas protegidas */}
              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <Layout>
                      <Dashboard />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/salas"
                element={
                  <PrivateRoute>
                    <Layout>
                      <Salas />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/torneos"
                element={
                  <PrivateRoute>
                    <Layout>
                      <Torneos />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/torneos/:id"
                element={
                  <PrivateRoute>
                    <Layout>
                      <TorneoDetalle />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/estadisticas"
                element={
                  <PrivateRoute>
                    <Layout>
                      <Estadisticas />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/rankings"
                element={
                  <PrivateRoute>
                    <Layout>
                      <Rankings />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/rankings/categorias"
                element={
                  <PrivateRoute>
                    <Layout>
                      <div className="text-textPrimary">Rankings por Categoría - Próximamente</div>
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/rankings/mi-ranking"
                element={
                  <PrivateRoute>
                    <Layout>
                      <div className="text-textPrimary">Mi Ranking - Próximamente</div>
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/salas/programados"
                element={
                  <PrivateRoute>
                    <Layout>
                      <div className="text-textPrimary">Partidos Programados - Próximamente</div>
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/salas/confirmaciones"
                element={
                  <PrivateRoute>
                    <Layout>
                      <Confirmaciones />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/torneos/mis-torneos"
                element={
                  <PrivateRoute>
                    <Layout>
                      <div className="text-textPrimary">Mis Torneos - Próximamente</div>
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/perfil"
                element={
                  <PrivateRoute>
                    <Layout>
                      <MiPerfil />
                    </Layout>
                  </PrivateRoute>
                }
              />
              <Route
                path="/configuracion"
                element={
                  <PrivateRoute>
                    <Layout>
                      <div className="text-textPrimary">Configuración - Próximamente</div>
                    </Layout>
                  </PrivateRoute>
                }
              />

              {/* Ruta 404 */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </TorneosProvider>
        </SalasProvider>
      </AuthProvider>
    </Router>
    </ErrorBoundary>
  );
}

export default App;
