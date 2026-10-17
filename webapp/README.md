# montfortmini webapp

The private video workbench for [montfortmini](https://github.com/bobfromarcher/montfortmini).
See the repository's root README for backend deployment, local setup and model limits.

Node 22.13+ is required. Run `npm install`, copy `.dev.vars.example` to ignored
`.dev.vars`, configure the backend URL/key, and run `npm run dev`.

This uses the Vinext/Sites starter. Preserve its authentication, build integration,
and bundled third-party license notices when hosting on Sites. The local dev
server provides mock sign-in; deployed Sites access is enforced by Sites.