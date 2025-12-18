from dataclasses import dataclass
from typing import Dict


@dataclass
class McpServerRef:
    name: str
    url: str
    kind: str


class McpRegistry:
    def __init__(self) -> None:
        self.servers: Dict[str, McpServerRef] = {}

    def add_server(self, name: str, url: str) -> None:
        if url.startswith("stdio://"):
            kind = "stdio"
        elif (
            url.startswith("sse://")
            or url.startswith("http://")
            or url.startswith("https://")
        ):
            kind = "sse"
        else:
            raise ValueError(f"Unsupported MCP URL: {url}")

        self.servers[name] = McpServerRef(
            name=name,
            url=url,
            kind=kind,
        )

