import { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Button from './Button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error capturado por ErrorBoundary:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-background">
          <div className="max-w-md w-full bg-cardBg rounded-2xl p-8 border border-cardBorder text-center">
            <div className="bg-red-500/10 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
              <AlertTriangle size={40} className="text-red-500" />
            </div>
            
            <h2 className="text-2xl font-black text-textPrimary mb-3">
              Algo salió mal
            </h2>
            
            <p className="text-textSecondary mb-6">
              Ha ocurrido un error inesperado. Por favor, intenta recargar la página.
            </p>

            {this.state.error && (
              <div className="bg-background rounded-lg p-4 mb-6 text-left">
                <p className="text-xs text-red-400 font-mono break-all">
                  {this.state.error.message}
                </p>
              </div>
            )}

            <Button
              variant="primary"
              onClick={this.handleReset}
              className="w-full flex items-center justify-center gap-2"
            >
              <RefreshCw size={18} />
              Recargar página
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
