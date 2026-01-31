'use client';

interface MacroDataItem {
  label: string;
  value: string;
  change: number;
  changePercent: string;
}

// Mock data for macro indicators
const mockMacroData: MacroDataItem[] = [
  { label: 'DXY', value: '104.25', change: 0.35, changePercent: '+0.34%' },
  { label: 'Gold', value: '$2,042.80', change: 12.40, changePercent: '+0.61%' },
  { label: 'Silver', value: '$23.15', change: -0.28, changePercent: '-1.20%' },
  { label: 'M2 Supply', value: '$20.87T', change: 0.12, changePercent: '+0.58%' },
  { label: 'Fed Funds', value: '5.33%', change: 0, changePercent: '0.00%' },
];

export function MacroTicker() {
  // Duplicate the data for seamless infinite scroll
  const tickerData = [...mockMacroData, ...mockMacroData];

  return (
    <div className="w-full overflow-hidden bg-[#1a1a1a] border-b border-[#2a2a2a]">
      <div className="flex animate-ticker">
        {tickerData.map((item, index) => (
          <div
            key={`${item.label}-${index}`}
            className="flex items-center gap-3 px-6 py-2 whitespace-nowrap"
          >
            <span className="text-[#e8e8e8] text-sm font-medium">
              {item.label}
            </span>
            <span className="font-mono text-sm text-white">
              {item.value}
            </span>
            <span
              className={`font-mono text-sm ${
                item.change > 0
                  ? 'text-green-500'
                  : item.change < 0
                  ? 'text-red-500'
                  : 'text-[#888888]'
              }`}
            >
              {item.changePercent}
            </span>
            {index < tickerData.length - 1 && (
              <span className="text-[#2a2a2a] ml-3">|</span>
            )}
          </div>
        ))}
      </div>

      <style jsx>{`
        @keyframes ticker {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        .animate-ticker {
          animation: ticker 30s linear infinite;
        }
        .animate-ticker:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
}
