import "./globals.css"; 

export const metadata = {
  title: "Rishi.AI (Demo)",
  description: "Gentle guidance in simple English 💙",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div style={{ borderBottom: "1px solid #eee", padding: "10px 16px" }}>
          <strong>Rishi.AI</strong>
          <span style={{ opacity: 0.7, marginLeft: 8 }}>
            • Express → Story → Guide → Practices → Progress
          </span>
        </div>

        <div style={{ minHeight: "calc(100vh - 48px)" }}>
          {children}
        </div>

        <footer style={{ borderTop: "1px solid #eee", padding: "10px 16px", fontSize: 12, opacity: 0.7 }}>
          Be kind to yourself. Simple steps are enough. 💙
        </footer>
      </body>
    </html>
  );
}
