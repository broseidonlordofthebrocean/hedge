'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    { href: '/rankings', label: 'Rankings' },
    { href: '/screener', label: 'Screener' },
    { href: '/portfolio', label: 'Portfolio' },
  ];

  return (
    <header className="bg-black border-b border-[#d4a853]/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="font-display text-2xl font-bold text-[#d4a853]">
            HEDGE
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-[#e8e8e8] hover:text-[#d4a853] transition-colors duration-200"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Sign In Button (Desktop) */}
          <div className="hidden md:block">
            <Link
              href="/sign-in"
              className="px-4 py-2 border border-[#d4a853] text-[#d4a853] hover:bg-[#d4a853] hover:text-black transition-colors duration-200 rounded"
            >
              Sign In
            </Link>
          </div>

          {/* Mobile Hamburger Menu Button */}
          <button
            type="button"
            className="md:hidden p-2 text-[#e8e8e8] hover:text-[#d4a853] transition-colors duration-200"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
            aria-expanded={isMobileMenuOpen}
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {isMobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-[#d4a853]/20">
            <nav className="py-4 space-y-2">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="block px-4 py-2 text-[#e8e8e8] hover:text-[#d4a853] hover:bg-[#d4a853]/10 transition-colors duration-200"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
              <Link
                href="/sign-in"
                className="block mx-4 mt-4 px-4 py-2 border border-[#d4a853] text-[#d4a853] hover:bg-[#d4a853] hover:text-black transition-colors duration-200 rounded text-center"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Sign In
              </Link>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
