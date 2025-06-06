import sys


def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) < 2:
        print("Usage: python script.py <arg1> <arg2> ...")
        sys.exit(1)

    # Get the command line arguments
    args = sys.argv[1:]  # Exclude the script name
    print("Command line arguments:", args)

    # Example usage of the arguments
    for arg in args:
        print(f"Processing argument: {arg}")


if __name__ == "__main__":
    main()
