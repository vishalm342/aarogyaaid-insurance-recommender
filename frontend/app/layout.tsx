import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist" });

export const metadata: Metadata = {
  title: "AarogyaAid — Smart Insurance Recommender",
  description: "AI-powered health insurance recommendations tailored for you",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={geist.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}