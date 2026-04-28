"""WebSocket endpoint for real-time job progress."""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.redis_pubsub import redis_pubsub

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/jobs/{job_id}")
async def websocket_job_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()
    pubsub = await redis_pubsub.subscribe(job_id)
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
        await pubsub.unsubscribe(f"job:{job_id}")
        await pubsub.close()
        try:
            await websocket.close()
        except Exception:
            pass
