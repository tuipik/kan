import string

from api.choices import TaskScales

TASK_NAME_REGEX = {
    #   Розбір regular expression: '\p{L}-\p{N}{2}-\p{N}{1,3}-\p{L}'
    #   \p{L} - будьяка літера
    #   \p{N}{2} - будьяка цифра 2 рази підряд
    #   \p{N}{1,3} - будьяка цифра від 1 до 3 разів підряд
    #   \p{L} - будьяка літера
    10: ["^\p{L}-\p{N}{1,2}-\p{N}{1,3}(-\p{L}){2}-[1-4]$", "M-36-111-Б-г-1"],  # M-36-111-Б-г-1
    25: ["^\p{L}-\p{N}{1,2}-\p{N}{1,3}(-\p{L}){2}$", "M-36-111-Б-г"],  # M-36-111-Б-г
    50: ["^\p{L}-\p{N}{1,2}-\p{N}{1,3}-\p{L}$", "M-36-111-Б"],  # M-36-111-Б
    100: ["^\p{L}-\p{N}{1,2}-\p{N}{1,3}$", "M-36-111"],  # M-36-111
    200: ["^\p{L}-\p{N}{1,2}-(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", "M-36-XI"],  # M-36-XI
    500: ["^\p{L}-\p{N}{1,2}-\p{L}$", "M-36-Б"],  # M-36-Б
    1000: ["^\p{L}-\p{N}{1,2}$", "M-36"],  # M-36
}

ROWS_CHOICES = [letter for letter in string.ascii_uppercase if letter not in ["W", "X", "Y", "Z", ]]
COLUMN_MAX = 60
COLUMNS_CHOICES = [str(num + 1) for num in range(COLUMN_MAX)]
TRAPEZE_500K_AND_50K_CHOICES = ["А", "Б", "В", "Г"]
ROMAN_NUMBERS = [
    "I", "II", "III", "IV", "V", "VI",  "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
    "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX",
    "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI",
]
TRAPEZE_100K_MAX = 144
TRAPEZE_100K_CHOICES = [str(num + 1) for num in range(TRAPEZE_100K_MAX)]
TRAPEZE_25K_CHOICES = ["а", "б", "в", "г"]
TRAPEZE_10K_MAX = 4
TRAPEZE_10K_CHOICES = ["1", "2", "3", "4"]

ROW_ERROR = "Перша літера назви - значення ряда, має бути ЛАТИНСЬКОЮ літерою у верхньому регістрі від A до V"
COLON_ERROR = "Друга цифра - значення колони, має бути цифрою від 1 до 60"
THOUSANDS_ERROR = "Цифра номенклатури масштабу 100 000 має бути в діапазоні від 1 до 144"
ROMAN_ERROR = "Цифра номенклатури масштабу 200 000 має бути римською цифрою в діапазоні від 1 до 36 написаною латинськими літерами"
CYRILLIC_LETTERS_UP_ERROR = "Літера для позначення номенклатури масштабу 50 000 має бути КИРИЛИЧНОЮ літерою у верхньому регістрі від А до Г"
CYRILLIC_LETTERS_DOWN_ERROR = "Остання літера для номенклатури масштабу 25 000 має бути КИРИЛИЧНОЮ літерою у нижньому регістрі від а до г"
TEN_SCALE_NUMBERS_ERROR = "Остання цифра номенклатури масштабу 10 000 має бути від 1 до 4"

TASK_NAME_RULES = {
    10: {
        0: {"rule": ROWS_CHOICES, "error": ROW_ERROR},
        1: {"rule": COLUMNS_CHOICES, "error": COLON_ERROR},
        2: {"rule": TRAPEZE_100K_CHOICES, "error": THOUSANDS_ERROR},
        3: {"rule": TRAPEZE_500K_AND_50K_CHOICES, "error": CYRILLIC_LETTERS_UP_ERROR},
        4: {"rule": TRAPEZE_25K_CHOICES, "error": CYRILLIC_LETTERS_DOWN_ERROR},
        5: {"rule": TRAPEZE_10K_CHOICES, "error": TEN_SCALE_NUMBERS_ERROR},
    },
    25: {
        0: {"rule": ROWS_CHOICES, "error": ROW_ERROR},
        1: {"rule": COLUMNS_CHOICES, "error": COLON_ERROR},
        2: {"rule": TRAPEZE_100K_CHOICES, "error": THOUSANDS_ERROR},
        3: {"rule": TRAPEZE_500K_AND_50K_CHOICES, "error": CYRILLIC_LETTERS_UP_ERROR},
        4: {"rule": TRAPEZE_25K_CHOICES, "error": CYRILLIC_LETTERS_DOWN_ERROR}
    },
    50: {
        0: {"rule": ROWS_CHOICES, "error": ROW_ERROR},
        1: {"rule": COLUMNS_CHOICES, "error": COLON_ERROR},
        2: {"rule": TRAPEZE_100K_CHOICES, "error": THOUSANDS_ERROR},
        3: {"rule": TRAPEZE_500K_AND_50K_CHOICES, "error": CYRILLIC_LETTERS_UP_ERROR},
    },
    100: {
        0: {"rule": ROWS_CHOICES, "error": ROW_ERROR},
        1: {"rule": COLUMNS_CHOICES, "error": COLON_ERROR},
        2: {"rule": TRAPEZE_100K_CHOICES, "error": THOUSANDS_ERROR},
    },
    200: {
        0: {"rule": ROWS_CHOICES, "error": ROW_ERROR},
        1: {"rule": COLUMNS_CHOICES, "error": COLON_ERROR},
        2: {"rule": ROMAN_NUMBERS, "error": ROMAN_ERROR},
    },
    500: {
        0: {"rule": ROWS_CHOICES, "error": ROW_ERROR},
        1: {"rule": COLUMNS_CHOICES, "error": COLON_ERROR},
        2: {"rule": TRAPEZE_500K_AND_50K_CHOICES, "error": CYRILLIC_LETTERS_UP_ERROR},
    },
    1000: {
        0: {"rule": ROWS_CHOICES, "error": ROW_ERROR},
        1: {"rule": COLUMNS_CHOICES, "error": COLON_ERROR},
    },
}

SCALE_RULES_FOR_IMPORT_EXCEL = {
    "1:10000": TaskScales.TEN.value,
    "1:25000": TaskScales.TWENTY_FIVE.value,
    "1:50000": TaskScales.FIFTY.value,
    ":100000": TaskScales.ONE_HUNDRED.value,
    ":200000": TaskScales.TWO_HUNDRED.value,
    ":500000": TaskScales.FIVE_HUNDRED.value,
    ":1000000": TaskScales.ONE_MILLION.value,
}