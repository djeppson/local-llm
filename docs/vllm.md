# Summary

In general, working with vLLM was rather frustrating and slow. I liked how it provided a benchmarking tool but it seems like the overall outcomes are:

- I could never get it to really perform well, model choice was confusing and overall it was hugely more complex than my [Ollama setup](./dj7900/ollama-server.md)
- It is oriented toward high-concurrency workloads (which will be very unlikely in home/personal use)
- It is heavily oriented toward NVidia (like most everything else)

# GPU workloads

## First working setup

See: https://docs.vllm.ai/projects/recipes/en/latest/GLM/GLM.html

- Note: the commands provided on the page spun up Qwen/Qwen3-0.6B rather that the expected (because of the source page) GLM

```
docker run -it \
  --rm \
  --ipc=host \
  --network=host \
  --privileged \
  --cap-add=CAP_SYS_ADMIN \
  --device=/dev/kfd \
  --device=/dev/dri \
  --device=/dev/mem \
  --group-add video \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  -v $(pwd):/work \
  -e SHELL=/bin/bash \
  --name foo \
  docker.io/vllm/vllm-openai-rocm:v0.15.1
```

## Baseline benchmark test

```
docker exec -it foo vllm bench serve \
  --dataset-name random \
  --random-input-len 8000 \
  --random-output-len 1000 \
  --num-prompts 16 \
  --ignore-eos
```

## Refined model running platform

- Use the 'latest' version of the container
- Remove privileged (not sure why it would be needed)
- Remove CAP_SYS_ADMIN (not sure why it is needed and it sounds like a lot of permission)
- Add HF token and cache directory
- Add serve 'model' parameter to the serve command for clarity
- Add serve 'max-model-len' parameter as a default to allow command reuse with larger models (e.g., Qwen/Qwen3-8B)

```
docker run -it \
  --rm \
  --ipc=host \
  --network=host \
  --device=/dev/kfd \
  --device=/dev/dri \
  --device=/dev/mem \
  --group-add video \
  --cap-add=SYS_PTRACE \
  -e SHELL=/bin/bash \
  --env "PYTORCH_ALLOC_CONF=expandable_segments:True" \
  --env "HF_TOKEN=${HF_TOKEN:?set HF_TOKEN from ~/.cache/huggingface/token}" \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v ~/.cache/vllm:/root/.cache/vllm \
  --name foo \
  docker.io/vllm/vllm-openai-rocm:latest \
    Qwen/Qwen3.5-0.8B \
    --max-model-len 'auto' \
    --reasoning-parser qwen3 \
    --tool-call-parser qwen3_coder \
    --enable-auto-tool-choice
```

## GPU Benchmarks (Output token throughput)

### 16K/1K input/output length / 16 concurrent (approx 12K words, 4 essays)

- Qwen/Qwen3-0.6B (344.55 tok/s)
- Qwen/Qwen3.5-0.8B (273.51 tok/s)
- Qwen/Qwen3.5-2B (236.42 tok/s)
- Qwen/Qwen3.5-4B (142.63 tok/s)
- unsloth/Seed-Coder-8B-Instruct (109.14 tok/s)
- Qwen/Qwen3-8B-AWQ (95.32 tok/s)
- Qwen/Qwen3-8B (89.43 tok/s)
- deepseek-ai/deepseek-coder-6.7b-instruct (37.84 tok/s)
- Qwen/Qwen3-14B-AWQ (24.01 tok/s)
- Qwen/Qwen3.5-9B (19.18 tok/s)
- Tesslate/OmniCoder-9B (19.03 tok/s)
- Qwen/Qwen3.5-9B (18.66 tok/s)

### 3K/1K input/output length / 16 concurrent (approx 2,250 words, 1 short essay or 3 blog posts)

- Qwen/Qwen3.5-2B (629.60 tok/s)
- Qwen/Qwen2.5-Coder-7B-Instruct (305.33 tok/s)
- Qwen/Qwen3.5-4B (273.12 tok/s)
- QuantTrio/Qwen3.5-9B-AWQ (194.65 tok/s)
- deepseek-ai/deepseek-coder-7b-instruct-v1.5 (118.67 tok/s)
- Qwen/Qwen2.5-Coder-14B-Instruct-AWQ (104.76 tok/s)
- Qwen/Qwen3.5-9B (78.93 tok/s)

### 1K/1K input/output length / 24 concurrent

- Qwen/Qwen3-0.6B (2027.15 tok/s)
- Qwen/Qwen3-14B-AWQ --language-model-only (242.37 tok/s)
- Qwen/Qwen2.5-Coder-14B-Instruct-AWQ (27.22 tok/s)

### 100/100 io length / 240 concurrent

- Qwen/Qwen3-0.6B (2898.50 tok/s)
- Qwen/Qwen3-14B-AWQ (749.47 tok/s)

What is the error:

```
UserWarning: Input tensor shape suggests potential format mismatch: seq_len (16) < num_heads (32). This may indicate the inputs were passed in head-first format [B, H, T, ...] when head_first=False was specified. Please verify your input tensor format matches the expected shape [B, T, H, ...]
```

# CPU workloads

Use case: Small model is good enough to summarize or classify short bits of text

- Batch processing: categorize fin tx descriptions
- Simple questions(?)

```
docker run -it \
  --rm \
  --ipc=host \
  --network=host \
  --device=/dev/mem \
  --cap-add=SYS_NICE \
  --env "HF_TOKEN=${HF_TOKEN:?set HF_TOKEN from ~/.cache/huggingface/token}" \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -e SHELL=/bin/bash \
  --name foo \
  docker.io/vllm/vllm-openai-cpu \
    --max-model-len 'auto' \
    --model Qwen/Qwen3-0.6B
```

## CPU Benchmarks (Output token throughput)

- 8K/1K input/output length / 16 concurrent
  - Qwen/Qwen3-0.6B (26.09 tok/s)
- 8K/1K inpu/outputt length / 2 concurrent
  - Qwen/Qwen3-0.6B (28.59 tok/s)
- 1K/1K input/output length / 24 concurrent
  - Qwen/Qwen3-0.6B (204.69 tok/s)
- 1K/1K input/output length / 12 concurrent
  - Qwen/Qwen3-0.6B (295.08 tok/s)
- 100/100 input/output length / 240 concurrent
  - Qwen/Qwen3-0.6B (474.58 tok/s)

## Home use-case benchmark

Jerraud and Darren running large essay-length summaries or writing/coding prompts consistently for awhile

```
docker exec -it foo vllm bench serve \
  --dataset-name random \
  --random-input-len 1000 \
  --random-output-len 200 \
  --max-concurrency 2 \
  --num-prompts 60 \
  --ignore-eos
```
