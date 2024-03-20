import os
import json
import time

import traceback
from typing import Callable, Awaitable, List, Optional

import bittensor as bt
from bittensor.axon import FastAPIThreadedServer
from fastapi import  APIRouter
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

from einstein.protocol import CoreSynapse, ClientRequestSynapse

ForwardFn = Callable[[CoreSynapse], Awaitable[CoreSynapse]]


class ApiServer:

    app: FastAPI
    fast_server: FastAPIThreadedServer
    router: APIRouter
    forward_fn: ForwardFn

    def __init__(
            self, 
            axon_port: int,
            forward_fn: ForwardFn,
    ):
        self.forward_fn = forward_fn
        self.app = FastAPI()

        self.fast_server = FastAPIThreadedServer(config=uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=axon_port,
            log_level="trace" if bt.logging.__trace_on__ else "critical"
        ))
        self.router = APIRouter()
        self.router.add_api_route(
            "/chat",
            self.translate,
            methods=["POST"],
        )
        self.app.include_router(self.router)

    async def translate(self, _request: ClientRequestSynapse):
        chat_msg = f"{_request.question_text}|{_request.question_type}"
        bt.logging.info(f"API: chat_msg {chat_msg}")
        request = CoreSynapse(roles=["user"], messages=[chat_msg])
        response = await self.forward_fn(request)
        bt.logging.info(f"API: response.completion {response.completion}")
        return JSONResponse(status_code=200,
                            content={"detail": "success", "text": response.completion})

    def start(self):
        self.fast_server.start()

    def stop(self):
        self.fast_server.stop()

