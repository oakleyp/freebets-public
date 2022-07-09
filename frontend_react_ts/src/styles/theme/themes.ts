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
    background: {
      default: '#f5f5f5',
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
    background: {
      default: '#212121',
    },
  },
});

export type Theme = typeof lightTheme;

export const themes = {
  light: lightTheme,
  dark: darkTheme,
};
