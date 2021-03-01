import os
from pathlib import Path

p = Path("/tmp/secrets")
p.mkdir(parents=True, exist_ok=True)
with open("/tmp/secrets/contrib_jaeger_sampler_rate", "w") as f:
    f.write("0.1")
os.environ["CONTRIB_SECRETS_DIR"] = "/tmp/secrets"
os.environ["CONTRIB_FASTAPI_APP"] = "tests.conftest.app"
