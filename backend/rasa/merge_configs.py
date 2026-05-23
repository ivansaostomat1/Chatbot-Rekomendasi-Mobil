import os

def merge_configs():
    # List of files to merge in order
    files_to_merge = [
        "configCP.yml",
        "configTAv1.yml",
        "configTAv2.yml",
        "configTAv3.yml",
        "configTAv4.yml",
        "configTAv5.yml",
        "configTAv6.yml"
    ]
    
    output_file = "merged_configs.txt"
    
    print(f"Starting merge into {output_file}...")
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        for filename in files_to_merge:
            if os.path.exists(filename):
                print(f"Adding {filename}...")
                outfile.write(f"{'='*50}\n")
                outfile.write(f" SECTION: {filename} \n")
                outfile.write(f"{'='*50}\n\n")
                
                with open(filename, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
                
                outfile.write("\n\n")
            else:
                print(f"Warning: {filename} not found, skipping.")
    
    print(f"Successfully created {output_file}")

if __name__ == "__main__":
    merge_configs()
