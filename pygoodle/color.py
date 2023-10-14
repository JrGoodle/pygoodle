"""color utilities

.. codeauthor:: JeanExtreme002

"""

def rgb_to_hex(rgb: list) -> str:

    hex_chars = {10: "A", 11: "B", 12: "C", 13: "D", 14: "E", 15: "F"}
    hex_color = "#"

    for channel in rgb:

        if channel > 255: raise ValueError("The maximum value of each of the colors is 255.")
        if channel < 0: raise ValueError("The minimum value of each of the colors is zero.")

        first_value = channel // 16
        second_value = int((channel / 16 - channel // 16) * 16)

        hex_color += hex_chars.get(first_value, str(first_value))
        hex_color += hex_chars.get(second_value, str(second_value))

    return hex_color


def hex_to_rgb(hexadecimal: str) -> list:

    hexadecimal = hexadecimal.replace("#", "").replace("0x", "").upper()

    if len(hexadecimal) != 6: raise ValueError("The hex value must contain 6 digits")

    hex_chars = {"A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15}
    rgb_color = []

    for index in range(0, len(hexadecimal), 2):
        first_value, second_value = hexadecimal[index : index + 2]

        if not all(map(lambda x: x in "0123456789ABCDEF", [first_value, second_value])):
            raise ValueError("The given value is not a hex value.")

        first_value = int(hex_chars.get(first_value, first_value)) * 16
        second_value = int(hex_chars.get(second_value, second_value))
        rgb_color.append(first_value + second_value)

    return rgb_color


def get_gradient(color1: list, color2: list, length: int):

    red1, green1, blue1 = color1
    red2, green2, blue2 = color2

    r_ratio = (red2 - red1) / length
    g_ratio = (green2 - green1) / length
    b_ratio = (blue2 - blue1) / length

    for pixel in range(length):
        red = int(red1 + (r_ratio * pixel))
        green = int(green1 + (g_ratio * pixel))
        blue = int(blue1 + (b_ratio * pixel))

        yield (red, green, blue)
