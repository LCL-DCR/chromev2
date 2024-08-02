from flask import Flask, render_template, request
import google.generativeai as genai
import requests
import re

MODEL_KEY = # gemini api key
SEARCH_KEY = # google search api key
ENGINE_ID = # engine id code

app = Flask(__name__)

class ChromeV2:
    def __init__(self, model_name, instruct):
        self.model_name = model_name
        genai.configure(api_key=MODEL_KEY)
        self.model = genai.GenerativeModel(model_name, system_instruction=[instruct])
    
    def chat(self, prompt):
        return self.model.generate_content(prompt)
    
    def search(self, query, row):
        db = []
        pages = []
        for i in range(1, row+10, 10):
            pages.append(i)
        for page in pages:
            url = f"https://www.googleapis.com/customsearch/v1?key={SEARCH_KEY}&cx={ENGINE_ID}&q={query}&start={page}"
            data = requests.get(url).json()
            sitems = data.get("items")
            try:
                for i, sitem in enumerate(sitems, 1):
                    title = sitem.get("title")
                    description = sitem.get("snippet")
                    link = sitem.get("link")
                    db.append([title, description, link])
            except:
                pass
        return db

def find_bracket_contents(s):
    pattern = r'\[.*?\]'
    reshaped = re.findall(pattern, s)
    return reshaped

def reorder_list(original_list, new_indices):
    return [original_list[i] for i in new_indices]

def string_to_list(string):
    string = string.strip('[] ')
    return list(map(int, string.split(',')))

instruct = "Index Google search results according to given user settings. (given: 'index. [title], [description]\n, ...' answer briefly and follow only the following form: [origin index number, ...]. zero index is high importance)"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        settings = request.form.get('settings')
        query = request.form.get('query')
        
        chromev2 = ChromeV2('gemini-1.5-flash', instruct + "\nUser Settings: " + settings)
        db = chromev2.search(query, 1)
        prompt = ""
        for i in range(len(db)):
            prompt += f"{i}. [{str(db[i][0])}], [{str(db[i][1])}]\n"
        answer = chromev2.chat(prompt)
        t = answer.text
        x = find_bracket_contents(t)
        y = string_to_list(str(x[0]))
        z = reorder_list(db, y)
        
        return render_template('results.html', results=z, query=query)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)