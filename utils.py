

def seconds_to_str(total_seconds):
    secondsInMinute = 60
    minuteInHour = 60
    secondsInHour = secondsInMinute * minuteInHour

    hours = int(total_seconds / (secondsInHour))
    minutes = int(total_seconds / minuteInHour % minuteInHour)
    seconds = int(total_seconds % secondsInMinute)

    if hours >= 1:
        htime = hours + (minutes / 60)
        return f"{htime} hours"
    elif minutes >= 1:
        mtime = minutes + (seconds / 60)
        return f"{mtime:.1f} minutes"
    else:
        return f"{seconds:.1f} seconds"

#   let string: NSString = NSString(format: "%02.f:%02.f:%02.f", hours, minutes, seconds)




# From: https://stackoverflow.com/questions/12523586/

def byte_to_str(B):
    """Return the given bytes as a human friendly KB, MB, GB, or TB string."""
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B / TB)
