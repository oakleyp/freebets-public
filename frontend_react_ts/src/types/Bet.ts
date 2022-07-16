export type Race = {
  track_code: string;
  race_number: number;
  race_date: string;
  mtp: number;
  status: string;
  post_time: Date;
  post_time_stamp: number;
  win_pool_total: number;
  place_pool_total: number;
  show_pool_total: number;
};

export type BaseBet = {
  id: number;
  title: string;
  description: string;
  predicted_odds: number;
  min_reward: number;
  avg_reward: number;
  max_reward: number;
  cost: number;
  bet_type: string;
  bet_strategy_type: string;
  tags: string[];
  race: Race;
};

export type SingleBet = BaseBet & {
  active_entries: any[];
  inactive_entries: any[];
};

export type MultiBet = BaseBet & {
  sub_bets: SingleBet[];
};

export function narrowBetType(bet: MultiBet | SingleBet, type: string) {
  const typeMap = {
    single: () => bet as SingleBet,
    multi: () => bet as MultiBet,
  };

  const converter = typeMap[type];

  if (typeof converter !== 'function') {
    throw new TypeError(`Unknown bet type ${type}`);
  }

  return converter();
}

export interface BetsListResponse {
  single_bets: SingleBet[];
  multi_bets: MultiBet[];
  skip: number;
  limit: number;
  track_codes: string[];
  bet_types: string[];
  bet_strat_types: BetStratType[];
  all_track_codes: string[];
  all_bet_strat_types: BetStratType[];
  all_bet_types: string[];
  next_refresh_ts: number;
}

export interface BetViewResponse {
  data: MultiBet | SingleBet;
  result_type: string;
  next_refresh_ts: number;
}

export const ALL_TRACKS = [
  'kee',
  'cd',
  'mrn',
  'sum',
  'btp',
  'sli',
  'pmo',
  'cby',
  'pid',
  'dre',
  'ct',
  'phl',
  'lrl',
  'lad',
  'wo',
  'mx',
  'pln',
  'evg',
  'gg',
  'gp',
  'trv',
  'rui',
  'cml',
  'vd',
  'haw',
  'phl',
  'prm',
  'hst',
  'ls',
  'stg',
  'sa',
  'geo',
  'nfl',
  'pcd',
  'emd',
  'hip',
  'aus',
  'fmt',
  'ace',
  'asd',
  'ded',
  'au1',
  'hop',
  'mnr',
  'grv',
  'z7d',
] as const;

export const ALL_STRATS = [
  'BetStrategyType.BOOK_ALL_WIN_ARB',
  'BetStrategyType.BOOK_BOX_WIN_ARB',
  'BetStrategyType.BOOK_WIN_BET',
] as const;

export type BetStratType = typeof ALL_STRATS[number];
