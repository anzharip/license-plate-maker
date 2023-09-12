import argparse
import os
import random
import secrets
import time
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

# ------------
# | 横浜200	|
# |か　10-74	|
# ------------
# 横浜　= plate_lto_abbr
# 200 = plate_class
# か　= plate_hira
# 10-74 = plate_number

HIRAGANA = [
    "あ",
    "い",
    "う",
    "え",
    "か",
    "き",
    "く",
    "け",
    "こ",
    "さ",
    "す",
    "せ",
    "そ",
    "た",
    "ち",
    "つ",
    "て",
    "と",
    "な",
    "に",
    "ぬ",
    "ね",
    "の",
    "は",
    "ひ",
    "ふ",
    "ほ",
    "ま",
    "み",
    "む",
    "め",
    "も",
    "ら",
    "り",
    "る",
    "れ",
    "ろ",
    "や",
    "ゆ",
    "よ",
    "わ",
    "を",
]

ISSUING_OFFICE = [
    "尾張小牧",
    "一宮",
    "春日井",
    "名古屋",
    "豊橋",
    "三河",
    "岡崎",
    "豊田",
    "秋田",
    "青森",
    "八戸",
    "千葉",
    "成田",
    "習志野",
    "野田",
    "柏",
    "袖ヶ浦",
    "愛媛",
    "福井",
    "福岡",
    "筑豊",
    "北九州",
    "久留米",
    "福島",
    "会津",
    "郡山",
    "いわき",
    "岐阜",
    "飛騨",
    "群馬",
    "前橋",
    "高崎",
    "福山",
    "広島",
    "旭川",
    "函館",
    "北見",
    "釧路",
    "室蘭",
    "帯広",
    "札幌",
    "姫路",
    "神戸",
    "水戸",
    "土浦",
    "つくば",
    "石川",
    "金沢",
    "岩手",
    "平泉",
    "盛岡",
    "香川",
    "鹿児島",
    "奄美",
    "相模",
    "湘南",
    "川崎",
    "横浜",
    "高知",
    "熊本",
    "京都",
    "三重",
    "鈴鹿",
    "宮城",
    "仙台",
    "宮崎",
    "松本",
    "諏訪",
    "長野",
    "長崎",
    "佐世保",
    "奈良",
    "長岡",
    "新潟",
    "大分",
    "岡山",
    "倉敷",
    "沖縄",
    "和泉",
    "堺",
    "大阪",
    "なにわ",
    "佐賀",
    "春日部",
    "越谷",
    "熊谷",
    "大宮",
    "川口",
    "所沢",
    "川越",
    "滋賀",
    "島根",
    "浜松",
    "沼津",
    "富士山",
    "伊豆",
    "静岡",
    "栃木",
    "宇都宮",
    "那須",
    "徳島",
    "足立",
    "八王子",
    "多摩",
    "練馬",
    "杉並",
    "品川",
    "世田谷",
    "鳥取",
    "富山",
    "和歌山",
    "庄内",
    "山形",
    "山口",
    "下関",
    "山梨",
]


