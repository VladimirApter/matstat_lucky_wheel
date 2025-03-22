class Color:
    def __init__(self, hsl=None, hex_code=None):
        if hsl:
            self.h, self.s, self.l = hsl
            self.r, self.g, self.b = self.hsl_to_rgb(*hsl)
        elif hex_code:
            self.r, self.g, self.b = self.hex_to_rgb(hex_code)
            self.h, self.s, self.l = self.rgb_to_hsl(self.r, self.g, self.b)
        else:
            raise ValueError("Нужно указать HSL или HEX")

        self.hex = self.rgb_to_hex(self.r, self.g, self.b)

    @staticmethod
    def hex_to_rgb(hex_code):
        hex_code = hex_code.lstrip('#')
        return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def rgb_to_hsl(r, g, b):
        r /= 255.0
        g /= 255.0
        b /= 255.0

        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val

        # Hue calculation
        if diff == 0:
            h = 0
        elif max_val == r:
            h = 60 * ((g - b) / diff % 6)
        elif max_val == g:
            h = 60 * ((b - r) / diff + 2)
        else:
            h = 60 * ((r - g) / diff + 4)

        # Lightness
        l = (max_val + min_val) / 2

        # Saturation
        s = 0 if diff == 0 else diff / (1 - abs(2 * l - 1))

        return (round(h % 360, 2), round(s, 4), round(l, 4))

    @staticmethod
    def hsl_to_rgb(h, s, l):
        h = h % 360
        s = max(0, min(1, s))
        l = max(0, min(1, l))

        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (
            int(round((r + m) * 255)),
            int(round((g + m) * 255)),
            int(round((b + m) * 255))
        )

    def darker(self, amount=0.2):
        new_l = max(0, self.l - amount)
        return Color(hsl=(self.h, self.s, new_l))