import ChatSection from "../components/ChatSection";
import UploadSection from "../components/UploadSection";

export default function Page() {
  return (
    <main className="page">
      <h1>RAG Test UI</h1>

      <UploadSection />
      <ChatSection />
    </main>
  );
}
