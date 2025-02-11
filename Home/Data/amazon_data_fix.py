# AMAZON CLEANING
import json

# Function to remove duplicate entries based on the "Product Name" field
def remove_duplicates(json_data):
    seen_products = set()  # To track unique product names
    unique_data = []

    for entry in json_data:
        product_name = entry.get("Product Name", "").strip()  # Get and clean the product name
        
        # If the product name hasn't been seen before, add it to the set and the unique data list
        if product_name and product_name not in seen_products:  # Check for non-empty product names
            seen_products.add(product_name)
            unique_data.append(entry)
    
    return unique_data

# Function to load JSON data from a file
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return []

# Function to save the unique JSON data back to a file
def save_json(file_path, json_data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4)

# Example usage
input_file = 'amazon_mobiles.json'  # Your input JSON file
output_file = 'amazon_mobiles_2.json'  # File to save the unique data

# Load, remove duplicates, and save the JSON data
json_data = load_json(input_file)
if json_data:  # Proceed only if data is loaded successfully
    unique_json_data = remove_duplicates(json_data)
    save_json(output_file, unique_json_data)
    
    # Print the total number of unique products
    print(f"Duplicate entries removed. Unique data saved to {output_file}.")
    print(f"Total number of unique products: {len(unique_json_data)}")
else:
    print("No data to process.")
