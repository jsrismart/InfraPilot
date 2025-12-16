import subprocess
import tempfile
import shutil
import os
import json

class PlannerAgent:
    def plan(self, iac_files: dict):
        temp_dir = tempfile.mkdtemp(prefix="tf-plan-")

        try:
            # Write files
            for name, content in iac_files.items():
                with open(os.path.join(temp_dir, name), "w") as f:
                    f.write(content)

            # Run terraform init
            subprocess.run(
                ["terraform", "init", "-input=false"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                check=True
            )

            # Run terraform plan (JSON output)
            plan = subprocess.run(
                ["terraform", "plan", "-input=false", "-json"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                check=True
            )

            return json.loads(plan.stdout)

        except Exception as e:
            return {"error": str(e)}

        finally:
            shutil.rmtree(temp_dir)
