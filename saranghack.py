import openai

openai.api_base = "https://api.pawan.krd/v1"
openai.api_key = "pk-dpqdJpwNUzoOxhxxEhWfrzHqkrwDsWbTLqDyPJHltXpBZXaj"

def generate_response(user_input, history):
    chat_completion = openai.ChatCompletion.create(
        model="pai-001",
        messages=history,
        query=user_input
    )
    response = chat_completion.choices[0].message.content
    return response

def generate_questions(topic_info, num_questions=5):
    response = openai.Completion.create(
        model="pai-001",
        prompt=topic_info,
        max_tokens=num_questions * 10,
        n=num_questions,
        stop="\n"
    )

    questions = []
    for choice in response.choices:
        if 'message' in choice:
            questions.append(choice['message']['content'])
        elif 'text' in choice:
            questions.append(choice['text'])
    return questions

def answer_questions(questions):
    score = 0
    for question in questions:
        print("Question:", question)
        answer = input("Your answer: ").strip().lower()
        if answer:
            score += 1
    return score

def chat():
    history = []
    print("AI teacher: Hello! What topic do you want to learn about today?")
    topic = input("You: ")
    topic_info = "Tell me about " + topic
    history.append({"role": "user", "content": topic_info})
    
    print("AI teacher: Let me tell you about", topic)
    response = generate_response(topic_info, history)
    print("AI teacher:", response)
    
    while True:
        print("AI teacher: Do you have any questions about", topic, "or would you like to take a quiz?")
        user_input = input("You: ")
        
        if "question" in user_input.lower():
            print("AI teacher: Sure! Feel free to ask me any questions.")
            while True:
                user_question = input("You: ")
                if user_question.lower() == "exit":
                    break
                response = generate_response(user_question, history)
                print("AI teacher:", response)
                history.append({"role": "user", "content": user_question})
                history.append({"role": "assistant", "content": response})
        elif "quiz" in user_input.lower():
            print("AI teacher: Let's start the quiz!")
            quiz_questions = generate_questions(topic_info)
            print("Answer the following questions:")
            user_score = answer_questions(quiz_questions)
            print("\nYour final score:", user_score, "/", len(quiz_questions))
            if user_score >= 3:
                print("Congratulations! You passed the topic.")
            else:
                print("Unfortunately, you didn't pass the topic. Let me explain again.")
                response = generate_response(topic_info, history)
                print("AI teacher:", response)
                history.append({"role": "assistant", "content": response})
        elif user_input.lower() in ['exit', 'quit', 'bye']:
            print("AI teacher: Goodbye!")
            break
        else:
            print("AI teacher: I'm sorry, I didn't understand that. Do you have any questions or would you like to take a quiz?")
        history.append({"role": "user", "content": user_input})

if __name__ == "__main__":
    chat()
