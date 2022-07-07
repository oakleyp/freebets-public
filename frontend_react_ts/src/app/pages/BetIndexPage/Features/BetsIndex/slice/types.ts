import { SingleBet, MultiBet, BetStratType } from 'types/Bet';

export const BET_LABELS = {
  'BetType.ALL_WIN_ARB': 'All Win',
  'BetType.BOX_WIN_ARB': '(Multi) Box Win',
  'BetType.WIN_BET': 'Win',
};

export type BetsIndexState = {
  loading: boolean;
  error?: BetsErrorType | null;
  availableFilterValues: AvailableBetFilterValues;
  currentBetSearchParams: BetSearchParams;
  currentBetList: BetList;
  selectedBet?: SingleBet | MultiBet | null;
  nextRefreshTs?: number | null;
  countdownRefreshEnabled: boolean;
};

export type BetList = {
  singleBets: any[];
  multiBets: any[];
};

export type BetSearchParams = {
  betTypes?: string[] | null;
  betStratTypes?: BetStratType[] | null;
  limit: number;
  skip: number;
  trackCodes: Array<string>;
};

export type AvailableBetFilterValues = {
  trackCodes: string[];
  betStratTypes: string[];
  betTypes: string[];
};

export enum BetsErrorType {
  RESPONSE_ERROR = 1,
  NO_BETS_ERROR = 2,
}
