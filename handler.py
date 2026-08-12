from pathlib import Path
import runpod
from depth_anything_3.api import DepthAnything3
import torch, base64, io
from PIL import Image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_dir = Path(__file__).resolve().parent / "models" / "depth-anythingDA3-GIANT-1.1"
model = DepthAnything3.from_pretrained(model_dir).to(device)


def handler(job):
    job_input = job.get("input", job)
    image_b64 = job_input.get("image")

    if not image_b64:
        return {"error": "No image provided."}

    img_bytes = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    predictions = model.inference([img], export_dir=None, export_format="npz")
    if isinstance(predictions, list) and predictions:
        prediction = predictions[0]
    else:
        prediction = predictions

    depth_map = getattr(prediction["output"], "depth", None)
    if depth_map is None:
        return {"error": "No depth map produced."}

    return {"depth": depth_map.tolist()}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})