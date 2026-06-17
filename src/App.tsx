import "./styles/tokens.css";
import "./styles/global.css";
import "./styles/award.css";
import { AppShell } from "./app/AppShell";
import { HomePage } from "./app/HomePage";

export default function App() {
  return (
    <AppShell>
      <HomePage />
    </AppShell>
  );
}
