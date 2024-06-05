from flask import Flask, request, jsonify, send_from_directory
from transformers import pipeline, set_seed

# Initialize Flask application
app = Flask(__name__)

# Initialize the GPT-2 text-generation pipeline with a specific model
set_seed(42)
generator = pipeline('text-generation', model='gpt2')

# Function to generate responses based on a user prompt
def generate_response(prompt, max_length=50, num_return_sequences=1, temperature=0.7):
    # Generate responses using the GPT-2 model with explicit truncation
    responses = generator(
        prompt,
        max_length=max_length,
        num_return_sequences=num_return_sequences,
        temperature=temperature,
        truncation=True  # Explicitly set truncation to True
    )
    
    # Return the generated response
    return responses[0]["generated_text"].strip()

# Define prakriti assessment questions
questions = [
    {"question": "What type of weather do you prefer?", "options": ["Cold", "Warm", "Neutral"]},
    {"question": "How is your sleep pattern?", "options": ["Light and disrupted", "Heavy and sound", "Balanced"]},
    {"question": "What kind of food do you prefer?", "options": ["Light and dry", "Spicy and oily", "Sweet and moist"]},
    # Add more questions as needed
]

# Define health tips for dominant doshas
health_tips = {
    "Vata": "Stay warm, maintain a regular schedule, and eat warm, nourishing foods.",
    "Pitta": "Stay cool, avoid spicy foods, and practice relaxation techniques.",
    "Kapha": "Stay active, eat light foods, and avoid heavy meals."
}

# Function to determine dominant dosha based on user's answers
def determine_dosha(answers):
    scores = {"Vata": 0, "Pitta": 0, "Kapha": 0}
    
    # Calculate scores based on user's answers
    for answer in answers:
        if answer in ["Cold", "Light and disrupted", "Light and dry"]:
            scores["Vata"] += 1
        elif answer in ["Warm", "Balanced", "Spicy and oily"]:
            scores["Pitta"] += 1
        elif answer in ["Neutral", "Heavy and sound", "Sweet and moist"]:
            scores["Kapha"] += 1
    
    # Determine dominant dosha
    dominant_dosha = max(scores, key=scores.get)
    return dominant_dosha

# Route to serve the HTML file from the root URL
@app.route('/')
def index():
    # Use `send_from_directory` to serve the HTML file from the `statics` folder
    return send_from_directory('statics', 'chatbot.html')

# Route for chatbot interaction
@app.route('/chat', methods=['POST'])
def chat_interaction():
    data = request.json
    
    # Check if prompt is present in the request
    if "prompt" in data:
        user_prompt = data["prompt"]
        
        # Generate response using the generate_response function
        response_text = generate_response(user_prompt)
        
        # Return the response as JSON
        return jsonify({"response": response_text})
    
    # Return an error message if prompt is not present
    return jsonify({"error": "No prompt provided"}), 400

# Route for prakriti assessment
@app.route('/prakriti', methods=['POST'])
def prakriti_assessment():
    data = request.json
    
    # Check if answers are present in the request
    if data and "answers" in data:
        answers = data["answers"]
        dominant_dosha = determine_dosha(answers)
        health_tip = health_tips[dominant_dosha]
        
        # Return the dominant dosha and health tip as JSON
        return jsonify({"dominant_dosha": dominant_dosha, "health_tip": health_tip})
    
    # Return the assessment questions as JSON if answers are not present
    return jsonify({"questions": questions})

# Route to serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    # Serve the favicon.ico file from the `statics` folder
    return send_from_directory('statics', 'favicon.ico')

# Run the Flask application
if __name__ == '__main__':
    app.run(port=5000, debug=True)
