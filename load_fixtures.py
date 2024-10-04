import os
import subprocess


def main():
    app_name = 'app_rhythmiq'
    output_folder_name = "fixtures"
    fixtures_dir = os.path.join(app_name, output_folder_name)
    # List the files in the fixtures directory
    fixture_files = [f for f in os.listdir(fixtures_dir) if f.endswith('.json')]

    # Loop through each fixture file and load the data
    for fixture_file in fixture_files:
        # Convert fixture filename to model name (remove .json and capitalize)
        model_name = ''.join(word.capitalize() for word in fixture_file.replace('.json', '').split('_'))

        # Command to load data for each model
        command = [
            'python', 'manage.py', 'loaddata', os.path.join(fixtures_dir, fixture_file),
            '--app', f'{app_name}.{model_name}'
        ]

        # Run the command
        subprocess.run(command)

        print(f"Data loaded for model: {model_name} from {fixture_file}")

if __name__ == "__main__":
    main()