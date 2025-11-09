export default function StoryLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <div style={{ padding: "8px 16px", background: "#fafafa", borderBottom: "1px solid #eee" }}>
        <strong>Story</strong> • Listen and reflect 🌱
      </div>
      {children}
    </div>
  );
}
