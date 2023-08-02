# Project Goal

Develop a simple command line application that parses a stream of events and produces an aggregated output (in the form of the `average_delivery_time.json` file). In this case, we're interested in calculating, for every minute, a moving average of the translation delivery time for the last X minutes.

# Solution Overview

### Requirements

This project was implemented using `Python 3.11.4` and the following Python packages:

+ Click - To define the command and its options;
+ json - To read the events from the input file;
+ Pandas - To easily save, clean, and process the events.

### Logic

The `maverage` command, linked to the function `process_events`, is executed in four steps:

1. Load and clean events - `get_clean_data()`
2. Process the events - `enhance_data()`
3. Compute moving average - `moving_average()`
4. Output - `output_result()`

In step 1, the input file is read one line at a time (empty ones are ignored) and only the `timestamp` and `duration` of **valid events** are added to the clean dataset. An event is _valid_ if it is of the type `translation_delivered` and if it contains the two properties mentioned above. It is assumed that, whenever present, these values are properly formatted.

Moreover, the timestamps that are kept are not the ones receives as input.
In fact, unless an event happened at an exact minute (eg. `"2018-12-26 18:25:00.000000"`) its `timestamp` is rounded to the next one:
`18:11:08.509654` -> `18:12:00.000000`

Next, the column `delta_ts` is added to the clean dataset. It contains the difference (in minutes) between each timestamp and the one that preceeds it.
This information is of use step 3.

Unsurprisingly, `moving_average()` computes the moving average for the `duration` field of the events received as input. I am considering that whenever no events were registered in a window, the `average_delivery_time` for the corresponding minute is `0`.

In addition, the moving average is always computed for the interval `[minT-1, maxT]`, even if a window size that is greater than the time range of the events received is provided. Here `minT` and `maxT` are the `timestamp` for the oldest and newest events respectively (after being processed in step 2, as mentioned above).

Finaly, the list with the resulting datapoints is written to the file `average_delivery_time.json`.

# Build

To build the CLI application run one of the following commands:

	pip install --editable .

	python -m pip install --editable .

To ensure the command succeeded, verify the creation of the directory `./maverage.egg-info/`.

# Run

To run the `maverage` CLI application with the input file `./events/events.json` with a window size of `10`, run the command as follows:

	maverage --input_file event/events.json --window_size 10

# Test
