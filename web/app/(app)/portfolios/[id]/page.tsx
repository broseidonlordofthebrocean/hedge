import PortfolioClient from "./PortfolioClient";

export function generateStaticParams() {
  return [
    { id: "1" },
    { id: "2" },
    { id: "3" },
  ];
}

export default function PortfolioDetailPage({ params }: { params: { id: string } }) {
  return <PortfolioClient id={params.id} />;
}
