
print("Simulating deployment trigger...")
try:
    import subprocess
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix Cassandra Voice: Free Tier compatibility + Symbol Stripping"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("Deployment triggered successfully via git push.")
except Exception as e:
    print(f"Deployment failed: {e}")
