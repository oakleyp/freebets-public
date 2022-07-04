/**
 * Asynchronously loads the component for AppBar
 */

import { lazyLoad } from 'utils/loadable';

export const AppBar = lazyLoad(
  () => import('./index'),
  module => module.AppBar,
);
