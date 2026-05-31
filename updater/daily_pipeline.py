import subprocess

print("Step 1 : Updating Data")
subprocess.run(["python", "update_data.py"])

print("Step 2 : Training Model")
subprocess.run(["python", "../training/train.py"])

print("Pipeline Complete")