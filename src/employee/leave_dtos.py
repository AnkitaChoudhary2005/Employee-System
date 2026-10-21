def leave_to_dto(leave):
    return {
        "id": leave.id,
        "employee_id": leave.employee_id,
        "start_date": leave.start_date,
        "end_date": leave.end_date,
        "reason": leave.reason,
        "status": leave.status,
        "review_note": leave.review_note,
        "reviewed_by": leave.reviewed_by,
        "created_at": leave.created_at,
        "reviewed_at": leave.reviewed_at,
    }