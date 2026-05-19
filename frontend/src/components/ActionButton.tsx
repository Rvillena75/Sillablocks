import type { ReactNode } from "react";

interface ActionButtonProps {
  children: ReactNode;
  onClick: () => void;
  variant?: "primary" | "soft" | "danger";
  disabled?: boolean;
}

export function ActionButton({ children, onClick, variant = "soft", disabled = false }: ActionButtonProps) {
  return (
    <button className={`action-button ${variant}`} type="button" onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}
