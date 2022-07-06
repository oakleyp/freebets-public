import { createTheme, Theme as MUITheme } from '@mui/material/styles';

const lightTheme: MUITheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#478ca8',
    },
    secondary: {
      main: '#33dcb8',
    },
  },
});

const darkTheme: MUITheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#478ca8',
      contrastText: '#fff',
    },
    secondary: {
      main: '#33dcb8',
    },
  },
});

export type Theme = typeof lightTheme;

export const themes = {
  light: lightTheme,
  dark: darkTheme,
};
