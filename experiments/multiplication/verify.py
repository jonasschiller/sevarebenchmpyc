import sys
import subprocess

# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print("Usage: python verify.py <user> <parties>")
    sys.exit(1)

# Get the parameters from the command line arguments
param1 = sys.argv[1]

# Run the bash script
for i in range(0, int(sys.argv[2])):
    script_path = "/root/sevarebenchmpyc/.sh"  # Replace with the actual path to your bash script
subprocess.run(["bash", script_path])



    

