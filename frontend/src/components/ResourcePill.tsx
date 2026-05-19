interface ResourcePillProps {
  label: string;
  value: number;
  tone: "gold" | "blue";
}

export function ResourcePill({ label, value, tone }: ResourcePillProps) {
  return (
    <span className={`resource-pill ${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
    </span>
  );
}

