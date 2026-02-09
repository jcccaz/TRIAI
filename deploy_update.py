
print("Simulating deployment trigger...")
try:
    import subprocess
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Cassandra Rebrand + Gemini Fix + Voice Integration (Paid Tier)"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Deployment triggered successfully via git push.")
except Exception as e:
    print(f"Deployment failed: {e}")
