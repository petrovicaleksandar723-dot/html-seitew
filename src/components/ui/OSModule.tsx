import { LucideIcon } from "lucide-react";

export function OSModule({
  label,
  icon: Icon,
  active,
  onActivate,
}: {
  label: string;
  icon: LucideIcon;
  active: boolean;
  onActivate: () => void;
}) {
  return (
    <button
      type="button"
      className={`os-app ${active ? "active" : ""}`}
      onMouseEnter={onActivate}
      onFocus={onActivate}
      onClick={onActivate}
    >
      <span className="os-app-ic">
        <Icon size={19} strokeWidth={1.7} />
      </span>
      <span className="os-app-l">{label}</span>
    </button>
  );
}
