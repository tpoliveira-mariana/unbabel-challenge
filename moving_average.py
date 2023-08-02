import click, json, pandas as pd

def is_valid_event(event : dict):
    return event and 'event_name' in event and \
            event['event_name'] == 'translation_delivered' and \
            'timestamp' in event and 'duration' in event

def get_clean_data(file : str):   
    with open(file) as f:
        clean = []
        for line in f:
            line = line.rstrip()    # ignore empty lines
            if line:
                datapoint = json.loads(line)
                if is_valid_event(datapoint):
                    # round timestamp to next minute 
                    timestamp = pd.to_datetime(datapoint['timestamp']).ceil(freq='T') 
                    duration = pd.to_numeric(datapoint['duration'])
                    clean.append({'timestamp': timestamp, 'duration': duration})

        return pd.DataFrame(clean)
    
def enhance_data(data : pd.DataFrame):
    data['timestep'] = data['timestamp'].diff().dt.total_seconds() / 60 
    data['timestep'].fillna(0, inplace=True)
    data['timestep'] = data['timestep'].astype(int).cumsum()

    agg_functions = {'timestamp': 'first', 'duration': 'mean', 'timestep': 'first'}
    return data.groupby(data['timestamp']).aggregate(agg_functions)

def build_result(prev_date : str, mean_duration : float):

    next_date = pd.Timestamp(prev_date) + pd.Timedelta(minutes=1)
    ndigits = None if mean_duration % 1 == 0 else 1

    return { 'date': str(next_date), 'average_delivery_time': round(mean_duration, ndigits)}

def moving_average(data : pd.DataFrame, period : int):
    steps = data['timestep'].iloc[-1] + 1
    results = [
        {
            'date': str(data['timestamp'].iloc[0] - pd.Timedelta(minutes=1)), 
            'average_delivery_time': 0
        }]

    # compute  moving average
    moments = list(data['timestep'])
    lower = 0
    oldest_idx = 0
    to_avg = []
    for upper in range(steps): 
        if upper >= period:
            # window shifts at every time step after period
            lower += 1
            if lower > moments[oldest_idx]:
                # first (aka oldest) event no longer in window
                to_avg.pop(0)
                oldest_idx += 1
            
        if upper in moments:
            # upper bound of window reached new event
            to_avg.append(data['duration'].iloc[moments.index(upper)])


        # prevent cases with no registered events in window
        average = 0
        if len(to_avg):
            average = sum(to_avg) / len(to_avg)

        results.append(build_result(results[upper]['date'], average))

    return results

def output_result(results : list):
    with open('average_delivery_time.json', 'w') as f:
        for result in results:
            json.dump(result, f)
            f.write('\n')       


@click.command()
@click.option("--input_file", type=click.Path(exists=True), required=True, 
              help="Json file with the events")
@click.option("--window_size", type=click.IntRange(0), required=True, 
              help="Size (in minutes) of the sliding window")
def process_events(input_file, window_size):
    data = get_clean_data(input_file)
    data = enhance_data(data)
    result = moving_average(data, window_size)
    output_result(result)
    
    
