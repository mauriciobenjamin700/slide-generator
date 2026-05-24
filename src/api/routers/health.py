"""`GET /health` — liveness probe."""

from fastapi import APIRouter


router: APIRouter = APIRouter(tags=["health"])


@router.get(
	"/health",
	summary="Liveness probe.",
	response_description="Static OK payload — does not check downstream dependencies.",
)
async def health() -> dict[str, str]:
	"""Return a constant OK payload.

	Returns:
	    `{"status": "ok"}`.
	"""
	return {"status": "ok"}
