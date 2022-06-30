import React from 'react';
import { Container, Segment, Table, Label, List, Grid } from 'semantic-ui-react';

function SingleBetView({bet}) {
  return (
    <Container>
      <Segment raised>
        <Grid columns={2}>
          <Grid.Column>
            <span>Race Details</span>
            <List divided>
              <List.Item>
                <Label horizontal>Track:</Label>
                {bet.race.track_code.toUpperCase()}
              </List.Item>
              <List.Item>
                <Label horizontal>Race Number:</Label>
                {bet.race.race_number}
              </List.Item>
              <List.Item>
                <Label horizontal>Race Date:</Label>
                {bet.race.race_date}
              </List.Item>
              <List.Item>
                <Label horizontal>Minutes To Post:</Label>
                {bet.race.mtp}
              </List.Item>
              <List.Item>
                <Label horizontal>Status:</Label>
                {bet.race.status}
              </List.Item>
            </List>
          </Grid.Column>
          <Grid.Column>
            <span>Bet Details</span>
            <List divided>
              <List.Item>
                <Label horizontal>Predicted Odds:</Label>
                {bet.predicted_odds}
              </List.Item>
              <List.Item>
                <Label horizontal>Min Reward:</Label>
                ${bet.min_reward.toFixed(2)}
              </List.Item>
              <List.Item>
                <Label horizontal>Avg Reward:</Label>
                ${bet.avg_reward.toFixed(2)}
              </List.Item>
              <List.Item>
                <Label horizontal>Max Reward:</Label>
                ${bet.max_reward.toFixed(2)}
              </List.Item>
              <List.Item>
                <Label horizontal>Cost:</Label>
                ${bet.cost}
              </List.Item>
              <List.Item>
                <Label horizontal>Bet Type:</Label>
                {bet.bet_type}
              </List.Item>
              <List.Item>
                <Label horizontal>Bet Strategy:</Label>
                {bet.bet_strategy_type}
              </List.Item>
            </List>
          </Grid.Column>
        </Grid>
      </Segment>

      <Segment raised>
        <Label>Active Entries</Label>
        <Table celled striped>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Program No.</Table.HeaderCell>
              <Table.HeaderCell>Horse</Table.HeaderCell>
              <Table.HeaderCell>Odds</Table.HeaderCell>
              <Table.HeaderCell>AI Odds</Table.HeaderCell>
            </Table.Row>
          </Table.Header>

          <Table.Body>
            {bet.active_entries.sort((a, b) => a.ai_predicted_odds - b.ai_predicted_odds).map(entry => (
              <Table.Row>
                <Table.Cell>{entry.program_no}</Table.Cell>
                <Table.Cell>{entry.name}</Table.Cell>
                <Table.Cell>{entry.odds}</Table.Cell>
                <Table.Cell>{entry.ai_predicted_odds}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </Segment>

      <Segment raised>
        <Label>Inactive Entries</Label>
        <Table celled striped>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Program No.</Table.HeaderCell>
              <Table.HeaderCell>Horse</Table.HeaderCell>
              <Table.HeaderCell>Odds</Table.HeaderCell>
              <Table.HeaderCell>AI Odds</Table.HeaderCell>
            </Table.Row>
          </Table.Header>

          <Table.Body>
            {bet.inactive_entries.map(entry => (
              <Table.Row>
                <Table.Cell>{entry.program_no}</Table.Cell>
                <Table.Cell>{entry.name}</Table.Cell>
                <Table.Cell>{entry.odds}</Table.Cell>
                <Table.Cell>{entry.ai_predicted_odds}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </Segment>
    </Container>
  );
}

export default SingleBetView;