class Plate:
    # List of plate type
    PLATE_TYPE = {
        2: "resources/template/kei.png",
        1: "resources/template/normal.png",
        3: "resources/template/comm.png",
        4: "resources/template/kei-comm.png",
        5: "resources/template/kari-white.png",
    }

    # List of font color
    FONT_COLOR = {
        1: (25, 79, 56),
        2: (50, 50, 50),
        3: (255, 255, 255),
        4: (243, 194, 4),
        5: (0, 0, 0),
    }

    # List of font directories
    LIST_FONT = {
        "TRM": "resources/font/trm.ttf",
        "FZ": "resources/font/fz.otf",
        "EPSON": "resources/font/epmgobld.ttf",
    }

    # List of Hiragana by Font
    FONT_TRM_HIRA = list("あいうかきくけこせを")
    FONT_FZ_HIRA = list("えさすそたちつてとなにぬねのはひふほまみむめもやゆよらりるれろわ")

    # List of LTO Abbreviations
    LIST_TRM_LTO_ABBR = ["ナニワ", "山口", "岐阜", "石川", "浜松", "島根", "横浜", "Ｏ", "Ｉ"]
    LIST_FZ_LTO_ABBR = ["ツクバ", "福島", "北九州", "奈良", "徳島", "金沢", "山口", "富士山", "高知"]

    BOLT_SOURCE = "resources/template/bolt.png"
    SCREW_SOURCE = "resources/template/screw.png"

    SCREW_POS = {1: ((205, 80), (1130, 80)), 2: ((205, 50), (1130, 50))}

    BOLT_POS = {1: (200, 75), 2: (200, 45)}

    def __init__(
        self,
        p_lto_abbr,
        p_class_num,
        p_hira,
        p_number,
        p_bolt,
        p_screw,
        p_type: int = 1,
    ):
        self.type = self.PLATE_TYPE[p_type]
        self.font_color = self.FONT_COLOR[p_type]
        # Hiragana Character Setting
        self.hira = p_hira
        self.hira_font = self._hira_font(p_hira)
        self.hira_font_size = 650 if self.hira in self.FONT_TRM_HIRA else 200
        self.hira_position = (60, 180) if self.hira in self.FONT_TRM_HIRA else (85, 380)
        # LTO abbreviation Setting
        self.lto_abbr = p_lto_abbr
        self.lto_abbr_font = self._lto_abbr_font(self.lto_abbr)
        self.lto_abbr_font_size = (
            200 if self.lto_abbr in self.LIST_TRM_LTO_ABBR else 175
        )
        self.lto_abbr_position = (
            (340, 70) if self.lto_abbr in self.LIST_TRM_LTO_ABBR else (365, 70)
        )
        # Class Number Setting
        self.class_num = self._class_num_format(p_class_num)
        self.class_num_font = self.LIST_FONT["TRM"]
        # Plate Number Setting
        self.number = self._plate_format(p_number)
        self.number_font = self.LIST_FONT["TRM"]
        # Bolt and Screw Setting
        self.bolt = p_bolt
        self.bolt_position = self._bolt_position(p_type)
        self.bolt_source = self.BOLT_SOURCE
        self.screw = p_screw
        self.screw_position = self._screw_positon(p_type)
        self.screw_source = self.SCREW_SOURCE

    def __str__(self):
        return f"""
		LTO Abbreviation: {self.lto_abbr}, Font used: {self.lto_abbr_font}
		Class Number: {self.class_num}
		Hiragana Character: {self.hira}, Font used: {self.hira_font}
		Number: {self.number}
		Path: {self.type}
		"""

    def _hira_font(self, letter):
        if letter in self.FONT_TRM_HIRA:
            return self.LIST_FONT["TRM"]
        elif letter in self.FONT_FZ_HIRA:
            return self.LIST_FONT["FZ"]
        else:
            raise HiraganaNotFoundError

    def _lto_abbr_font(self, lto_abbr):
        return self.LIST_FONT["EPSON"]
        if lto_abbr in self.LIST_TRM_LTO_ABBR:
            return self.LIST_FONT["TRM"]
        elif lto_abbr in self.LIST_FZ_LTO_ABBR:
            return self.LIST_FONT["FZ"]
        else:
            raise LTOAbbreviationNotFoundError

    def _plate_format(self, number):
        if len(number) <= 4:
            if len(number) == 4:
                return f"{number[:2]}-{number[2:]}"
            elif len(number) == 3:
                return f".{number[:1]} {number[1:]}"
            elif len(number) == 2:
                return f".. {number}"
            elif len(number) == 1:
                return f".. .{number}"
        else:
            raise PlateNumberOutOfBoundError

    def _class_num_format(self, number):
        if len(number) in (1, 2, 3):
            return number
        else:
            raise ClassNumberOutOfBoundError("ClassNumberOutOfBoundError")

    def _screw_positon(self, type):
        if type != 5:
            return self.SCREW_POS[1]
        else:
            return self.SCREW_POS[2]

    def _bolt_position(self, type):
        if type != 5:
            return self.BOLT_POS[1]
        else:
            return self.BOLT_POS[2]

    def generatePlate(self):
        img = Image.open(self.type)
        draw = ImageDraw.Draw(img)
        # Draw LTO Abbreviation
        font_lto_abbr = ImageFont.truetype(self.LIST_FONT["EPSON"], 190)
        # draw.text((365, 70),self.lto_abbr,fill=self.font_color, font=font_lto_abbr)
        if len(self.lto_abbr) == 1:
            draw.text(
                (420, 60), self.lto_abbr[0], fill=self.font_color, font=font_lto_abbr
            )
        if len(self.lto_abbr) == 2:
            draw.text(
                (405, 60), self.lto_abbr[0], fill=self.font_color, font=font_lto_abbr
            )
            draw.text(
                (590, 60), self.lto_abbr[1], fill=self.font_color, font=font_lto_abbr
            )
        if len(self.lto_abbr) == 3:
            temp_image = Image.new("RGBA", img.size, (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_image)
            temp_draw.text(
                (220, 60), self.lto_abbr[0], fill=self.font_color, font=font_lto_abbr
            )
            temp_draw.text(
                (405, 60), self.lto_abbr[1], fill=self.font_color, font=font_lto_abbr
            )
            temp_draw.text(
                (590, 60), self.lto_abbr[2], fill=self.font_color, font=font_lto_abbr
            )
            squashed_image = temp_image.resize(
                (int(temp_image.width * 0.85), int(temp_image.height * 1))
            )
            img.paste(squashed_image, (120, 0), squashed_image)
        if len(self.lto_abbr) == 4:
            temp_image = Image.new("RGBA", img.size, (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_image)
            temp_draw.text(
                (220, 60), self.lto_abbr[0], fill=self.font_color, font=font_lto_abbr
            )
            temp_draw.text(
                (405, 60), self.lto_abbr[1], fill=self.font_color, font=font_lto_abbr
            )
            temp_draw.text(
                (590, 60), self.lto_abbr[2], fill=self.font_color, font=font_lto_abbr
            )
            temp_draw.text(
                (775, 60), self.lto_abbr[3], fill=self.font_color, font=font_lto_abbr
            )
            squashed_image = temp_image.resize(
                (int(temp_image.width * 0.63), int(temp_image.height * 1))
            )
            img.paste(squashed_image, (170, 0), squashed_image)
        # draw.text((390, 60),self.lto_abbr,fill=self.font_color, font=font_lto_abbr)
        # Draw Hiragana Character
        font_hira = ImageFont.truetype(self.hira_font, self.hira_font_size)
        draw.text(self.hira_position, self.hira, fill=self.font_color, font=font_hira)
        # Draw Class Number
        font_class_num = ImageFont.truetype(self.class_num_font, 200)
        if len(self.class_num) == 1:
            draw.text(
                (890, 70), self.class_num, fill=self.font_color, font=font_class_num
            )
        if len(self.class_num) == 2:
            draw.text(
                (840, 70), self.class_num, fill=self.font_color, font=font_class_num
            )
        if len(self.class_num) == 3:
            draw.text(
                (770, 70), self.class_num, fill=self.font_color, font=font_class_num
            )
        # Draw Number
        font_number = ImageFont.truetype(self.number_font, 400)
        draw.text((335, 300), self.number, fill=self.font_color, font=font_number)
        # Draw screw
        if self.screw:
            screw = Image.open(self.screw_source)
            resized_screw = screw.resize(
                (round(screw.size[0] * 0.15), round(screw.size[1] * 0.15))
            )
            img.paste(resized_screw, self.screw_position[0], resized_screw)
            img.paste(resized_screw, self.screw_position[1], resized_screw)
        # Draw Bolt
        if self.bolt:
            bolt = Image.open(self.bolt_source)
            resized_bolt = bolt.resize(
                (round(bolt.size[0] * 0.18), round(bolt.size[1] * 0.18))
            )
            img.paste(resized_bolt, self.bolt_position, resized_bolt)
        # generate plate name to be sent back to client
        now = time.time()
        filename = f"output/{len(self.class_num)}-digit_{self.lto_abbr}_{self.hira}_{now}_{secrets.token_hex(4)}_synth_plate.png"
        img.save(filename)
        return filename


class Error(Exception):
    pass  # Base Exception


class HiraganaNotFoundError(Error):
    pass  # Exception when plate_hira is not in the list


class LTOAbbreviationNotFoundError(Error):
    pass  # Exception when LTO Abbreviation is not in the list


class PlateNumberOutOfBoundError(Error):
    pass  # Exception when plate number is not provided//more than 4 characters


class ClassNumberOutOfBoundError(Error):
    pass  # Exception when plate number is not provided//more than 3/less than 2 characters


def _generate_random_v_class():
    return str(random.randint(1, 6))


def _generate_random_v_class_num():
    return str(random.randint(0, 99))


def _generate_random_office():
    return random.choice(ISSUING_OFFICE)


def _generate_random_v_number(length):
    if length == 1:
        return str(random.randint(1, 9))
    if length == 2:
        return str(random.randint(10, 99))
    if length == 3:
        return str(random.randint(100, 999))
    if length == 4:
        return str(random.randint(1000, 9999))
    raise ValueError("Length has to be between 1 to 9999")


def _generate_random_hiragana():
    return HIRAGANA[random.randint(0, 41)]


def _generate_plate(hiragana, set_count):
    for plate_type in range(1, 6):
        for i in range(0, set_count):
            office = _generate_random_office()
            v_class = _generate_random_v_class() + _generate_random_v_class_num()
            v_number = _generate_random_v_number()
            p = Plate(office, v_class, hiragana, v_number, True, True, plate_type)
            print(p)
            p.generatePlate()


def _generate_random_v_class_and_number(length):
    if length == 1:
        return _generate_random_v_class()
    if length == 2:
        return _generate_random_v_class() + str(random.randint(0, 9))
    if length == 3:
        return _generate_random_v_class() + str(random.randint(10, 99))

def _generate_random_plate():
    return random.randint(1, 5)

def _generate_plate_v_class(v_class_length, set_count):
    for plate_type in range(1, 6):
        for i in range(0, set_count):
            v_class = _generate_random_v_class_and_number(v_class_length)
            v_number = _generate_random_v_number()
            hiragana = _generate_random_hiragana()
            p = Plate(
                _generate_random_office(),
                v_class,
                hiragana,
                v_number,
                True,
                True,
                plate_type,
            )
            print(p)
            p.generatePlate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic Japanese vehicle number plate. "
    )
    issuing_office_group = parser.add_mutually_exclusive_group(required=True)
    issuing_office_group.add_argument(
        "--issuing-office-random",
        help="Set the issuing office to random. ",
        dest="issuing_office_random",
        action="store_true",
    )
    issuing_office_group.add_argument(
        "--issuing-office",
        help="Set the issuing office manually. ",
        choices=ISSUING_OFFICE,
        dest="issuing_office",
    )

    vehicle_class_group = parser.add_mutually_exclusive_group(required=True)
    vehicle_class_group.add_argument(
        "--vehicle-class-random",
        help="Set the vehicle class to random. ",
        dest="vehicle_class_random",
        action="store_true",
    )
    vehicle_class_group.add_argument(
        "--vehicle-class",
        help="Set the vehicle class manually. ",
        dest="vehicle_class",
    )
    parser.add_argument(
        "--vehicle-class-length",
        help="Set the vehicle class length. Will be ignored if --vehicle-class is defined. ",
        choices=[1, 2, 3],
        dest="vehicle_class_length",
        type=int,
        required=True,
    )
    hiragana_group = parser.add_mutually_exclusive_group(required=True)
    hiragana_group.add_argument(
        "--hiragana-random",
        help="Set the hiragana to random. ",
        dest="hiragana_random",
        action="store_true",
    )
    hiragana_group.add_argument(
        "--hiragana",
        help="Set the hiragana manually. ",
        choices=HIRAGANA,
        dest="hiragana",
    )
    number_group = parser.add_mutually_exclusive_group(required=True)
    number_group.add_argument(
        "--number-random",
        help="Set the number to random. ",
        dest="number_random",
        action="store_true",
    )
    number_group.add_argument(
        "--number", help="Set the number manually. ", type=int, dest="number"
    )
    parser.add_argument(
        "--number-length",
        help="Set the number length. Will be ignored if --number-random is defined. ",
        choices=[1, 2, 3, 4],
        dest="number_length",
        type=int,
        required=True,
    )
    plate_group = parser.add_mutually_exclusive_group(required=True)
    plate_group.add_argument(
        "--plate-random",
        help="Set the plate type to random",
        dest="plate_random",
        action="store_true",
    )
    plate_group.add_argument(
        "--plate",
        help="Set the plate type manually",
        dest="plate",
        choices=[1, 2, 3, 4, 5],
        type=int,
    )
    parser.add_argument(
        "--count",
        help="Number of plates to generate. ",
        dest="count",
        type=int,
        required=True,
    )
    args = parser.parse_args()
    if args.issuing_office_random:
        issuing_office_generator = _generate_random_office
    else:
        issuing_office_generator = lambda: args.issuing_office
    if args.vehicle_class_random:
        vehicle_class_generator = lambda: _generate_random_v_class_and_number(
            args.vehicle_class_length
        )
    else:
        if len(args.vehicle_class) > 0 and len(args.vehicle_class) < 4:
            vehicle_class_generator = lambda: args.vehicle_class
        else:
            raise ValueError("Vehicle class has to be between 1 to 599")
    if args.hiragana_random:
        hiragana_generator = _generate_random_hiragana
    else:
        hiragana_generator = lambda: args.hiragana
    if args.number_random:
        number_generator = lambda: _generate_random_v_number(args.number_length)
    else:
        if args.number > 0 and args.number < 10000:
            number_generator = lambda: args.number
        else:
            raise ValueError("Number has to be between 1 to 9999")
    if args.plate_random:
        plate_generator = _generate_random_plate
    else:
        plate_generator = lambda: args.plate
    os.makedirs("./output", exist_ok=True)
    for n in range(args.count):
        p = Plate(
            issuing_office_generator(),
            vehicle_class_generator(),
            hiragana_generator(),
            number_generator(),
            True,
            True,
            plate_generator(),
        )
        print(p)
        p.generatePlate()
