import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { LearnerProvider } from '../context/LearnerContext';
import { CoachProvider } from '../context/CoachContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'SkillPath AI — Evidence-Driven Data Science Career Platform',
  description:
    'SkillPath AI is an evidence-driven Data Science career learning platform. The learner does not follow the roadmap; the roadmap follows the learner.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-slate-50/70 antialiased">
      <body className={`${inter.className} min-h-full flex flex-col`}>
        <LearnerProvider>
          <CoachProvider>{children}</CoachProvider>
        </LearnerProvider>
      </body>
    </html>
  );
}
