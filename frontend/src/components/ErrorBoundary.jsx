import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary]', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="glass-card p-5 text-center space-y-3">
          <div className="text-red-400 text-xl font-bold">⚠️ Component Error</div>
          <p className="text-gray-400 text-sm">
            {this.props.fallbackMessage || 'Something went wrong rendering this panel.'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="px-4 py-2 rounded bg-quantum-600 text-white text-xs hover:bg-quantum-500 transition"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
