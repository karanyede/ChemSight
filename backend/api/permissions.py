"""Custom permission classes."""
from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsDatasetOwner(BasePermission):
    """Allows access only to the owner of a dataset or its child objects."""

    message = "You do not have permission to access this dataset."

    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        dataset = getattr(obj, "dataset", obj)
        owner = getattr(dataset, "uploaded_by", None)
        return owner == request.user
