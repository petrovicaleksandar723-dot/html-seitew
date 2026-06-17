import { Component, ReactNode } from "react";

interface Props {
  fallback: ReactNode;
  children: ReactNode;
}

/** Generic error boundary — keeps a WebGL/render failure from blanking the app. */
export class Boundary extends Component<Props, { err: boolean }> {
  state = { err: false };
  static getDerivedStateFromError() {
    return { err: true };
  }
  componentDidCatch(error: unknown) {
    // eslint-disable-next-line no-console
    console.warn("[boundary]", error);
  }
  render() {
    return this.state.err ? this.props.fallback : this.props.children;
  }
}
