import type { Metadata } from 'next';
import { Bebas_Neue, JetBrains_Mono, Source_Serif_4 } from 'next/font/google';
import './globals.css';

const bebasNeue = Bebas_Neue({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-bebas',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains',
  display: 'swap',
});

const sourceSerif = Source_Serif_4({
  subsets: ['latin'],
  variable: '--font-source-serif',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'HEDGE - Dollar Devaluation Protection',
  description: 'Score stocks on their resilience to US dollar devaluation. Stress-test your portfolio against currency collapse scenarios.',
  keywords: ['stocks', 'investing', 'dollar', 'devaluation', 'inflation', 'hedge', 'gold', 'commodities'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${bebasNeue.variable} ${jetbrainsMono.variable} ${sourceSerif.variable}`}
    >
      <body className="min-h-screen bg-black antialiased font-serif">
        {children}
      </body>
    </html>
  );
}
