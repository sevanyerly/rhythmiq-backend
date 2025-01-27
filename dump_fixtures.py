import os
import subprocess


def main():
    # Paths
    app_name = "app_rhythmiq"
    models_dir = os.path.join(app_name, "models")
    fixtures_dir = os.path.join(app_name, "fixtures")

    # Create the fixtures directory if it doesn't exist
    if not os.path.exists(fixtures_dir):
        os.makedirs(fixtures_dir)

    # List the files in the models directory
    model_files = [
        f for f in os.listdir(models_dir) if f.endswith(".py") and f != "__init__.py"
    ]

    # Add auth.User model to the list manually
    model_files.append("user.py")

    # Loop through each model file and generate a fixture
    for model_file in model_files:
        if model_file == "user.py":
            model_name = "User"
            fixture_file = os.path.join(fixtures_dir, "auth_user.json")
        else:
            model_name = "".join(
                word.capitalize()
                for word in os.path.basename(model_file).replace(".py", "").split("_")
            )
            fixture_file = os.path.join(
                fixtures_dir, f"{model_file.replace('.py', '.json')}"
            )

        # Command to dump data for each model
        command = [
            "python",
            "manage.py",
            "dumpdata",
            f"{app_name}.{model_name}" if model_file != "user.py" else "auth.User",
            "--indent",
            "4",
        ]

        # Open the output file to redirect the dump
        with open(fixture_file, "w") as f:
            subprocess.run(command, stdout=f)

        print(f"Dump completed for model: {model_name} -> {fixture_file}")


if __name__ == "__main__":
    main()
