import os
import subprocess
import json


def get_model_order():
    return [
        "auth_user.json",  # User
        "user_profile.json",  # User profile
        "genre.json",  # Genre
        "song.json",  # Song
        "downloaded_song.json",  # Downloaded song
        "like.json",  # Like
        "playlist.json",  # Playlist
    ]


def load_fixture(fixture_file, fixtures_dir):
    fixture_path = os.path.join(fixtures_dir, fixture_file)

    # Check if the fixture file contains valid data
    with open(fixture_path, "r") as f:
        try:
            data = json.load(f)
            if not data:  # Empty list or invalid data
                print(f"Skipping file with no data: {fixture_file}")
                return False
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON file: {fixture_file}")
            return False

    # Command to load the fixture data
    command = ["python", "manage.py", "loaddata", fixture_path]
    subprocess.run(command)

    print(f"Data loaded from {fixture_file}")
    return True


def main():
    app_name = "app_rhythmiq"
    output_folder_name = "fixtures"
    fixtures_dir = os.path.join(app_name, output_folder_name)

    if not os.path.exists(fixtures_dir):
        print(f"Fixtures directory {fixtures_dir} not found!")
        return

    # Get the files in the defined loading order
    model_order = get_model_order()

    # Load the fixtures in the specified order
    for fixture_file in model_order:
        load_fixture(fixture_file, fixtures_dir)


if __name__ == "__main__":
    main()
