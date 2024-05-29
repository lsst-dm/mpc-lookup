"""Handlers for the app's external root, ``/mpc-lookup/``."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from safir.dependencies.logger import logger_dependency
from safir.metadata import get_metadata
from structlog.stdlib import BoundLogger

from ..config import config
from ..models import Index

__all__ = ["get_index", "external_router"]

external_router = APIRouter()
"""FastAPI router for all external handlers."""


@external_router.get(
    "/",
    description=(
        "Document the top-level API here. By default it only returns metadata"
        " about the application."
    ),
    response_model=Index,
    response_model_exclude_none=True,
    summary="Application metadata",
)
async def get_index(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Index:
    """GET ``/mpc-lookup/`` (the app's external root).

    Customize this handler to return whatever the top-level resource of your
    application should return. For example, consider listing key API URLs.
    When doing so, also change or customize the response model in
    `mpclookup.models.Index`.

    By convention, the root of the external API includes a field called
    ``metadata`` that provides the same Safir-generated metadata as the
    internal root endpoint.
    """
    # There is no need to log simple requests since uvicorn will do this
    # automatically, but this is included as an example of how to use the
    # logger for more complex logging.
    logger.info("Request for application metadata")

    metadata = get_metadata(
        package_name="mpc-lookup",
        application_name=config.name,
    )
    return Index(metadata=metadata)


_DESIGNATION_PREPEND = "2011 "


@external_router.get("/search", response_class=RedirectResponse)
async def search(
    designation: Annotated[str, Query()],
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> str:
    """
    Request a redirect to the MPCORB record for a given designation.

    Notes
    -----
    Example request:

    /mpc-lookup/search?designation=2011+1001+T-2

    """
    logger.info("Request for designation URL", designation=designation)
    fd = designation.replace(_DESIGNATION_PREPEND, "")
    redirect_url = (
        "https://www.minorplanetcenter.net/db_search/"
        f"show_object?object_id={fd}"
    )
    logger.info("Redirecting to designation URL", redirect_url=redirect_url)
    return redirect_url
