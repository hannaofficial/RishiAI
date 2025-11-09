export default function GuideLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <div style={{ padding: "8px 16px", background: "#fafafa", borderBottom: "1px solid #eee" }}>
        <strong>Guide</strong> • A calm chat to find your next step 💬
      </div>
      {children}
    </div>
  );
}
