"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const linkClass = (path: string) =>
    `block px-4 py-3 rounded-lg mb-2 ${
      pathname === path
        ? "bg-blue-600 text-white font-semibold"
        : "text-gray-700 hover:bg-gray-200"
    }`;

  return (
    <aside className="w-64 bg-white shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6">InfraPilot</h2>

      <nav>
        <Link href="/" className={linkClass("/")}>
          Home
        </Link>
        <Link href="/pipeline" className={linkClass("/pipeline")}>
          Pipeline
        </Link>
        <Link href="/projects" className={linkClass("/projects")}>
          Projects
        </Link>
        <Link href="/settings" className={linkClass("/settings")}>
          Settings
        </Link>
      </nav>
    </aside>
  );
}
