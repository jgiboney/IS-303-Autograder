'''
IS 303 Autograder

This program evaluates Python file submissions by students. It relies on 
a rubric.json for instructions on how to grade the files. The grading process 
involves reading the Python files, extracting comments, and comparing them 
against the expected comments defined in the JSON file. The program will 
provide feedback on the comments, including the number of comments, the number 
of lines in each comment, and the content of the comments.

Inputs:
- Folder path containing folders with student submissions
- JSON file path for grading instructions

Processes:
- Read the JSON file to get grading instructions.
- For each student folder, read the Python files and extract comments.
- Compare the extracted comments with the expected comments from the JSON file.
- Provide feedback on the comments, including the number of comments, the number 
  of lines in each comment, and the content of the comments.

Outputs:
- Whether the comments matched the expected comments
- Scores based on what is in the JSON file
'''

import json, os, re, subprocess, sys


###### CONSTANTS ######
FOLDER_PATH = 'C:/Users/.../School/2025/Spring/IS 303/Assignment 1 Submissions'
RUBRIC_PATH = 'C:/Users/.../School/2025/Spring/IS 303/Assignment solutions/assignment_1_rubric.json'



###### FUNCTIONS ######s

# This function checks the contents of the file.
def check_file_contents(file_path, rubric, problem_name):
    total_points = 0
    notes = ''
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    content_checks = rubric['Problem specific rubrics'][problem_name]['Content checks']
    for check in content_checks:
        field = check['field']
        regexes = check['regexes']
        points = check['points']
        # Check if any of the regexes match the file content
        found_field = False
        for regex in regexes:
            if re.search(regex, file_content.lower()):
                found_field = True
                break
        
        if found_field:
            total_points += points
        else:
            notes += f"\n    Field '{field}' not found in '{problem_name}'"
    return total_points, notes


# This function grades a single problem based on the rubric and the file path.
def grade_problem(problem_name, file_path, rubric):
    file_name = os.path.basename(file_path)
    print(f"  Grading file: {file_name} for problem: {problem_name}")
    # read the file, use the 'Problem specific rubrics' matching the problem_name from the rubric
    # loop through Content checks which have a field, regexes, and points
    # if at least one regex matches, add the points to the score
    # if the field is not in the file, add a note stating that the field is missing
    total_points = 0
    notes = ''
    points, add_notes = check_file_contents(file_path, rubric, problem_name)
    total_points += points
    notes += add_notes
    # Try to run the file with simulated inputs
    points, add_notes = run_student_file_with_input(file_path, rubric, problem_name)
    total_points += points
    notes += add_notes
    return total_points, notes


# This function grades the submissions of a single student.
def grade_student_submissions(folder_path, dir_name, rubric, scoring_data):
    print(f"Grading folder: {dir_name}")
    # Add the student to the scoring data
    scoring_data['Students'][dir_name] = {'Score': 0, 'Notes': '', 'Problems Solved': {}}
    scoring_data['Students'][dir_name]['Score'] += rubric['Points for submission']
    # Loop through .py files in the student folder
    # Attempt to match the file with the rubric problem_naming dictionary
    for file_name in os.listdir(os.path.join(folder_path, dir_name)):
        if file_name.endswith('.py'):
            problem_name = identify_problem(file_name, rubric)
            # If a problem name is found, grade the file and add the score and the problem solved to the scoring data
            if problem_name:
                if problem_name not in scoring_data['Problems Solved']:
                    scoring_data['Problems Solved'][problem_name] = 0
                scoring_data['Problems Solved'][problem_name] += 1
                score, notes = grade_problem(problem_name, os.path.join(folder_path, dir_name, file_name), rubric)
                scoring_data['Students'][dir_name]['Score'] += score
                scoring_data['Students'][dir_name]['Problems Solved'][problem_name] = score
                scoring_data['Students'][dir_name]['Notes'] += notes
            else:
                print(f"  No problem name found for file: {file_name}")
                continue
    return scoring_data
            


