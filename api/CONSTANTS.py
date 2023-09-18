from api.models import TimeTrackerStatuses, YearQuarter, TaskScales

TASK_NAME_REGEX = {
    #   Розбір regular expression: '\p{L}-\p{N}{2}-\p{N}{1,3}-\p{L}(?![\p{L}\p{N}\-])'
    #   \p{L} - будьяка літера
    #   \p{N}{2} - будьяка цифра 2 рази підряд
    #   \p{N}{1,3} - будьяка цифра від 1 до 3 разів підряд
    #   \p{L} - будьяка літера
    #   (?![\p{L}\p{N}\-]) - наступний символ не літера, не цифра і не знак '-'
    25: "\p{L}-\p{N}{2}-\p{N}{1,3}(-\p{L}){2}",  # M-36-111-A-a
    50: "\p{L}-\p{N}{2}-\p{N}{1,3}-\p{L}(?![\p{L}\p{N}\-])",  # M-36-111-A
    100: "\p{L}-\p{N}{2}-\p{N}{1,3}(?![\p{L}\p{N}\-])",  # M-36-111
    200: "\p{L}-\p{N}{2}-\(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})(?![\p{L}\p{N}\-])",  # M-36-XI
    500: "\p{L}-\p{N}{2}-\p{L}(?![\p{L}\p{N}\-])",  # M-36-A
}

TASK_SCALES = {scale.value: scale.label for scale in TaskScales}
TIME_TRACKER_STATUSES = {status.value: status.label for status in TimeTrackerStatuses}
YEAR_QUARTERS = {quarter.value: quarter.label for quarter in YearQuarter}
