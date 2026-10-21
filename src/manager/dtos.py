def manager_to_dto(manager, user=None):
    return {
        "id": manager.id,
        "user_id": manager.user_id,
        "name": manager.name,
        "department": manager.department,
        "email": user.email if user else None,
    }
