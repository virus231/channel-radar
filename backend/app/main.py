from typing import Annotated
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Channel


class ChannelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    title: str | None


def create_app(frontend_dir: Path | None = None):
    application = FastAPI(title="Channel Radar")

    @application.get("/healthz")
    def health():
        return {"status": "ok"}

    @application.get("/api/channels", response_model=list[ChannelResponse])
    def channels(session: Annotated[Session, Depends(get_session)]):
        return session.scalars(select(Channel).order_by(Channel.id)).all()

    frontend_root = (frontend_dir or Path(__file__).parents[2] / "frontend/dist").resolve()
    if frontend_root.is_dir():
        @application.get("/{route:path}", include_in_schema=False)
        def frontend(route: str):
            requested_file = (frontend_root / route).resolve()
            if route == "api" or route.startswith("api/") or not requested_file.is_relative_to(frontend_root):
                raise HTTPException(status_code=404)
            if requested_file.is_file():
                return FileResponse(requested_file)
            if route.startswith("assets/") or Path(route).suffix:
                raise HTTPException(status_code=404)
            return FileResponse(frontend_root / "index.html")

    return application


app = create_app()
