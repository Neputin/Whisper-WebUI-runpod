FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 GRADIO_ANALYTICS_ENABLED=False
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY runpod/requirements.txt /app/requirements.txt
RUN python3 -m pip install -r /app/requirements.txt && python3 -m pip check
COPY runpod/ /app/
RUN python3 -m unittest discover -s tests -v && DATA_DIR=/tmp/whisper-build-check python3 -c "import app; assert app.demo is not None"
ENV DATA_DIR=/workspace/whisper-txt
EXPOSE 7860
CMD ["python3", "app.py"]
