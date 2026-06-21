PIXEL_SIZE = 2

with open(
    "CARS.PTX",
    "rb",
) as f:
    data = f.read()
    data = data[44:]

    possible_resolutions = []
    for width in range(1, 1025):
        if len(data) == width * PIXEL_SIZE * (len(data) // (width * PIXEL_SIZE)):
            possible_resolutions.append((width, len(data) // (width * PIXEL_SIZE)))

    print("Possible resolutions:")
    for width, height in possible_resolutions:
        print(f"{width}x{height}")
