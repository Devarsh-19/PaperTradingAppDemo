export interface Quote {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  day_high: number;
  day_low: number;
  timestamp: string;
}

export interface PortfolioSummary {
  portfolio_id: string;
  total_value: number;
  cash_balance: number;
  invested_amount: number;
  today_pnl: number;
  today_pnl_percent: number;
  total_pnl: number;
  total_pnl_percent: number;
}

export interface Position {
  symbol: string;
  quantity: number;
  average_price: number;
  current_price?: number;
  total_value?: number;
  unrealized_pnl?: number;
  unrealized_pnl_percent?: number;
}

export interface Order {
  id: string;
  symbol: string;
  order_type: 'MARKET' | 'LIMIT' | 'STOP_LOSS';
  side: 'BUY' | 'SELL';
  quantity: number;
  limit_price?: number;
  stop_price?: number;
  status: 'OPEN' | 'FILLED' | 'CANCELLED' | 'REJECTED';
  filled_quantity: number;
  average_fill_price?: number;
  created_at: string;
}

export interface Trade {
  id: string;
  order_id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  execution_price: number;
  total_value: number;
  timestamp: string;
}

export interface WatchlistItem {
  symbol: string;
  added_at: string;
  current_price?: number;
  change_percent?: number;
}

export interface LeaderboardEntry {
  user_id: string;
  username: string;
  total_return: number;
  rank: number;
}