# This function loopps through the folders in the given path and grades the
# submissions based on the rubric in the JSON file.
def grade_submissions(folder_path, rubric_path, scoring_data):
    # Load the rubric from the JSON file
    with open(rubric_path, 'r') as f:
        rubric = json.load(f)
    dirs = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
    for dir_name in dirs:
        scoring_data = grade_student_submissions(folder_path, dir_name, rubric, scoring_data)
    # Print the scoring data
    print("\n\nProblems solved overview:")
    for problem in scoring_data['Problems Solved']:
        print(f"  {problem}: {scoring_data['Problems Solved'][problem]}")
    print("\n\nStudent overview:")
    for student in scoring_data['Students']:
        print(f"{student}: {scoring_data['Students'][student]['Score']} points")
        print(f"  Problems solved: {scoring_data['Students'][student]['Problems Solved']}")
        print(f"  Notes: {scoring_data['Students'][student]['Notes']}\n")
        
    


# This function attempts to identify the problem the student is solving based on the
# file name. The rubric contains a dictionary called problem_naming that contains
# keys for the problem name and a list of possible file names. The function checks if the
# file name matches any of the possible file names in the rubric. If a match is found,
# the function returns the problem name. If no match is found, the function returns None.
def identify_problem(file_name, rubric):
    for problem_name, possible_names in rubric['Problem naming'].items():
        for name in possible_names:
            if name == file_name.lower():
                return problem_name
    return None


# This function attempts to run the student's Python file with simulated inputs.
def run_student_file_with_input(file_path, rubric, problem_name, timeout=15):
    # loop through Simulated inputs from the rubric
    # run the file with the simulated input
    # check the output against the rubric
    total_points = 0
    notes = ''
    for i in range(0,len(rubric['Problem specific rubrics'][problem_name]['Simulated inputs'])):
        simulated_input = rubric['Problem specific rubrics'][problem_name]['Simulated inputs'][i]
        expected_output = rubric['Problem specific rubrics'][problem_name]['Expected outputs'][i]

        try:
            abs_path = os.path.abspath(file_path)

            result = subprocess.run(
                [sys.executable, abs_path],
                input=simulated_input,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Check if there are any errors in the output
            if result.returncode != 0:
                notes += f"\n    Error running file: {file_path}"
            '''if result.returncode != 0:
                return {
                    'status': 'error',
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }'''

            # Check if the output matches the expected output
            #if result.stdout.strip().lower() != expected_output.strip():
            if not re.search(expected_output, result.stdout.lower()):
                notes += f"\n    Output mismatch for input '{i}':  Expected: {expected_output.strip()}  Got: {result.stdout.strip()}"
            else:
                total_points += rubric['Problem specific rubrics'][problem_name]['Points per check']
                '''return {
                    'status': 'mismatch',
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }'''


            '''return {
                'status': 'success',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'notes': f"Expected output: {expected_output.strip()}"
            }'''

        except subprocess.TimeoutExpired as e:
            notes += f"\n    Timeout running file: {file_path}"
            '''return {
                'status': 'timeout',
                'stdout': e.stdout or '',
                'stderr': e.stderr or '',
                'returncode': None
            }'''

        except Exception as e:
            notes += f"\n    Error running file: {file_path}"
            '''return {
                'status': 'error',
                'stdout': '',
                'stderr': str(e),
                'returncode': None
            }'''
    return total_points, notes


# This function asks the user for a folder path and a JSON file path, then 
# grades the submissions in the folder based on the rubric in the JSON file.
def main():
    #folder_path = input("Enter the folder path containing student folders: ")
    #rubric_path = input("Enter the path to the rubric.json file: ")
    folder_path = FOLDER_PATH
    rubric_path = RUBRIC_PATH
    scoring_data = {'Problems Solved':{}, 'Students':{}}
    grade_submissions(folder_path, rubric_path, scoring_data)


if __name__ == '__main__':
    main()