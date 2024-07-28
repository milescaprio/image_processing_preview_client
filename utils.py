def mapval(value, valMin, valMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = valMax - valMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - valMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def clamp(n, smallest, largest): return max(smallest, min(n, largest))