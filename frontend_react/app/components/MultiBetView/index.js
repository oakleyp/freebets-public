import React from 'react';
import { Container, Segment, Table, Label, List, Grid } from 'semantic-ui-react';

function MultiBetView({bet}) {
  return (
    <Container>
      <Segment raised>
        <Grid columns={1}>
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

      {bet.sub_bets.map((sub_bet, i) => (
        <Segment raised key={sub_bet.id}>
          <span>Bet {i+1}</span>
          <Segment raised>
            <span>Race Details</span>
            <List divided>
              <List.Item>
                <Label horizontal>Track:</Label>
                {sub_bet.race.track_code.toUpperCase()}
              </List.Item>
              <List.Item>
                <Label horizontal>Race Number:</Label>
                {sub_bet.race.race_number}
              </List.Item>
              <List.Item>
                <Label horizontal>Race Date:</Label>
                {sub_bet.race.race_date}
              </List.Item>
              <List.Item>
                <Label horizontal>Minutes To Post:</Label>
                {sub_bet.race.mtp}
              </List.Item>
              <List.Item>
                <Label horizontal>Status:</Label>
                {sub_bet.race.status}
              </List.Item>
            </List>
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
                {sub_bet.active_entries.map(entry => (
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
                {sub_bet.inactive_entries.map(entry => (
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
        </Segment>
      ))}

    </Container>
  );
}

export default MultiBetView;
