import * as React from 'react';
import { ThemeProvider as OriginalThemeProvider } from '@mui/material/styles';

import { useSelector } from 'react-redux';
import { useThemeSlice } from './slice';
import { selectTheme } from './slice/selectors';

export const ThemeProvider = (props: { children: React.ReactChild }) => {
  useThemeSlice();

  const theme = useSelector(selectTheme);

  return (
    <OriginalThemeProvider theme={theme}>
      {React.Children.only(props.children)}
    </OriginalThemeProvider>
  );
};
