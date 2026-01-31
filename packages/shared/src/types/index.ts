/**
 * Represents a company with its fundamental data and scoring
 */
export interface Company {
  id: string;
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  market_cap: number;
  score: number;
  tier: string;
}

/**
 * Represents the scoring breakdown for a company
 */
export interface Score {
  total_score: number;
  factors: {
    [key: string]: number;
  };
  scenario_scores: {
    [scenario: string]: number;
  };
  tier: string;
  confidence: number;
}

/**
 * Represents a holding within a portfolio
 */
export interface Holding {
  company_id: string;
  ticker: string;
  shares: number;
  cost_basis: number;
  current_value: number;
}

/**
 * Represents a portfolio with its holdings and metrics
 */
export interface Portfolio {
  id: string;
  name: string;
  holdings: Holding[];
  total_value: number;
  survival_score: number;
}

/**
 * Represents macroeconomic indicator data
 */
export interface MacroData {
  dxy: number;
  gold: number;
  silver: number;
  m2: number;
  fed_funds: number;
  ten_year: number;
}
