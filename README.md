# reputable\_bot

![build](https://gitea.bogan.io/jukebox/reputable_bot/actions/workflows/build.yaml?branch=main)

Reputable Bot is a Discord bot built with [Pycord](https://pycord.dev/).

## Usage

You can run Repbot directly in your terminal with the following commands:

```sh
pip install -e . && python -m reputable_bot
```

Or you can use a container:

```sh
docker build . -t repbot:local
docker run repbot:local
```

## Configuration

Repbot is configured using environment variables, to facilitate ease of configuration when
containerised.

| Variable | Description | Default |
|----------|-------------|---------|
| (string) (required) `REPBOT_DISCORD_API_TOKEN` | A Discord API token that allows authentication with Discord. | |
| (string) `REPBOT_OLLAMA_URL` | The URL of an Ollama server, used to generate responses. | `http://localhost:11343` |
| (string) `REPBOT_DEFAULT_MODEL` | The default model tag to use with Ollama. | `llama3.1:latest` |
| (string) `REPBOT_DEFAULT_CHANNEL_ID` | The ID of a channel in Discord that Repbot announces its presence in and focuses its attention on to start. | Randomly chosen from available text channels. |
| (string) `REPBOT_LOG_LEVEL` | Sets the log level. `info`, `debug`, and `error` are the possible options. | `info` |


