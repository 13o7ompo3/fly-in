import hashlib
import webcolors  # type: ignore


class Color:
    @staticmethod
    def get_color(color_name: str) -> str:
        clean_name = str(color_name).strip().lower()

        # 1. Direct matching check
        try:
            hex_code = webcolors.name_to_hex(clean_name)
            return str(hex_code)
        except ValueError:
            pass

        # 2. Map the unknown color name to a raw RGB coordinate using MD5
        hash_object = hashlib.md5(clean_name.encode('utf-8'))
        hex_hash = hash_object.hexdigest()
        raw_hex = f"#{hex_hash[:6]}"
        target_rgb = webcolors.hex_to_rgb(raw_hex)

        # 3. Geometric loop to find the nearest physical neighbor
        smallest_distance = float('inf')
        closest_hex = ""

        # Check against all standard CSS3 colors
        for official_name in webcolors.names("css3"):
            hex_code = webcolors.name_to_hex(official_name)
            named_rgb = webcolors.hex_to_rgb(hex_code)

            # Euclidean distance formula
            distance = (
                (target_rgb.red - named_rgb.red) ** 2 +
                (target_rgb.green - named_rgb.green) ** 2 +
                (target_rgb.blue - named_rgb.blue) ** 2
            )

            if distance < smallest_distance:
                smallest_distance = distance
                closest_hex = hex_code

        return closest_hex

    @staticmethod
    def colored_text_from_hex_codes(text: str, hex_codes: list[str]) -> str:
        rgb_values = [webcolors.hex_to_rgb(hex_code) for hex_code in hex_codes]
        if len(rgb_values) == 1:
            rgb = rgb_values[0]
            return f"\033[38;2;{rgb.red};{rgb.green};{rgb.blue}m{text}\033[0m"
        ret = ""
        for i, char in enumerate(text):
            rgb = rgb_values[i % len(rgb_values)]
            ret += f"\033[38;2;{rgb.red};{rgb.green};{rgb.blue}m{char}"
        ret += "\033[0m"
        return ret

    @staticmethod
    def colored_text(text: str, color_names: list[str]) -> str:
        hex_codes = [Color.get_color(name) for name in color_names]
        return Color.colored_text_from_hex_codes(text, hex_codes)
