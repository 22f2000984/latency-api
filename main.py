import json
import statistics
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    DATA = json.load(f)


@app.post("/")
async def metrics(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in DATA if r["region"] == region]
        lat = [r["latency_ms"] for r in rows]
        up = [r["uptime"] for r in rows]

        result[region] = {
            "avg_latency": round(statistics.mean(lat), 2),
            "p95_latency": sorted(lat)[int(0.95 * len(lat)) - 1],
            "avg_uptime": round(statistics.mean(up), 4),
            "breaches": sum(1 for x in lat if x > threshold),
        }

    return result