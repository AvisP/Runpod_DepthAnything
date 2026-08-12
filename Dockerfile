FROM pytorch/pytorch:2.13.0-cuda13.2-cudnn9-runtime

WORKDIR /app

# Install OS packages required to build some Python packages and venv support
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
	 git build-essential ffmpeg libsndfile1 python3-venv \
 && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to avoid PEP 668 "externally-managed-environment" errors,
# then install Python packages into that venv
RUN python -m venv /opt/venv \
 && /opt/venv/bin/python -m pip install --upgrade pip setuptools wheel \
 && /opt/venv/bin/python -m pip install --prefer-binary runpod depth-anything-3 pillow \
 && /opt/venv/bin/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu132

# Ensure the venv binaries are used by default
ENV PATH=/opt/venv/bin:$PATH

RUN apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy your handler file
COPY handler.py /app
COPY test_input.json /app
COPY models /app/models

# Start the container
CMD ["python", "-u", "handler.py"]