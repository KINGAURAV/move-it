# Image signing (optional automation)

**Move-It** › **Step 8** › `08_deploy/image-signing/`

<table width="100%" style="width:100%">
<tr>
<td align="left"><a href="../README.md">Back — Step 8 — Deploy</a></td>
<td align="right"><a href="https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/registry/">Manual signing — Container Registry guide</a></td>
</tr>
</table>

Use this guide if you prefer the automated signing flow with [`sign_image.py`](sign_image.py) instead of following the manual steps in the [Container Registry guide](https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/registry/). Vayu ML Services require **signed** container images. Sign **each** image after push — once for ingest, once for dashboard.

---

<details>
<summary><h3>📦 What gets created</h3></summary>

[`sign_image.py`](sign_image.py) downloads tooling and writes signing assets in this folder:

| Path | Purpose |
|------|---------|
| `move-it/tcl-cosign` | `tcl-cosign` binary (repo root, made executable) |
| `08_deploy/image-signing/fulcio.crt` | Sigstore root certificate |
| `08_deploy/image-signing/rekor.key` | Rekor public key |
| `08_deploy/image-signing/ctlog.key` | CT log public key |

These certificate files are gitignored and re-downloaded when you run the script.

</details>

---

<details>
<summary><h3>📋 Prerequisites</h3></summary>

Set registry variables in the root [`.env`](../../README.md) (see [`.env.example`](../../.env.example)). Values are provided in the **Access Guide**:

- `IMAGE_REGISTRY`
- `REGISTRY_PROJECT`
- `REGISTRY_USERNAME`
- `REGISTRY_PASSWORD`
- `VAYU_USERNAME` (verify only)

</details>

---

<details>
<summary><h3>✍️ Sign the images</h3></summary>

Sign the ingest image:

```bash
cd /home/jovyan/move-it
set -a && source .env && set +a

export IMAGE=$IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-ingest:latest

python 08_deploy/image-signing/sign_image.py sign
```

Sign the dashboard image:

```bash
export IMAGE=$IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-dashboard:latest
python 08_deploy/image-signing/sign_image.py sign
```

Follow the browser prompt during signing (copy the authorization code when redirected).

</details>

---

<details>
<summary><h3>🔍 Verify (optional)</h3></summary>

Repeat per image:

```bash
export IMAGE=$IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-ingest:latest
python 08_deploy/image-signing/sign_image.py verify
```

</details>

---

<details>
<summary><h3>🔑 Environment variables</h3></summary>

| Variable | Used for | Source |
|----------|----------|--------|
| `IMAGE_REGISTRY` | build + sign + verify | Root `.env` — registry host from your Vayu user profile |
| `REGISTRY_PROJECT` | build + sign + verify | Root `.env` — registry project name (between host and image repo) |
| `IMAGE` | sign + verify | Export per run: `$IMAGE_REGISTRY/$REGISTRY_PROJECT/move-it-ingest:latest` or `.../move-it-dashboard:latest` |
| `REGISTRY_USERNAME` | sign + verify + `docker login` | Root `.env` — container registry username |
| `REGISTRY_PASSWORD` | sign + verify + `docker login` | Root `.env` — container registry CLI secret |
| `VAYU_USERNAME` | verify only | Root `.env` — your Vayu username (certificate identity) |

</details>

---

<table width="100%" style="width:100%">
<tr>
<td align="left"><a href="../README.md">Back — Step 8 — Deploy</a></td>
<td align="right"><a href="https://ipcloud.tatacommunications.com/docs/docs/user-docs/vayu-ai-studio/registry/">Manual signing — Container Registry guide</a></td>
</tr>
</table>
