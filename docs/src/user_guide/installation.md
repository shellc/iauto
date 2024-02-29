# Installation

Python version requirement: >=3.8

iauto can be installed from PyPI using pip. It is recommended to create a new virtual environment before installation to avoid conflicts.

```bash
pip install -U iauto
```

To access the latest code, install directly from the GitHub repository.

```bash
pip install git+https://github.com/shellc/iauto.git
```

## Enable hardware acceleration for local LLM

If you want to run LLM locally, you can enable hardware acceleration in the following ways.

To enable cuBLAS acceleration on NVIDIA GPU:

```bash
CMAKE_ARGS="-DGGML_CUBLAS=ON" pip install -U iauto
```

To enable Metal on Apple silicon devices:

```bash
CMAKE_ARGS="-DGGML_METAL=ON" pip install -U iauto
```
