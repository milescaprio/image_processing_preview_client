def mapval(value, valMin, valMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = valMax - valMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - valMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def add2(a, b):
    return (a[0] + b[0], a[1] + b[1])

def sub2(a, b):
    return (a[0] - b[0], a[1] - b[1])

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def clamp2(s : tuple[float, float], minx, miny, maxx, maxy):
    return (clamp(s[0], minx, maxx), clamp(s[1], miny, maxy))