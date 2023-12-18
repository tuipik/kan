class BaseValidationStrategy:

    def __init__(self, validated_data, task, request_user, status):
        self.validated_data = validated_data
        self.task = task
        self.request_user = request_user
        self.status = status
        self.department = validated_data.get("department", None)
        self.user = validated_data.get("user") or (
            task.user if task else None
        )
