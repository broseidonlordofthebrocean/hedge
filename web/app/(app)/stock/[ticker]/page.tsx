import StockClient from "./StockClient";

export function generateStaticParams() {
  return [
    { ticker: "NEM" },
    { ticker: "GOLD" },
    { ticker: "XOM" },
    { ticker: "CVX" },
    { ticker: "FCX" },
    { ticker: "BHP" },
    { ticker: "AAPL" },
    { ticker: "MSFT" },
  ];
}

export default function StockDetailPage({ params }: { params: { ticker: string } }) {
  return <StockClient ticker={params.ticker} />;
}
