import string

TASK_NAME_REGEX = {
    #   Розбір regular expression: '\p{L}-\p{N}{2}-\p{N}{1,3}-\p{L}'
    #   \p{L} - будьяка літера
    #   \p{N}{2} - будьяка цифра 2 рази підряд
    #   \p{N}{1,3} - будьяка цифра від 1 до 3 разів підряд
    #   \p{L} - будьяка літера
    25: ["^\p{L}-\p{N}{2}-\p{N}{1,3}(-\p{L}){2}$", "M-36-111-Б-г"],  # M-36-111-Б-г
    50: ["^\p{L}-\p{N}{2}-\p{N}{1,3}-\p{L}$", "M-36-111-Б"],  # M-36-111-Б
    100: ["^\p{L}-\p{N}{2}-\p{N}{1,3}$", "M-36-111"],  # M-36-111
    200: ["^\p{L}-\p{N}{2}-(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", "M-36-XI"],  # M-36-XI
    500: ["^\p{L}-\p{N}{2}-\p{L}$", "M-36-Б"],  # M-36-Б
}
COLONS_NUM = 60
COLONS_NUM_STR_LIST = [str(num) for num in range(1, COLONS_NUM + 1)]
THOUSANDS = 144
THOUSANDS_STR_LIST = [str(num) for num in range(1, THOUSANDS + 1)]
ROMAN_NUMS = [
    "I", "II", "III", "IV", "V", "VI",  "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
    "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX",
    "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI",
]
ROW_LATIN_LETTERS = [letter for letter in string.ascii_uppercase if letter not in ["W", "X", "Y", "Z", ]]
CYRILLIC_LETTERS_UP = ["А", "Б", "В", "Г"]
CYRILLIC_LETTERS_DOWN = ["а", "б", "в", "г"]

ROW_ERROR = "Перша літера назви - значення ряда, має бути ЛАТИНСЬКОЮ літерою у верхньому регістрі від A до V"
COLON_ERROR = "Друга цифра - значення колони, має бути цифрою від 1 до 60"
THOUSANDS_ERROR = "Цифра номенклатури масштабу 100 000 має бути в діапазоні від 1 до 144"
ROMAN_ERROR = "Цифра номенклатури масштабу 200 000 має бути римською цифрою в діапазоні від 1 до 36 написаною латинськими літерами"
CYRILLIC_LETTERS_UP_ERROR = "Літера для позначення номенклатури масштабу 50 000 має бути КИРИЛИЧНОЮ літерою у верхньому регістрі від А до Г"
CYRILLIC_LETTERS_DOWN_ERROR = "Остання літера для номенклатури масштабу 25 000 має бути КИРИЛИЧНОЮ літерою у нижньому регістрі від а до г"

TASK_NAME_RULES = {
    25: {
        0: {"rule": ROW_LATIN_LETTERS, "error": ROW_ERROR},
        1: {"rule": COLONS_NUM_STR_LIST, "error": COLON_ERROR},
        2: {"rule": THOUSANDS_STR_LIST, "error": THOUSANDS_ERROR},
        3: {"rule": CYRILLIC_LETTERS_UP, "error": CYRILLIC_LETTERS_UP_ERROR},
        4: {"rule": CYRILLIC_LETTERS_DOWN, "error": CYRILLIC_LETTERS_DOWN_ERROR}
    },
    50: {
        0: {"rule": ROW_LATIN_LETTERS, "error": ROW_ERROR},
        1: {"rule": COLONS_NUM_STR_LIST, "error": COLON_ERROR},
        2: {"rule": THOUSANDS_STR_LIST, "error": THOUSANDS_ERROR},
        3: {"rule": CYRILLIC_LETTERS_UP, "error": CYRILLIC_LETTERS_UP_ERROR},
    },
    100: {
        0: {"rule": ROW_LATIN_LETTERS, "error": ROW_ERROR},
        1: {"rule": COLONS_NUM_STR_LIST, "error": COLON_ERROR},
        2: {"rule": THOUSANDS_STR_LIST, "error": THOUSANDS_ERROR},
    },
    200: {
        0: {"rule": ROW_LATIN_LETTERS, "error": ROW_ERROR},
        1: {"rule": COLONS_NUM_STR_LIST, "error": COLON_ERROR},
        2: {"rule": ROMAN_NUMS, "error": ROMAN_ERROR},
    },
    500: {
        0: {"rule": ROW_LATIN_LETTERS, "error": ROW_ERROR},
        1: {"rule": COLONS_NUM_STR_LIST, "error": COLON_ERROR},
        2: {"rule": CYRILLIC_LETTERS_UP, "error": CYRILLIC_LETTERS_UP_ERROR},
    },
}
