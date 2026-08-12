import base64
import json
import os
import time
import urllib.request
import urllib.error
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

API_KEY = os.getenv("API_KEY") or os.getenv("RUNPOD_API_KEY")
RUNPOD_BASE_URL = os.getenv("RUNPOD_BASE_URL") or "http://localhost:8000"

BASE_DIR = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(BASE_DIR, "StreetView.jpg")
OUT_PATH = os.path.join(BASE_DIR, "test_input.json")

def make_payload(image_path=IMAGE_PATH, out_path=OUT_PATH):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {"input": {"image": b64}}

    with open(out_path, "w", encoding="utf-8") as wf:
        json.dump(payload, wf)

    print(f"Wrote payload to {out_path}")
    return payload


def post_json(url, payload, timeout=300):
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode("utf-8")
        except Exception:
            err = str(e)
        raise RuntimeError(f"HTTPError {e.code}: {err}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"URLError: {e.reason}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e


def get_json(url, timeout=30):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body)


def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as wf:
        json.dump(data, wf, indent=2)
    print(f"Saved JSON to {file_path}")


def run_and_wait(base_url, payload, retries=15, delay=2):
    try:
        status, result = post_json(f"{base_url}/runsync", payload)
        print(f"Runsync status: {status}")
        print(json.dumps(result, indent=2))
        return result
    except RuntimeError as exc:
        print(f"Runsync unavailable, falling back to /run + /status: {exc}")

    status, initial = post_json(f"{base_url}/run", payload)
    print(f"Submission status: {status}")
    # print(json.dumps(initial, indent=2))

    job_id = initial.get("id")
    if not job_id:
        raise RuntimeError("No job id returned")

    for _ in range(retries):
        time.sleep(delay)
        status, result = post_json(f"{base_url}/status/{job_id}", {})
        print(f"Status check: {status}")
        # print(json.dumps(result, indent=2))

        if result.get("status") in {"COMPLETED", "FAILED"}:
            return result

    raise RuntimeError("Timed out waiting for the job to finish")

if __name__ == "__main__":
    payload = make_payload()
    result = run_and_wait(RUNPOD_BASE_URL, payload, delay=10)

    output_json_path = os.path.join(BASE_DIR, "result.json")
    save_json(result, output_json_path)

    depth = result["output"].get("depth")
    if depth is not None:
        plt.imshow(depth[0], cmap="viridis")
        plt.colorbar(label="Depth")
        plt.title("Depth Map")

        output_file = os.path.join(BASE_DIR, "depth_map.png")
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Saved depth map to {output_file}")
        plt.show()
    else:
        print("No depth data found in the result.")
