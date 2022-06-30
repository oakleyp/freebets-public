/**
 * RepoListItem
 *
 * Lists the name and the issue count of a repository
 */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { createStructuredSelector } from 'reselect';
import { FormattedNumber } from 'react-intl';

import ListItem from 'components/ListItem';
import IssueIcon from './IssueIcon';
import IssueLink from './IssueLink';
import RepoLink from './RepoLink';
import Wrapper from './Wrapper';
import { Label } from 'semantic-ui-react';
import PostTimer from 'components/PostTimer';
import { getEffectiveTS } from 'utils/bets';

const TAG_COLOR = {
  free: 'red',
  'good value': 'green',
};

export function BetsListItem(props) {
  const { item } = props;

  const tagContent = item.tags.length ?
  (
    <>
      {item.tags.map(tag => (
        <React.Fragment key={tag.id}>
          &nbsp;
          <Label color={TAG_COLOR[tag.name.toLowerCase()]} horizontal title={tag.description}>{tag.name}</Label>
        </React.Fragment>
      ))}
    </>
  ) : null;

  const descLabels = [
    <Label horizontal>Cost: ${item.cost}</Label>,
    <Label horizontal>Max: ${item.max_reward.toFixed(2)}</Label>,
    <Label horizontal>Avg: ${item.avg_reward.toFixed(2)}</Label>,
    <Label horizontal>Min: ${item.min_reward.toFixed(2)}</Label>,
    <PostTimer postTime={getEffectiveTS(item)} />,
  ];

  const getTitlePrefix = item => {
    if (item.sub_bets) {
      const uniqTrackCodes = [
        ...new Set(
          item.sub_bets.map(bet => bet.race.track_code.toUpperCase())
        )
      ].join(" | ");

      return `(MULTI) ${uniqTrackCodes}`;
    }

    return item.race.track_code.toUpperCase()
  }

  const title = <>{getTitlePrefix(item)} -&nbsp;{descLabels}</>

  // Put together the content of the repository
  const content = (
    <Wrapper>
      <RepoLink href={`/bets/${item.id}`} target="_blank">
        {title} {tagContent}
      </RepoLink>
      {/* <IssueLink href={`${item.html_url}/issues`} target="_blank">
        <IssueIcon />
        <FormattedNumber value={item.open_issues_count} />
      </IssueLink> */}
    </Wrapper>
  );

  // Render the content into a list item
  return <ListItem key={`repo-list-item-${item.title}`} item={content} />;
}

BetsListItem.propTypes = {
  item: PropTypes.object,
  currentUser: PropTypes.string,
};

export default BetsListItem;
