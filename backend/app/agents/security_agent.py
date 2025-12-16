import subprocess
import tempfile
import shutil
import os
import json

class SecurityAgent:
    def scan(self, iac_files: dict):
        temp = tempfile.mkdtemp(prefix="checkov-")

        try:
            # Write IaC
            for name, content in iac_files.items():
                with open(os.path.join(temp, name), "w") as f:
                    f.write(content)

            cmd = [
                "checkov", "-d", temp,
                "--quiet",
                "--output", "json"
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True
            )

            return json.loads(result.stdout or "{}")

        finally:
            shutil.rmtree(temp)
