import openpyxl

from api.models import Task, TimeTracker, Statuses

path = "/home/yurii/PROJECTS/test/Розрахунок виконання робіт_2024.xlsx"

book = openpyxl.open(path, read_only=True)
sheet = book.active

for row in range (4, sheet.max_row+1):
    task = Task.objects.create(
        **{
            "scale": sheet[row][0].value,
            "name": sheet[row][1].value,
            "year": sheet[row][2].value,
            "category": sheet[row][3].value,
            "editing_time_estimate": sheet[row][4].value,
            "correcting_time_estimate": sheet[row][5].value,
            "tc_time_estimate": sheet[row][6].value,
            "quarter": sheet[row][7].value,
            "department": sheet[row][8].value,
        }
    )

    task.save()

    TimeTracker.objects.create(
        task=task,
        task_status=Statuses.EDITING_QUEUE.value,
        task_department=task.department,
        start_time=task.created,
    )
    Comment.objects.create(
        task=task,
        user=User.objects.first(),
        body=f"Створено задачу {task.name}",
        is_log=True,
    )
    self.stdout.write(f"Created task: {task.name}")

    name = sheet[row][0].value
    scores = sheet[row][1].value
    print(row, name, scores)


