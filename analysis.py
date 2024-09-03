import re
from collections import defaultdict
from responses import data, ita_diffusion_correct,ita_denoiser_correct,ita_denoiser_wrong,ita_diffusion_wrong,ita_dtln_correct,ita_dtln_wrong,ger_denoiser_correct,ger_denoiser_wrong,ger_diffusion_correct,ger_diffusion_wrong,ger_dtln_correct,ger_dtln_wrong

# User IDs to exclude
excluded_users = {"meenakshisirigiraju", "hemalshaji77", "chowdamv"}

# Regex patterns to identify file types
patterns = {
    'diffusion': re.compile(r'diffusion', re.IGNORECASE),
    'denoiser': re.compile(r'denoiser', re.IGNORECASE),
    'dtln': re.compile(r'dtln', re.IGNORECASE),
}

# Initialize a counter for all users excluding the ones in excluded_users
total_language_counter = defaultdict(lambda: {'diffusion': 0, 'denoiser': 0, 'dtln': 0})

# Iterate through the responses
for user_id, user_data in data["responses"].items():
    if user_id not in excluded_users:
        for response_key, response_data in user_data["responses"].items():
            language = response_data["language"]
            file_name = response_data["file_name"]

            # Check the file type based on the filename
            for type_name, pattern in patterns.items():
                if pattern.search(file_name):
                    total_language_counter[language][type_name] += 1

# Print aggregated results for all included users
print("Aggregated results for all included users:")
for language, counts in total_language_counter.items():
    print(f"  Language: {language}")
    for type_name, count in counts.items():
        print(f"    {type_name.capitalize()}: {count}")

# Initialize counters for each user
user_match_counts = {}
total_files_with_denoiser = 0

# Process each user in the data
for user_id, user_data in data["responses"].items():
    match_count = 0
    user_files_with_denoiser = 0
    
    # Process each set in the user's responses
    for set_id, response in user_data["responses"].items():
        file_name = response["file_name"]
        
        # Check if the file_name contains 'denoiser'
        if 'diffusion' in file_name:
            user_files_with_denoiser += 1
            
            # Split the file_name by underscores
            parts = file_name.split("_")
            
            # Check if the last part of the split contains '_diffusion'
            if len(parts) > 1 and parts[-1].startswith("diffusion"):
                # Extract SESS_xxxx part and append _BLOCKE
                sess_part = parts[0]
                sess_blocke = sess_part + "_BLOCKE"
                
                # Check if this sess_blocke is found in any entry of the denoiser_correct array
                if any(re.search(sess_blocke, entry) for entry in ger_diffusion_wrong):
                    match_count += 1
    
    # Update the total files with 'denoiser' count
    total_files_with_denoiser += user_files_with_denoiser
    
    # Calculate the percentage of matches for this user
    if user_files_with_denoiser > 0:
        match_percentage = (match_count / user_files_with_denoiser) * 100
    else:
        match_percentage = 0

    user_match_counts[user_id] = {
        "matches": match_count,
        "files_with_denoiser": user_files_with_denoiser,
        "match_percentage": match_percentage
    }

# Calculate cumulative match percentage across all users
total_match_count = sum(user_data["matches"] for user_data in user_match_counts.values())

if total_files_with_denoiser > 0:
    cumulative_match_percentage = (total_match_count / total_files_with_denoiser) * 100
else:
    cumulative_match_percentage = 0

# print("User Match Counts:", user_match_counts)
print("Cumulative Match Percentage:", cumulative_match_percentage)
print(total_match_count)
print(total_files_with_denoiser)
