import os
import json
import time
import urllib.parse

import threading

import urllib.parse

import traceback
from typing import Callable, Awaitable, List, Optional

import bittensor as bt
from bittensor.axon import FastAPIThreadedServer
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request
from pydantic import BaseModel
from uvicorn import Config, Server
import asyncio

from einstein.protocol import StreamCoreSynapse, ClientRequestSynapse

ForwardFn = Callable[[CoreSynapse], Awaitable[CoreSynapse]]


class ApiServer:

    app: FastAPI
    # fast_server: FastAPI
    router: APIRouter
    forward_fn: ForwardFn

    def __init__(
        self,
        axon_port: int,
        forward_fn: ForwardFn,
    ):
        self.forward_fn = forward_fn
        self.app = FastAPI()
        self.axon_port = axon_port

        # self.fast_server = FastAPI(config=uvicorn.Config(
        #     self.app,
        #     host="0.0.0.0",
        #     port=axon_port,
        #     log_level="trace" if bt.logging.__trace_on__ else "critical"
        # ))
        self.router = APIRouter()
        self.router.add_api_route(
            "/chat",
            self.translate,
            methods=["POST"],
        )
        self.app.include_router(self.router)
        bt.logging.info("end apiserver init")

    async def translate(self, _request: ClientRequestSynapse):
        bt.logging.info(f"RECEIVE MESSAGE")
        chat_msg = urllib.parse.urlencode(
            {
                "question_text": _request.question_text,
                "question_type": _request.question_type,
                "question_markdown": _request.question_markdown,
            }
        )
        bt.logging.info(f"API: chat_msg {chat_msg}")
        request = StreamCoreSynapse(roles=["user"], messages=[chat_msg])
        response = await self.forward_fn(request)
        bt.logging.info(f"API: response.completion {response.completion}")
        return JSONResponse(
            status_code=200, content={"detail": "success", "text": response.completion}
        )

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.config = Config(
            self.app,
            host="0.0.0.0",
            port=self.axon_port,
            log_level="trace" if bt.logging.__trace_on__ else "critical",
        )
        self.server = Server(self.config)
        self.loop.run_until_complete(self.server.serve())

    def stop(self):
        self.loop.stop()
        self.thread.join()
