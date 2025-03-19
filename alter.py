import json
import os

def process_folder_and_save(input_folder_path, output_folder_name="output"):
    """Processes JSON files in a folder, merges data, and saves to an output folder."""

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)

    # Iterate through files in the input folder
    for filename in os.listdir(input_folder_path):
        if filename.endswith(".json"):
            input_file_path = os.path.join(input_folder_path, filename)
            output_file_path = os.path.join(output_folder_name, filename)

            try:
                with open(input_file_path, 'r') as file:
                    data = json.load(file)

                data_units = data[0]['data_units']
                object_answers = data[0]['object_answers']

                frame_answer_groups = {}

                for unit_key, unit_value in data_units.items():
                    labels = unit_value.get('labels', {})
                    for frame_key, frame_value in labels.items():
                        frame = frame_key
                        objects = frame_value.get('objects', [])

                        for obj in objects:
                            object_hash = obj.get('objectHash')
                            name = obj.get('name')
                            point = obj.get('point', {}).get('0', {})

                            classification_answer = None
                            if object_hash in object_answers:
                                classifications = object_answers[object_hash].get('classifications', [])
                                for classification in classifications:
                                    answers = classification.get('answers')
                                    if isinstance(answers, list) and answers:
                                        classification_answer = answers[-1]
                                    else:
                                        classification_answer = answers

                            group_key = (frame, classification_answer)

                            if group_key not in frame_answer_groups:
                                frame_answer_groups[group_key] = {
                                    "frame": frame,
                                    "answer": classification_answer,
                                    "keypoint": {}
                                }

                            frame_answer_groups[group_key]["keypoint"][name] = {
                                "x": point.get("x"),
                                "y": point.get("y")
                            }

                output = {
                    "name": data[0]["data_title"], #change here
                    "annotation": [
                        {
                            "frame_number": group["frame"],
                            "subject_id": f"person_{group['answer']}",
                            "keypoint": [group["keypoint"]]
                        }
                        for group in frame_answer_groups.values()
                    ]
                }

                json_output = json.dumps(output, indent=4)

                with open(output_file_path, 'w') as outfile:
                    outfile.write(json_output)

                print(f"Processed and saved: {output_file_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Example usage:
input_folder = input("Enter Your File path : ").strip('"').strip("'")
process_folder_and_save(input_folder)
