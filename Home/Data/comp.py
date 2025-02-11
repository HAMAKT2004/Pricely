import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load product data from Flipkart, Croma, and Amazon
with open('flipkart_mobiles_2.json', 'r', encoding='utf-8') as file:
    flipkart_data = json.load(file)

with open('croma_mobiles_3.json', 'r', encoding='utf-8') as file:
    croma_data = json.load(file)

with open('amazon_mobiles_2.json', 'r', encoding='utf-8') as file:
    amazon_data = json.load(file)

# Prepare dictionaries to hold product details
flipkart_dict = {product['Product Name']: {
    'Price': product['Price'],
    'Link': product['Product Link'],
    'Image': product['Image Link']} for product in flipkart_data}

croma_dict = {product['Product Name']: {
    'Price': product['Price'],
    'Link': product['Product Link']} for product in croma_data}

amazon_dict = {product['Product Name']: {
    'Price': product['Price'],
    'Link': product['Product Link']} for product in amazon_data}

# Function to calculate cosine similarity scores
def get_best_match(product_name, comparison_dict):
    vectorizer = TfidfVectorizer().fit_transform([product_name] + list(comparison_dict.keys()))
    vectors = vectorizer.toarray()
    cosine_similarities = cosine_similarity(vectors)
    best_match_index = cosine_similarities[0][1:].argmax() + 1  # +1 to skip the first entry (itself)
    best_match_score = cosine_similarities[0][best_match_index]
    best_match_name = list(comparison_dict.keys())[best_match_index - 1]
    return best_match_name, best_match_score

# Store results and accepted count
results = []
accepted_count = 0  # Counter for accepted products

# Compare Amazon products with Flipkart and Croma products
for amazon_name, amazon_info in amazon_dict.items():
    flipkart_best_match_name, flipkart_best_score = get_best_match(amazon_name, flipkart_dict)
    croma_best_match_name, croma_best_score = get_best_match(amazon_name, croma_dict)

    # Check if the product has valid matches in Flipkart and Croma
    has_flipkart_match = flipkart_best_score > 0.40  # Threshold for similarity
    has_croma_match = croma_best_score > 0.40  # Threshold for similarity

    # Ensure that matches are found in both platforms
    if has_flipkart_match and has_croma_match:
        result = {
            'Amazon Product Name': amazon_name,
            'Amazon Price': amazon_info['Price'],
            'Amazon Link': amazon_info['Link'],
            'Amazon vs Flipkart Score': flipkart_best_score,
            'Amazon vs Croma Score': croma_best_score,
            'Flipkart Product Name': flipkart_best_match_name,
            'Flipkart Price': flipkart_dict[flipkart_best_match_name]['Price'],
            'Flipkart Link': flipkart_dict[flipkart_best_match_name]['Link'],
            'Flipkart Image Link': flipkart_dict[flipkart_best_match_name]['Image'],
            'Croma Product Name': croma_best_match_name,
            'Croma Price': croma_dict[croma_best_match_name]['Price'],
            'Croma Link': croma_dict[croma_best_match_name]['Link'],
        }
        
        # Print accepted products
        print(f"Accepted {amazon_name} with matches in Flipkart and Croma.")
        
        # Add the result to the list of results
        results.append(result)
        accepted_count += 1  # Increment the accepted count

# Save results to a JSON file
with open('comparison_results.json', 'w', encoding='utf-8') as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

# Print total accepted mobiles
print("Comparison completed and results saved to comparison_results.json.")
print(f"Total number of mobiles accepted: {accepted_count}")
