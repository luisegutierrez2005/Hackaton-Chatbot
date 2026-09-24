# CESA Lookup

One narrow OpenClaw tool that calls the local CESA chatbot at `127.0.0.1:8765`. It does not expose shell, files, Nido credentials, or arbitrary URLs. The Python server must already be running on the same machine.

## Build

```bash
npm install
npm run plugin:build
npm run plugin:validate
npm test
```

This is an optional route for using OpenClaw as the Telegram channel. The alternative `../telegram_bridge.py` does not need OpenClaw. For a shared bot, create an isolated agent allowed to call only `cesa_lookup`; do not attach this plugin to an unrestricted personal agent. The user's local install previously handled manual Telegram questions, but cloning this repository does not install or configure the agent or channel. See `../docs/CONFIGURACION_OPENCLAW.md`.

The TypeScript build and Vitest unit test passed locally. The source, not `node_modules` or `dist`, is committed; build it after cloning. The Python service must remain on the same machine as the plugin, bound to localhost.
