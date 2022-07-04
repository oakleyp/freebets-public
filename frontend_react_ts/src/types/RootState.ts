import { ThemeState } from 'styles/theme/slice/types';
import { BetsIndexState } from 'app/pages/HomePage/Features/BetsIndex/slice/types';
import { BetViewState } from 'app/pages/BetViewPage/Features/BetView/slice/types';
// [IMPORT NEW CONTAINERSTATE ABOVE] < Needed for generating containers seamlessly

/*
  Because the redux-injectors injects your reducers asynchronously somewhere in your code
  You have to declare them here manually
*/
export interface RootState {
  theme?: ThemeState;
  betsIndex?: BetsIndexState;
  betView?: BetViewState;
  // [INSERT NEW REDUCER KEY ABOVE] < Needed for generating containers seamlessly
}
