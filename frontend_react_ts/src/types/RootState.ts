import { ThemeState } from 'styles/theme/slice/types';
import { BetsIndexState } from 'app/pages/HomePage/Features/BetsIndex/slice/types';
// [IMPORT NEW CONTAINERSTATE ABOVE] < Needed for generating containers seamlessly

/*
  Because the redux-injectors injects your reducers asynchronously somewhere in your code
  You have to declare them here manually
*/
export interface RootState {
  theme?: ThemeState;
  betsIndex?: BetsIndexState;
  // [INSERT NEW REDUCER KEY ABOVE] < Needed for generating containers seamlessly
}
