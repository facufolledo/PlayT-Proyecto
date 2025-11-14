import { Component, ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';
import Button from './Button';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    // En producción, aquí enviarías el error a un servicio como Sentry
    console.error('Error capturado por ErrorBoundary:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <div className="bg-cardBg rounded-2xl p-8 border border-cardBorder shadow-2xl max-w-md w-full">
            <div className="flex flex-col items-center text-center">
              <div className="bg-red-500/10 p-4 rounded-full mb-4">
                <AlertTriangle className="text-red-500" size={48} />
              </div>
              
              <h2 className="text-2xl font-bold text-textPrimary mb-2">
                ¡Oops! Algo salió mal
              </h2>
              
              <p className="text-textSecondary mb-6">
                Ha ocurrido un error inesperado. Por favor, recarga la página o intenta más tarde.
              </p>

              {this.state.error && import.meta.env.DEV && (
                <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-4 mb-6 w-full">
                  <p className="text-red-500 text-xs font-mono text-left break-all">
                    {this.state.error.message}
                  </p>
                </div>
              )}

              <div className="flex gap-3 w-full">
                <Button
                  onClick={() => window.history.back()}
                  variant="ghost"
                  className="flex-1"
                >
                  Volver
                </Button>
                <Button
                  onClick={this.handleReload}
                  variant="primary"
                  className="flex-1"
                >
                  Recargar página
                </Button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
