"""WebSocket endpoint for real-time job progress."""

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.redis_pubsub import redis_pubsub

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/jobs/{job_id}")
async def websocket_job_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()
    try:
        pubsub = await redis_pubsub.subscribe(job_id)
    except Exception as exc:
        logger.warning("Redis pub/sub unavailable for WS: %s", exc)
        await websocket.send_json({
            "type": "error",
            "message": "Live updates unavailable (Redis not connected).",
        })
        await websocket.close()
        return

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)
                # Auto-close on completion or error
                if data.get("type") in ("complete", "error"):
                    break
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await pubsub.unsubscribe(f"job:{job_id}")
            await pubsub.close()
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
