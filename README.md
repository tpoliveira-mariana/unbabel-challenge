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

Moreover, the timestamps that are kept are not the ones received as input.
In fact, unless an event happened at an exact minute (eg. `"2018-12-26 18:25:00.000000"`) its `timestamp` is rounded to the next one:
`18:11:08.509654` -> `18:12:00.000000`.

Next, the column `timestep` is added to the clean dataset. It contains the cumulative sum of the differences (in minutes) between each timestamp and the one that preceeds it.
This information is useful in step 3.

The function `enhance_data()` also ensures the support for multiple events in the same minute. It does so by aggregating the corresponding rows into a single one with: the same `timestamp`, the `timestep` of the oldest one, and the average `duration` for the events involved.

Unsurprisingly, `moving_average()` computes the moving average for the `duration` field of the events received as input. I am considering that, whenever no events were registered in a window, the `average_delivery_time` for the corresponding minute is `0`.

In addition, the moving average is always computed for the interval `[minT-1, maxT]`, even if a window size that is greater than the time range of the events received is provided. Here `minT` and `maxT` are the `timestamp` for the oldest and newest events respectively (after being processed in step 2, as mentioned above).

Finaly, the list with the resulting datapoints is written to the file `average_delivery_time.json`.

# Build


To build the CLI application, first ensure you have `Python` and `pip` intalled, then run one of the following commands:

	pip install --editable .

	python -m pip install --editable .

**Note:** You need to be on the root directory of this repo.

To ensure the command succeeded, verify the creation of the directory `./maverage.egg-info/`.

# Run

To run the `maverage` CLI application with the input file `./events/events.json` with a window size of `10`, run the command as follows:

	maverage --input_file event/events.json --window_size 10

# Test

To ensure the CLI application behaves as described above, one can use the example events files in the `events` folder. Find below multiple aspects to validate:

1. Basic behaviour with the `events.json`, provided in the problem description;
2. When no events are registered in a specific time window, the `average_delivery_time` is `0`;
3. Moving average computed only until for the interval `[minT-1, maxT]`, despite the window being longer than the time range between the first and the last event;
4. Support events over different days;
5. Support multiple events in the same minute.

Next some test examples are provided. Feel free to go over each one, and to try your own inputs!

#### Test 1

Run:

	maverage --input_file events/events.json --window_size 10

Output to file `average_delivery_time.json`:

	{"date": "2018-12-26 18:11:00", "average_delivery_time": 0}
	{"date": "2018-12-26 18:12:00", "average_delivery_time": 20}
	{"date": "2018-12-26 18:13:00", "average_delivery_time": 20}
	{"date": "2018-12-26 18:14:00", "average_delivery_time": 20}
	{"date": "2018-12-26 18:15:00", "average_delivery_time": 20}
	{"date": "2018-12-26 18:16:00", "average_delivery_time": 25.5}
	{"date": "2018-12-26 18:17:00", "average_delivery_time": 25.5}
	{"date": "2018-12-26 18:18:00", "average_delivery_time": 25.5}
	{"date": "2018-12-26 18:19:00", "average_delivery_time": 25.5}
	{"date": "2018-12-26 18:20:00", "average_delivery_time": 25.5}
	{"date": "2018-12-26 18:21:00", "average_delivery_time": 25.5}
	{"date": "2018-12-26 18:22:00", "average_delivery_time": 31}
	{"date": "2018-12-26 18:23:00", "average_delivery_time": 31}
	{"date": "2018-12-26 18:24:00", "average_delivery_time": 42.5}

*Validations:*

1. ✔️
2. \-
3. ✔️ - In this case, `minT = "2018-12-26 18:12:00"` because the first event was registered past `18:11:00`, and `maxT= "2018-12-26 18:24:00"` because the last event was registered past `18:23:00`.
4. \-
5. \-

---
#### Test 2

Run:

	maverage --input_file events/events3.json --window_size 10

Output to file `average_delivery_time.json`:

	{"date": "2018-12-26 23:54:00", "average_delivery_time": 0}
	{"date": "2018-12-26 23:55:00", "average_delivery_time": 20}
	{"date": "2018-12-26 23:56:00", "average_delivery_time": 25.5}
	{"date": "2018-12-26 23:57:00", "average_delivery_time": 31}
	{"date": "2018-12-26 23:58:00", "average_delivery_time": 0}
	{"date": "2018-12-26 23:59:00", "average_delivery_time": 0}
	{"date": "2018-12-27 00:00:00", "average_delivery_time": 0}
	{"date": "2018-12-27 00:01:00", "average_delivery_time": 0}
	{"date": "2018-12-27 00:02:00", "average_delivery_time": 0}
	{"date": "2018-12-27 00:03:00", "average_delivery_time": 0}
	{"date": "2018-12-27 00:04:00", "average_delivery_time": 0}
	{"date": "2018-12-27 00:05:00", "average_delivery_time": 0}
	{"date": "2018-12-27 00:06:00", "average_delivery_time": 0}
	{"date": "2018-12-27 00:07:00", "average_delivery_time": 54}

*Validations:*

1. \-
2. ✔️
3. ✔️
4. ✔️ - Note that events occured over `2018-12-26` and `2018-12-27`.
5. \-

---

#### Test 3

Run:

	maverage --input_file events/events5.json --window_size 20

Output to file `average_delivery_time.json`:

	{"date": "2018-12-26 18:10:00", "average_delivery_time": 0}
	{"date": "2018-12-26 18:11:00", "average_delivery_time": 20}
	{"date": "2018-12-26 18:12:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:13:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:14:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:15:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:16:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:17:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:18:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:19:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:20:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:21:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:22:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:23:00", "average_delivery_time": 22.8}
	{"date": "2018-12-26 18:24:00", "average_delivery_time": 33.2}

*Validations:*

1. \-
2. \-
3. ✔️ - The time range between the first and last events is `13 minutes < 20` (the window size provided).
4. \-
5. ✔️ - Note events 2 and 3 both occur at `18:11`.
