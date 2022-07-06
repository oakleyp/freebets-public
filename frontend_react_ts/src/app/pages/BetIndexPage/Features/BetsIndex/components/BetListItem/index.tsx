import React from 'react';

import { styled } from '@mui/material/styles';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import Tooltip from '@mui/material/Tooltip';
import Link, { LinkProps } from '@mui/material/Link';
import { AirplaneTicket, FileCopy } from '@mui/icons-material';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Chip from '@mui/material/Chip';
import ListItemButton from '@mui/material/ListItemButton';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import { PostTimer } from 'app/components/PostTimer';
import { getEffectiveTS } from 'utils/bets';

interface BetListItemProps {
  bet: any;
}

function getBetIcon(bet: any): any {
  if (bet.sub_bets) {
    return <FileCopy />;
  }

  return <AirplaneTicket />;
}

function getBetName(bet: any): any {
  if (bet.sub_bets) {
    const uniqTrackCodes = [
      ...new Set(bet.sub_bets.map(bet => bet.race.track_code.toUpperCase())),
    ].join(' | ');

    return `(MULTI) ${uniqTrackCodes}`;
  }

  return bet.race.track_code.toUpperCase();
}

const tagColorMap = {
  'good value': 'primary',
  free: 'warning',
};

function tagColor(tagName: string) {
  return tagColorMap[tagName];
}

function getTags(bet: any): any {
  return (
    <TagsContainer>
      <Stack direction="row" spacing={1}>
        {bet.tags.map(tag => (
          <Tooltip title={tag.description} key={tag.name}>
            <Chip label={tag.name} color={tagColor(tag.name.toLowerCase())} />
          </Tooltip>
        ))}
      </Stack>
    </TagsContainer>
  );
}

const iconMap = {
  ai: {
    tooltip: 'Based on AI odds',
    icon: <PrecisionManufacturingIcon fontSize="small" />,
  },
  book: {
    tooltip: 'Based on book odds',
    icon: <MenuBookIcon fontSize="small" />,
  },
};

const betStratTypeIconMap = {
  'BetStrategyType.AI_ALL_WIN_ARB': iconMap.ai,
  'BetStrategyType.AI_BOX_WIN_ARB': iconMap.ai,
  'BetStrategyType.AI_WIN_BET': iconMap.ai,
  'BetStrategyType.BOOK_ALL_WIN_ARB': iconMap.book,
  'BetStrategyType.BOOK_BOX_WIN_ARB': iconMap.book,
  'BetStrategyType.BOOK_WIN_BET': iconMap.book,
};

function getBetTypeIcons(bet: any): any {
  return [betStratTypeIconMap[bet.bet_strategy_type]]
    .filter(Boolean)
    .map(spec => <Tooltip title={spec.tooltip}>{spec.icon}</Tooltip>);
}

export function BetListItem({ bet }: BetListItemProps) {
  return (
    <Tooltip title="Open play in new tab">
      <StyledListItem component={Link} href={`/bets/${bet.id}`} target="_blank">
        <ListItemAvatar>
          <Avatar>{getBetIcon(bet)}</Avatar>
        </ListItemAvatar>
        <ListItemText
          primary={
            <Stack direction="row" spacing={1}>
              <span>{getBetName(bet)}</span>
              {getBetTypeIcons(bet).map(icon => (
                <span key={icon}>{icon}</span>
              ))}
            </Stack>
          }
          secondary={
            <>
              <Stack direction="row" spacing={1}>
                <span>{`Cost = $${bet.cost.toFixed(2)}`}</span>
                <span>{`Min Reward = $${bet.min_reward.toFixed(2)}`}</span>
                <span>{`Avg. Reward = $${bet.avg_reward.toFixed(2)}`}</span>
                <span>{`Max Reward = $${bet.max_reward.toFixed(2)}`}</span>
                <span>
                  <PostTimer postTime={getEffectiveTS(bet)} />
                </span>
              </Stack>
              {getTags(bet)}
            </>
          }
        />
      </StyledListItem>
    </Tooltip>
  );
}

const StyledListItem = styled(ListItemButton)<
  LinkProps & { component?: React.ElementType }
>(({ theme, ...props }) => ({
  paddingTop: '8px',
  paddingBottom: '16px',
  border: '1px solid',
  margin: '0.5em 0',
  borderRadius: '5px',
  textDecoration: 'none',
  color: theme.palette.primary.dark,
}));

const TagsContainer = styled('div')(({ theme, ...props }) => ({
  paddingTop: '0.4em',
}));
