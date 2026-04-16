export function Button({ title, transparent, color = "blue", onClick }: { 
  title: string; 
  transparent?: boolean;
  color?: string;
  onClick: () => void;
}) {
  return transparent ? (
    <button
      onClick={onClick}
      style={{ borderColor: color, color: color }}
      className="border-2 rounded-md px-4 py-2 hover:opacity-70 transition-opacity font-bold cursor-pointer"
    >
      {title}
    </button>
  ) : (
    <button
      onClick={onClick}
      style={{ backgroundColor: color }}
      className="text-white px-4 py-2 rounded-md hover:opacity-70 transition-all font-bold cursor-pointer"
    >
      {title}
    </button>
  );
}
export default Button