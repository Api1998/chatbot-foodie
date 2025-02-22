import re

def order_dict_to_str(order_dict: dict):
    result = ", ".join([f"{int(value)} {key}" for key, value in order_dict.items()])
    return result


def get_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string

    return ""

if __name__ == "__main__":
    
    # example
    print(get_session_id("projects/chatbot-foodie-vjyp/agent/sessions/1234/contexts/ongoing-order"))
    
    print(order_dict_to_str({"samosa": 2, "pizza": 3}))