import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';
import React from 'react';

export function Copyright(props: any) {
  return (
    <Typography
      variant="body2"
      color="text.secondary"
      align="center"
      {...props}
    >
      {'Copyright © '}
      <Link color="inherit" href="https://oakleypeavler.com/">
        Oakley Peavler
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
      &nbsp; | &nbsp;
      {'Documentation and code on '}
      <Link color="inherit" href="https://github.com/oakleyp/freebets-public">
        GitHub
      </Link>
    </Typography>
  );
}
