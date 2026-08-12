from huggingface_hub import snapshot_download

local_dir = snapshot_download(
    repo_id="depth-anything/DA3-GIANT-1.1",
    local_dir="./models/dinov2",
    local_dir_use_symlinks=False  # ensures real files, not symlinks
)

print("Saved to:", local_dir)
