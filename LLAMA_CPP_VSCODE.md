To expose a llama.cpp model running on your system to Visual Studio Code, you need to ensure that the llama.cpp server is accessible via an API endpoint. Since you mentioned that the llama.cpp server exposes an OpenAI-compatible API on port 10000, we can proceed with integrating this into VS Code.

Here are the steps:

### Step 1: Ensure the llama.cpp Server is Running
First, make sure your llama.cpp server is running and accessible via `http://localhost:10000`. You should be able to test it using a tool like `curl` or Postman by sending requests to this endpoint.

```bash
curl http://localhost:10000/v1/models
```

### Step 2: Install the VS Code Extension for Language Models
You need an extension in VS Code that can communicate with your llama.cpp server. One such extension is `Language Server Protocol (LSP)` extensions like `CodeLLaMa` or similar.

To install a suitable extension, you can use the following command:

```bash
code --install-extension <extension-id>
```

For example, if there's an extension called `llama-vscode`, you would run:

```bash
code --install-extension llama-vscode
```

### Step 3: Configure VS Code to Use Your llama.cpp Server

Once the extension is installed, configure it to use your local llama.cpp server. This typically involves setting up a configuration file or using settings in VS Code.

#### Example Configuration for `CodeLLaMa` Extension:
If you're using an extension like `CodeLLaMa`, you might need to add something similar to this in your workspace's `.vscode/settings.json`.

```json
{
    "llama.serverUrl": "http://localhost:10000",
    "llama.apiKey": ""
}
```

### Step 7: Verify Integration

After configuring the extension, restart VS Code and verify that it can communicate with your llama.cpp server. You should be able to see prompts or completions provided by the model.

If you encounter any issues during this process, please provide more details so I can assist further.

Would you like me to proceed with installing an appropriate extension and configuring it for you?