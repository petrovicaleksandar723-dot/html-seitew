import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}
interface State {
  hasError: boolean;
}

/**
 * Guards an optional/enhancement subtree (e.g. the WebGL canvas) so a runtime
 * failure there — WebGL unavailable, context lost, GPU blocked — degrades
 * gracefully instead of taking the whole page down.
 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    // non-fatal: the rest of the experience continues without this subtree
    console.warn("[ErrorBoundary] subtree disabled:", error);
  }

  render() {
    if (this.state.hasError) return this.props.fallback ?? null;
    return this.props.children;
  }
}
