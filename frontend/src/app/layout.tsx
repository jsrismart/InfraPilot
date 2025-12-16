import "./globals.css";
import Sidebar from "../components/Sidebar";

export const metadata = {
  title: "InfraPilot",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-100">
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <Sidebar />

          {/* Main content */}
          <div className="flex-1 p-8">{children}</div>
        </div>
      </body>
    </html>
  );
}
