import os

def generate_env_example(input_file=".env", output_file=".env.example"):
    """
    Generates a .env.example file from a .env file by replacing values with placeholders.

    :param input_file: Path to the input .env file.
    :param output_file: Path to the output .env.example file.
    """
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    try:
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            for line in infile:
                # Skip empty lines or comments
                if line.strip() == "" or line.strip().startswith("#"):
                    outfile.write(line)
                    continue

                # Replace the value with a placeholder
                if "=" in line:
                    key, value = line.split("=", 1)
                    outfile.write(f"{key}=<YOUR_{key.strip()}>\n")
                else:
                    outfile.write(line)

        print(f"Generated {output_file} from {input_file}.")
    except Exception as e:
        print(f"Error while generating {output_file}: {e}")

# Run the script
generate_env_example()
