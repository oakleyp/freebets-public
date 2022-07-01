# Batteries

There are two aspects of this project that, due to copywright law, I have to leave to the imagination of the reader. Implementing just `Live Racing` will allow this to be used as a technical betting platform, but in order to use predictive betting, both of the following are needed.

## Live Racing

\- `backend/app/app/lib/clients/live_abstract.py`  
You will need to implement the `AbstractLiveRacingClient` and `AbstractLiveRacingClientException` interfaces provided. Callers of this client will expect instances of the exception class on known errors.

\- `backend/app/app/raceday/processor.py`  
In the `RaceDayProcessor` class, replace references to `LiveRacingClient` with your newly implemented class.

## Historical Racing

Compared to the Live Racing set up, this will require a substantial amount of work. I may find a way to better decouple the copywright-sensitive portions of the code in the future, but currently the codebase is not quite mature enough for the level of abstraction that would make this easier.

### 1. Implement the Historical Client interface

\- `backend/app/app/lib/clients/historical_abstract.py`  
Similar to the live racing client, you will need to implement the `AbstractHistoricalRacingClient` and its `AbstractHistoricalRacingClientException` class. This is essentially just a PDF download, so it should be much easier at this stage.

\- `backend/app/app/ml/race_results_proc.py`  
In the `RaceResultsProcessor` class, replace references to `HistoricalRacingClient` with your newly implemented class.

### 2. RMQ Listener & PDF Parser

After you have implemented the `HistoricalRacingClient`, the `RaceResultProcessor` will be using it to download past races and publish messages to RabbitMQ, signaling that these races are ready for parsing/ingest.

At this point, you need to build a RMQ listener service that can reach both Clickhouse and RabbitMQ inside the container network. This service needs to receive the `IngestSignal` JSON sent from the `RaceResultProcessor` side, parse the PDF specified, and upload the resulting race data to the Clickhouse DB. 

\- `backend/app/app/ml/clickhouse_pd.py`  
The Clickhouse DB table schemas need to match the schema used by `get_complete_race_df()` in this file, and the data must be both worked into the Jupyter Notebook in that same folder, and munged properly so that it aligns with the live racing data that the trained model will be run against. 

This area is the most active part of the codebase at the time of writing, and this will make any details that I expand on obsolete too quickly to keep up to date. I don't really expect anyone to actually go through with implementing this completely at this point. If you are determined and capable enough to complete the above steps, you will probably prefer building your own solution to fit the platform rather than recreate my process step-by-step.
