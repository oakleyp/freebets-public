# Architecture

## Core Concepts

*Bets*

In this platform, the main output is the `Bet`, a structure that describes:
- The race date, number, and track that this bet can be placed
- The type of bet, whether standard (Win, Place, Show) exotic (trifecta, exacta, tri-box, etc.)
- The cost and min/max/average return of the bet
- The `entries`, or horses in the race, and whether they are selected in the bet or not

Bets can either bet `SingleBets`, where in the real world they would be equivalent to one betting slip, or `MultiBets`, which describe multiple betting slips across a range of races, or targetting a single race. For a `MultiBet`, there is an overarching `root` bet that aggregates the cost/return of all `sub_bets`.

In the current design, bets are ephemeral, and are deleted and regenerated every time the live racing data is updated. This is due to the fact that live odds change constantly up to seconds before the race, and what was a good bet at one minute may not be in the next. As a result, it doesn't seem useful at this point to go to the effort of supporting partial bet updates, since this would add a lot of complexity and the generation process is relatively inexpensive, although this may change in the future.

*Entries/Starters*

These terms are used somewhat interchangeably, but refer to the horses in the race that are included in a bet. An `Entry` holds all the significant data that is available from the live racing source, including:
- The horse's name, number, weight, jockey, trainer
- The horse's book odds
- The horse's predicted win probability
- The horse's last race

*Bet Tags*

These are a list of tags attached to each bet that allow for filtering of bets based on certain conditions computed at the time the bet is generated. Currently, the defined tags are:
- `Good Value` - for bets where the average return is greater than the cost of the bet
- `Free` - for bets where the minimum return is greater than the cost of the bet

## Real-time Race Processing Control Flow

```mermaid
sequenceDiagram
    participant LiveDataSource
    participant RaceDayProcessor
    participant PostgresDB
    participant RacePredictor
    RaceDayProcessor->>PostgresDB: Clear Bets in Configured Lookahead Window
    RaceDayProcessor->>LiveDataSource: Fetch Race List
    LiveDataSource-->>RaceDayProcessor: 
    loop For each race
    RaceDayProcessor->>LiveDataSource: Fetch Race Entries
    LiveDataSource-->>RaceDayProcessor: 
    end
    RaceDayProcessor->>RacePredictor: Apply Trained Model Predictions to Race Entries
    RacePredictor-->>RaceDayProcessor: 
    RaceDayProcessor->>RaceDayProcessor: Generate Bets and Tags
    RaceDayProcessor->>PostgresDB: Save Bets and Tags
    RaceDayProcessor->>RaceDayProcessor: Sleep until Next Check Time
```

## Historical Race Training Control Flow

Stage 1:

```mermaid
sequenceDiagram
    participant HistoricalDataSource
    participant DownloadWorker
    participant RabbitMQ
    participant Parser
    participant ClickhouseDB
    loop For each Track in Configured Search:
    DownloadWorker->>HistoricalDataSource: Download Chart
    HistoricalDataSource-->>DownloadWorker: 
    DownloadWorker->>RabbitMQ: Send IngestSignal with File Path
    end
    loop Forever
    Parser->>RabbitMQ: Listen for latest IngestSignal
    RabbitMQ-->>Parser: 
    Parser-->>Parser: Read File & Parse data
    Parser->>ClickhouseDB: Store data
    end
```

Stage 2 (as of now, this will be automated once the training method is better defined):

```mermaid
sequenceDiagram
    participant Me
    participant JupyterNotebook
    participant ClickhouseDB
    Me->>JupyterNotebook: Create Training/Test Sets from Clickhouse
    JupyterNotebook->>ClickhouseDB: Fetch Race/Entry Data
    ClickhouseDB-->>JupyterNotebook: 
    Me->>JupyterNotebook: Train Catboost Model
    Me->>JupyterNotebook: Save Catboost Model
```

## API/UI Flow

```mermaid
sequenceDiagram
    participant UI
    participant API
    UI->>API: Fetch & Paginate Bet List
    API-->>UI: 
    UI-->>UI: Select Bet to View
    UI->>API: Fetch Complete Bet Details
    API-->>UI: 
```
