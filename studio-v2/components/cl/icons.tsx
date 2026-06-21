import type { SVGProps } from "react";

type IconName =
  | "play"
  | "pen"
  | "globe"
  | "star"
  | "calendar"
  | "bulb"
  | "spark"
  | "growth"
  | "crown"
  | "browser"
  | "share"
  | "check"
  | "mark"
  | "arrow";

const DEFS: Record<IconName, { vb: string; sw: number; body: JSX.Element }> = {
  play: {
    vb: "0 0 24 24",
    sw: 1.8,
    body: (
      <>
        <rect x="3" y="3.5" width="18" height="17" rx="4.5" />
        <path d="M10 8.5l5.5 3.5-5.5 3.5z" fill="currentColor" stroke="none" />
      </>
    ),
  },
  pen: {
    vb: "0 0 24 24",
    sw: 1.8,
    body: (
      <>
        <path d="M4 20h4L19 9a2.1 2.1 0 0 0-3-3L5 17z" />
        <path d="M14.5 7.5l3 3" />
      </>
    ),
  },
  globe: {
    vb: "0 0 24 24",
    sw: 1.8,
    body: (
      <>
        <circle cx="12" cy="12" r="8.5" />
        <path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17" />
      </>
    ),
  },
  star: {
    vb: "0 0 24 24",
    sw: 1.8,
    body: <path d="M12 3.6l2.5 5 5.5.8-4 3.9.95 5.5L12 16.2 7.05 18.8 8 13.3l-4-3.9 5.5-.8z" />,
  },
  calendar: {
    vb: "0 0 24 24",
    sw: 1.8,
    body: (
      <>
        <rect x="3.5" y="5" width="17" height="15.5" rx="3" />
        <path d="M3.5 9.5h17M8 3.5v3.5M16 3.5v3.5M7.5 13.5h4M7.5 17h7" />
      </>
    ),
  },
  bulb: {
    vb: "0 0 24 24",
    sw: 1.9,
    body: (
      <path
        d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.5.4.5.8.5 1.6h6c0-.8 0-1.2.5-1.6A6 6 0 0 0 12 3z"
        fill="currentColor"
        stroke="none"
      />
    ),
  },
  spark: {
    vb: "0 0 24 24",
    sw: 1.8,
    body: <path d="M12 4l1.7 5L19 11l-5.3 1.8L12 18l-1.7-5.2L5 11l5.3-2z" fill="currentColor" stroke="none" />,
  },
  growth: {
    vb: "0 0 24 24",
    sw: 1.9,
    body: (
      <>
        <path d="M4 19h16" />
        <path d="M5 15l4-4 3 3 6-6.5" />
        <path d="M14.5 7.5H19V12" />
      </>
    ),
  },
  crown: {
    vb: "0 0 24 24",
    sw: 1.7,
    body: (
      <>
        <path d="M4 17.5h16l1-9-5 3.5L12 5.5 8 12 3 8.5z" fill="currentColor" stroke="none" />
        <path d="M4 20h16" />
      </>
    ),
  },
  browser: {
    vb: "0 0 24 24",
    sw: 1.8,
    body: (
      <>
        <rect x="3" y="4.5" width="18" height="15" rx="3" />
        <path d="M3 9.5h18" />
      </>
    ),
  },
  share: {
    vb: "0 0 24 24",
    sw: 1.8,
    body: (
      <>
        <circle cx="6.5" cy="12" r="2.5" />
        <circle cx="17" cy="6.5" r="2.5" />
        <circle cx="17" cy="17.5" r="2.5" />
        <path d="M8.7 10.8l6-3.2M8.7 13.2l6 3.2" />
      </>
    ),
  },
  check: {
    vb: "0 0 24 24",
    sw: 2,
    body: (
      <>
        <circle cx="12" cy="12" r="10" />
        <path d="M7.5 12.5l3 3 6-6.5" />
      </>
    ),
  },
  arrow: {
    vb: "0 0 24 24",
    sw: 2,
    body: <path d="M5 12h14M13 6l6 6-6 6" />,
  },
  mark: {
    vb: "0 0 100 100",
    sw: 3,
    body: (
      <g strokeLinejoin="round" strokeLinecap="round">
        <polygon points="50,6 88.1,28 88.1,72 50,94 11.9,72 11.9,28" />
        <polygon points="50,17 78.6,33.5 78.6,66.5 50,83 21.4,66.5 21.4,33.5" opacity=".8" />
        <polygon points="50,28 69,39 69,61 50,72 31,61 31,39" opacity=".58" />
        <path d="M50,50 L50,6 M50,50 L11.9,72 M50,50 L88.1,72" />
      </g>
    ),
  },
};

export function Icon({
  name,
  ...props
}: { name: IconName } & SVGProps<SVGSVGElement>) {
  const d = DEFS[name];
  return (
    <svg
      viewBox={d.vb}
      fill="none"
      stroke="currentColor"
      strokeWidth={d.sw}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {d.body}
    </svg>
  );
}

export type { IconName };
