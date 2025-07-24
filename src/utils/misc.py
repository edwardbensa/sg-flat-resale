# Function to bin numbers
def bin_numbers(number, start, step):
    start_number = start
    interval = step
    interval_number = start_number + interval - 1
    addend = interval * ((number - start_number) // interval)
    return f"{start_number + addend}-{interval_number + addend}"