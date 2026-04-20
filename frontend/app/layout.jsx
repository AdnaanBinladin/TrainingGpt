import "../styles/globals.css";

export const metadata = {
  title: "RAG Test UI",
  description: "Minimal interface for testing file upload and RAG chat.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
