from api.management.commands.task_importer.task_importer import TaskImporter

file = "/home/yurii/PROJECTS/kan/api/management/commands/task_importer/task_updates.xlsx"

task_importer = TaskImporter()

task_importer.run(file)
